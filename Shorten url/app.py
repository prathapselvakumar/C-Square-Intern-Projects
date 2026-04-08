from flask import Flask, request, render_template, jsonify, redirect, abort
from pymongo import MongoClient
import datetime
import string
import random

app = Flask(__name__)

# Initialize MongoDB connection
client = MongoClient('mongodb://localhost:27017')
db = client['url']
urls_collection = db['urls']

# Function to generate a unique short URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choice(characters) for _ in range(6))
        # Check if the short URL already exists in the database
        if not urls_collection.find_one({'short_url': short_url}):
            return short_url

# Function to format datetime
def format_datetime(dt):
    return dt.strftime("%d/%m/%y %H:%M:%S.%f")

# Function to check if a long URL already exists in the database
def is_long_url_in_database(long_url):
    return urls_collection.find_one({'long_url': long_url}) is not None

@app.route('/')
def index():
    # Fetch URLs from the database
    urls = list(urls_collection.find())
    urls = [{'long_url': url['long_url'], 'short_url': url['short_url'], 'time': format_datetime(url['time'])} for url in urls]

    return render_template('index.html', urls=urls)

# Route to handle URL shortening and saving to MongoDB
@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    long_url = request.form['longUrl']

    # Check if the long URL already exists in the database
    if is_long_url_in_database(long_url):
        existing_entry = urls_collection.find_one({'long_url': long_url})
        short_url = existing_entry['short_url']
    else:
        short_url = generate_short_url()
        complete_short_url = request.url_root + short_url

        # Save to MongoDB
        urls_collection.insert_one({'short_url':request.url_root + short_url    , 'long_url': long_url, 'time': datetime.datetime.now()})

    return jsonify({'short_url': short_url})

# Route to handle redirection based on short URL
@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    # Retrieve the long URL associated with the short URL
    url_entry = urls_collection.find_one({'short_url':request.url_root + short_url})

    if url_entry:
        long_url = url_entry['long_url']
        print(f"Redirecting from {short_url} to {long_url}")
        return redirect(long_url, code=302) # Temp redirection 
    else:
        print(f"Short URL not found: {short_url}")
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
