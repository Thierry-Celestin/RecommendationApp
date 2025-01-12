from neo4j import GraphDatabase

NEO4J_URI="neo4j+s://808ff9fb.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="pqU2r5MX1hNiHUBDM7_MNdu_zJX3P6Miu2rMMn96jqs"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def add_user_relationship(user1_id, user2_id):
    with driver.session() as session:
        session.run(
            "MERGE (u1:User {id: $user1_id}) "
            "MERGE (u2:User {id: $user2_id}) "
            "MERGE (u1)-[:FRIEND]->(u2)",
            user1_id=user1_id, user2_id=user2_id
        )

def recommend_books_based_on_friends(user_id):
    with driver.session() as session:
        result = session.run(
            "MATCH (u:User {id: $user_id})-[:FRIEND]->(f)-[:LIKES]->(b:Book) "
            "RETURN b.title AS title, b.genre AS genre, b.author AS author",
            user_id=user_id
        )
        return [{"title": record["title"], "genre": record["genre"], "author": record["author"]} for record in result]