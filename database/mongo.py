import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "recoverai")

class MongoDB:
    _client = None
    _db = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            try:
                cls._client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
                # Verify connection
                cls._client.admin.command('ping')
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                # We won't raise the error here to allow the app to fail gracefully later
        return cls._client

    @classmethod
    def get_db(cls):
        client = cls.get_client()
        if client is not None:
            return client[MONGODB_DB_NAME]
        return None
