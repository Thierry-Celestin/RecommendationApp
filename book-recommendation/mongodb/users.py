from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId  
from neo4j import GraphDatabase  
import bcrypt  

# MongoDB connection setup
username = "followalong"
password = "Password123"
cluster_url = "cluster0.3kvom.mongodb.net"

MONGO_URI = f"mongodb+srv://{username}:{password}@{cluster_url}/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)

db = client['bookstore']
users_collection = db['users']

# Ensure the email field is unique
users_collection.create_index("email", unique=True)

# Neo4j connection setup
NEO4J_URI = "neo4j+s://808ff9fb.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "pqU2r5MX1hNiHUBDM7_MNdu_zJX3P6Miu2rMMn96jqs"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


# Function to add a user
def add_user(name, email, password, favorite_genres=[]):
    user_id = str(ObjectId())  
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  

    user = {
        "_id": user_id,
        "name": name,
        "email": email,
        "password": hashed_password.decode('utf-8'), 
        "favorite_genres": favorite_genres
    }

    try:
        # Add user to MongoDB
        users_collection.insert_one(user)

        # Add user to Neo4j
        with driver.session() as session:
            session.run(
                "MERGE (u:User {id: $id, name: $name, email: $email})",
                id=user_id, name=name, email=email
            )
        return user_id

    except DuplicateKeyError:
        print(f"Error: A user with the email {email} already exists.")
        return None


# Function to get a user by email
def get_user_by_email(email):
    try:
        user = users_collection.find_one({"email": email})
        return user
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None


# Function to verify password during login
def verify_password(email, password):
    try:
        user = get_user_by_email(email)
        if user:
            return bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8'))
        return False
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False
