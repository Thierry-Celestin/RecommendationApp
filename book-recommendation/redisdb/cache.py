import redis

try:
    # Replace with your actual Redis host, port, and password
   cache = redis.Redis(
        host='redis-14334.c80.us-east-1-2.ec2.redns.redis-cloud.com',
        port=14334,
        username="default",
        password="8tETvd68PYW7ItXWRWhwLBo30SrW8XIY",  
        decode_responses=True
    )

    # Test connection
   cache.ping()
   print("Successfully connected to Redis!")

    # Example: Set and get a value
   cache.set('foo', 'bar')
   print("Value retrieved from Redis:", cache.get('foo'))

except Exception as e:
    print(f"Failed to connect to Redis: {e}")


def cache_book(book_id, book_data):
    cache.set(f"book:{book_id}", book_data)

def get_cached_book(book_id):
   book_data = cache.get(f"book:{book_id}")
   return book_data if book_data else None

def cache_user_preferences(user_id, preferences):
    cache.set(f"user:{user_id}:preferences", preferences)

def get_cached_preferences(user_id):
    return cache.get(f"user:{user_id}:preferences")

