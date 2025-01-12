# Book Recommendation System

## Overview
This project demonstrates the integration of MongoDB (Document Database), Neo4j (Graph Database), and Redis (Key-Value Database) to build a book recommendation system.

## Features
- Store user and book data (MongoDB).
- Manage user relationships and recommend books (Neo4j).
- Cache frequently accessed books (Redis).

## How to Run
1. Set up MongoDB, Neo4j, and Redis.
2. Install dependencies: `pip install -r requirements.txt`.
3. Replace the placeholder credentials in `mongodb/` and `neo4j/`.
4. Run the application:
   ```bash
   python app.py
