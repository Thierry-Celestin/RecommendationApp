from pymongo import MongoClient
from bson import ObjectId  
import json  
import redis  

# MongoDB connection setup
username = "followalong"
password = "Password123"
cluster_url = "cluster0.3kvom.mongodb.net"

MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster_url}/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

db = client['bookstore']
books_collection = db['books']

# Redis connection setup
cache = redis.Redis(
        host='redis-14334.c80.us-east-1-2.ec2.redns.redis-cloud.com',
        port=14334,
        username="default",
        password="8tETvd68PYW7ItXWRWhwLBo30SrW8XIY",  
        decode_responses=True
    )

# Function to add a new book
def add_book(title, author, genre, reviews=[]):
    book_id = str(ObjectId())  # Generate a unique string ID
    book = {
        "_id": book_id,
        "title": title,
        "author": author,
        "genre": genre,
        "reviews": reviews
    }
    books_collection.insert_one(book)
    # Cache the book data
    cache.set(f"book:{book_id}", json.dumps(book))
    return book_id


# Function to retrieve books by genre
def get_books_by_genre(genre):
    if genre:
        return list(books_collection.find({"genre": genre}))
    return list(books_collection.find())


# Function to retrieve a book by its ID
def get_book_by_id(book_id):
    try:
        # First, check the Redis cache
        cached_book = cache.get(f"book:{book_id}")
        if cached_book:
            return json.loads(cached_book)

        # If not found in cache, query MongoDB
        book = books_collection.find_one({"_id": ObjectId(book_id)})
        if book:
            # Cache the book for future use
            cache.set(f"book:{book_id}", json.dumps(book))
        return book
    except Exception as e:
        print(f"Error retrieving book: {e}")
        return None


# Adding 30 books across different genres
books_to_add = [
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction"),
    ("1984", "George Orwell", "Fiction"),
    ("Pride and Prejudice", "Jane Austen", "Romance"),
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy"),
    ("Dune", "Frank Herbert", "Science Fiction"),
    ("The Catcher in the Rye", "J.D. Salinger", "Fiction"),
    ("Brave New World", "Aldous Huxley", "Science Fiction"),
    ("The Diary of a Young Girl", "Anne Frank", "Biography"),
    ("Sapiens: A Brief History of Humankind", "Yuval Noah Harari", "Non-Fiction"),
    ("Becoming", "Michelle Obama", "Biography"),
    ("The Silent Patient", "Alex Michaelides", "Mystery"),
    ("The Girl on the Train", "Paula Hawkins", "Mystery"),
    ("To Kill a Mockingbird", "Harper Lee", "Fiction"),
    ("The Da Vinci Code", "Dan Brown", "Mystery"),
    ("The Night Circus", "Erin Morgenstern", "Fantasy"),
    ("The Fault in Our Stars", "John Green", "Romance"),
    ("The Book Thief", "Markus Zusak", "Historical"),
    ("The Alchemist", "Paulo Coelho", "Fiction"),
    ("Educated", "Tara Westover", "Non-Fiction"),
    ("The Immortalists", "Chloe Benjamin", "Fiction"),
    ("A Brief History of Time", "Stephen Hawking", "Non-Fiction"),
    ("Murder on the Orient Express", "Agatha Christie", "Mystery"),
    ("The Shining", "Stephen King", "Horror"),
    ("The Road", "Cormac McCarthy", "Historical"),
    ("The Lord of the Rings", "J.R.R. Tolkien", "Fantasy"),
    ("A Song of Ice and Fire", "George R.R. Martin", "Fantasy"),
    ("The Help", "Kathryn Stockett", "Historical"),
    ("The Picture of Dorian Gray", "Oscar Wilde", "Fiction"),
    ("Fahrenheit 451", "Ray Bradbury", "Science Fiction"),
    ("The Art of War", "Sun Tzu", "Non-Fiction")
]

# Insert the books into the MongoDB collection
for title, author, genre in books_to_add:
    add_book(title, author, genre)

print("Books have been added to MongoDB!")