from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from db import Database
import pymongo

app = Flask(__name__)

# MongoDB Configuration
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = mongo_client["AUTHENTICATION"]
collection = db["IDS"]

# Database Configuration
db = Database()

@app.route('/')
def app_root():
    return redirect(url_for('signup'))

@app.route('/logout')
def app_logout():
    session.clear()
    _url = url_for('app_root')
    return redirect(f"{config.CSQ_SSO_BASE_URL}/csquare/logout?redirect_url={_url}")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.find_user(username):
            return "Username already exists. Please choose another."
        else:
            db.insert_user(username, password)
        return "Signup successful! You can now log in."
    return render_template('user/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.verify_password(username, password):
            session['username'] = username
            return redirect(url_for('chat'))
        return "Invalid credentials. Please try again."
    return render_template('user/login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('app_root'))

@app.route('/assets/<p1>/<f1>', methods=['GET'])
def asset_share(p1, f1):
    print(p1, f1)
    return send_from_directory(f"assets/{p1}", f"{f1}")

# Additional asset routes...

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
