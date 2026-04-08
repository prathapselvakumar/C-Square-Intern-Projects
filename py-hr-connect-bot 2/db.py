
import pymongo
from pymongo import MongoClient
from bson import ObjectId
from passlib.hash import bcrypt

class Database:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')  # Update the MongoDB URI as needed
        self.db = self.client['AUTHENTICATION']  
        self.users = self.db['IDS']

    def insert_user(self, username, password):
        hashed_password = bcrypt.hash(password)
        user_data = {
            'username': username,
            'password': hashed_password
        }
        return self.users.insert_one(user_data)

    def find_user(self, username):
        return self.users.find_one({'username': username})

    def verify_password(self, username, password):
        user = self.find_user(username)
        if user and bcrypt.verify(password, user['password']):
            return True
        return False
