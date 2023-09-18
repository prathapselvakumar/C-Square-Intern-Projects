"""Page routes for local signup, login, and logout."""

from flask import redirect, render_template, request, session, url_for

import config
from core import app
from user_database import UserDatabase

user_db = UserDatabase()


@app.route("/")
def app_root():
    """Send visitors to the signup page."""
    return redirect(url_for("signup"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Show the signup form, or create the account on submit."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if user_db.find_user(username):
            return "Username already exists. Please choose another."
        user_db.insert_user(username, password)
        return "Signup successful! You can now log in."
    return render_template("user/signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Show the login form, or check the credentials and open the chat page."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if user_db.verify_password(username, password):
            session["username"] = username
            return redirect(url_for("chat"))
        return "Invalid credentials. Please try again."
    return render_template("user/login.html")


@app.route("/logout")
def app_logout():
    """Clear the local session and log the user out of SSO as well."""
    session.clear()
    return_url = url_for("app_root")
    return redirect(f"{config.CSQ_SSO_BASE_URL}/csquare/logout?redirect_url={return_url}")
