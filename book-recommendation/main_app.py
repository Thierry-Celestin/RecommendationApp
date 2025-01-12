import streamlit as st
import pandas as pd
from mongodb.books import get_books_by_genre, books_collection
from mongodb.users import get_user_by_email, users_collection
from neo4jdb.recommendations import add_user_relationship, recommend_books_based_on_friends
from redisdb.cache import get_cached_book, cache_book  
from bson import ObjectId
import json  

def main_app():
    # Sidebar for actions
    with st.sidebar:
        st.header("User Actions")
        action = st.radio(
            "Choose an action",
            ["Browse Books", "Get Recommendations", "Rate Books", "Manage Friends", "Logout"]
        )

    # Helper: Recommend books based on genres and ratings
    def recommend_books_based_on_genres_and_ratings(user_id):
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return []

        favorite_genres = user.get("favorite_genres", [])
        if not favorite_genres:
            return []

        # Find books in user's favorite genres, sorted by average rating
        recommended_books = books_collection.aggregate([ 
            {"$match": {"genre": {"$in": favorite_genres}}}, 
            {"$unwind": {"path": "$ratings", "preserveNullAndEmptyArrays": True}},  
            {"$group": {
                "_id": "$_id",
                "title": {"$first": "$title"},
                "author": {"$first": "$author"},
                "genre": {"$first": "$genre"},
                "avg_rating": {"$avg": {"$ifNull": ["$ratings.rating", 0]}}
            }},
            {"$sort": {"avg_rating": -1}},
            {"$limit": 10}  
        ])
        return list(recommended_books)

    # Action: Browse Books
    if action == "Browse Books":
        st.header("Browse Books")
        genre = st.selectbox("Filter by Genre", ["All", "Fiction", "Non-Fiction", "Mystery", "Science Fiction", "Romance", "Fantasy", "Historical", "Biography"])
        books = get_books_by_genre(genre) if genre != "All" else list(books_collection.find())

        if books:
            df = pd.DataFrame(books)
            df["_id"] = df["_id"].astype(str)  
            st.dataframe(df[["title", "author", "genre"]])
        else:
            st.info("No books found.")

    # Action: Get Recommendations
    elif action == "Get Recommendations":
        st.header("Get Recommendations")
        user_email = st.text_input("Enter Your Email")
        if st.button("Get Recommendations"):
            user = get_user_by_email(user_email)
            if user:
                # Recommendations based on friends and genres/ratings
                recommendations = recommend_books_based_on_friends(str(user["_id"])) or []
                recommendations += recommend_books_based_on_genres_and_ratings(str(user["_id"]))

                if recommendations:
                    st.write("Recommended Books:")
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec['title']} by {rec['author']} (Genre: {rec['genre']}) - Avg Rating: {rec.get('avg_rating', 'N/A'):.2f}")
                else:
                    st.info("No recommendations found.")
            else:
                st.warning("User not found. Please register first.")

    # Action: Rate Books
    elif action == "Rate Books":
        st.header("Rate Books")
        user_email = st.text_input("Enter Your Email")
        books = list(books_collection.find())  # Fetch all books
        if books:
            book_titles = [book["title"] for book in books]
            selected_book = st.selectbox("Select a Book", book_titles)
            rating = st.slider("Rate the Book", 1, 5, 3)

            if st.button("Submit Rating"):
                user = get_user_by_email(user_email)
                if user:
                    # Retrieve the selected book from Redis cache first
                    cached_book = get_cached_book(selected_book)
                    if cached_book:
                        book = json.loads(cached_book)  # Convert cached data back to dictionary
                    else:
                        # If the book is not in cache, retrieve from MongoDB
                        book = books_collection.find_one({"title": selected_book})
                        if book:
                            # Cache the book data in Redis
                            cache_book(str(book["_id"]), json.dumps(book))
                    if book:
                        # Add rating to the book
                        books_collection.update_one(
                            {"_id": ObjectId(book["_id"])},
                            {"$push": {"ratings": {"user_id": ObjectId(user["_id"]), "rating": rating}}}
                        )
                        st.success("Rating submitted successfully!")
                    else:
                        st.warning("Book not found.")
                else:
                    st.warning("User not found. Please register first.")
        else:
            st.info("No books available to rate.")

    # Action: Manage Friends
    elif action == "Manage Friends":
        st.header("Manage Friends")
        user_email = st.text_input("Your Email")
        friend_email = st.text_input("Friend's Email")

        if st.button("Add Friend"):
            user = get_user_by_email(user_email)
            friend = get_user_by_email(friend_email)
            if user and friend:
                add_user_relationship(str(user["_id"]), str(friend["_id"]))
                st.success(f"Friendship added between {user['name']} and {friend['name']}!")
            else:
                st.warning("One or both users not found.")

    # Action: Logout
    elif action == "Logout":
        st.session_state["user_id"] = None
        st.session_state["user_email"] = None
        st.info("You have been logged out.")
        st.rerun()
