import string
import random
from datetime import datetime

class URLShortener:
    def __init__(self, base_url):
        self.base_url = base_url
        self.short_url_length = 8  # Length of the short URL

    def generate_random_string(self, length):
        # Generate a random string of specified length
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def shorten_url(self, long_url):
        # Generate a random string for the short URL
        random_string = self.generate_random_string(self.short_url_length)

        # Create the short URL by appending the random string to the base URL
        short_url = self.base_url + random_string

        # Assuming you have a MongoDB collection named 'collection' set up
        # Save the URL data in MongoDB
        url_data = {
            "long_url": long_url,
            "short_url": short_url,
            "created_at": datetime.now()
        }
        # Insert data into MongoDB collection here
        # collection.insert_one(url_data)

        return short_url
