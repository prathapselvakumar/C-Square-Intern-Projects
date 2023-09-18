"""Page routes for the chat interface."""

from flask import render_template

from core import app, session_required


@app.route("/chat")
@session_required
def chat(user):
    """Render the chat page for the logged-in user."""
    return render_template("chat/chat-main.html")
