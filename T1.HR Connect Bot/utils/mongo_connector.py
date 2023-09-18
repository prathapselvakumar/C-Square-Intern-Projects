"""Thin wrapper around a pooled MongoDB client."""

from pymongo import MongoClient


class MongoConnector:
    """Holds one MongoDB client and a handle to a single database."""

    def __init__(self, connection_string, database_name, pool_size=5):
        self.client = MongoClient(connection_string, maxPoolSize=pool_size)
        self.db = self.client[database_name]

    def find(self, collection_name, query):
        """Return every document in `collection_name` that matches `query`."""
        return list(self.db[collection_name].find(query))
