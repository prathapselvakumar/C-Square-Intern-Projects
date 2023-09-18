"""Storage for local user accounts used by the signup and login pages."""

from passlib.hash import bcrypt
from pymongo import MongoClient

import config


class UserDatabase:
    """Creates and verifies users stored in MongoDB with bcrypt-hashed passwords."""

    def __init__(self):
        self.client = MongoClient(config.AUTH_MONGO_HOST)
        self.db = self.client[config.AUTH_MONGO_DB]
        self.users = self.db[config.AUTH_MONGO_COLLECTION]

    def insert_user(self, username, password):
        """Store a new user with a bcrypt hash of their password."""
        user_data = {
            "username": username,
            "password": bcrypt.hash(password),
        }
        return self.users.insert_one(user_data)

    def find_user(self, username):
        """Return the user document for `username`, or None."""
        return self.users.find_one({"username": username})

    def verify_password(self, username, password):
        """Return True when the user exists and the password matches."""
        user = self.find_user(username)
        return bool(user and bcrypt.verify(password, user["password"]))
