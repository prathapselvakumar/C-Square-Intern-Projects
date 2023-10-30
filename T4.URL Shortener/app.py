"""A small Flask URL shortener backed by MongoDB.

Each long URL is mapped to a random six-character code. Visiting
<host>/<code> redirects to the original address.
"""

import datetime
import os
import random
import string

from flask import Flask, abort, jsonify, redirect, render_template, request
from pymongo import MongoClient

SHORT_CODE_LENGTH = 6
SHORT_CODE_CHARACTERS = string.ascii_letters + string.digits

app = Flask(__name__)

# Each document stores the full short URL, the original URL, and when it was created.
mongo_client = MongoClient(os.getenv("MONGO_HOST", "mongodb://localhost:27017"))
url_collection = mongo_client["url"]["urls"]


def generate_short_code():
    """Return a random code that is not yet used by any stored short URL."""
    while True:
        short_code = "".join(random.choice(SHORT_CODE_CHARACTERS) for _ in range(SHORT_CODE_LENGTH))
        if not url_collection.find_one({"short_url": request.url_root + short_code}):
            return short_code


def format_datetime(value):
    """Format a timestamp for the history table, e.g. 31/12/23 18:05:42.123456."""
    return value.strftime("%d/%m/%y %H:%M:%S.%f")


def find_by_long_url(long_url):
    """Return the stored entry for `long_url`, or None if it has not been shortened."""
    return url_collection.find_one({"long_url": long_url})


@app.route("/")
def index():
    """Show the shortening form and every URL shortened so far."""
    urls = [
        {
            "long_url": entry["long_url"],
            "short_url": entry["short_url"],
            "time": format_datetime(entry["time"]),
        }
        for entry in url_collection.find()
    ]
    return render_template("index.html", urls=urls)


@app.route("/shorten_url", methods=["POST"])
def shorten_url():
    """Return the short URL for the submitted long URL, creating one if needed."""
    long_url = request.form["longUrl"]

    # Reuse the existing short URL so the same address is never stored twice.
    existing_entry = find_by_long_url(long_url)
    if existing_entry:
        return jsonify({"short_url": existing_entry["short_url"]})

    short_url = request.url_root + generate_short_code()
    url_collection.insert_one({
        "short_url": short_url,
        "long_url": long_url,
        "time": datetime.datetime.now(),
    })
    return jsonify({"short_url": short_url})


@app.route("/<short_code>")
def redirect_to_long_url(short_code):
    """Redirect a short URL to its original address, or return 404."""
    entry = url_collection.find_one({"short_url": request.url_root + short_code})
    if not entry:
        print(f"Short URL not found: {short_code}")
        abort(404)

    print(f"Redirecting from {short_code} to {entry['long_url']}")
    return redirect(entry["long_url"], code=302)


if __name__ == "__main__":
    app.run(debug=True)
