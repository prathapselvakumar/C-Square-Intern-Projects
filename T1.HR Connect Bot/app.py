"""Entry point for the HR Connect Bot.

Importing the route modules registers their URLs on the shared Flask app
defined in core.py. Run this file directly for local development.
"""

from flask import send_from_directory

from core import app
import models.chat  # noqa: F401  chat API: /chat/send-message, /chat/clear-history
import views.auth  # noqa: F401  pages: /, /signup, /login, /logout
import views.chat  # noqa: F401  page: /chat


@app.route("/assets/<folder>/<filename>", methods=["GET"])
def serve_asset(folder, filename):
    """Serve static files from the assets folder used by the page templates."""
    return send_from_directory(f"assets/{folder}", filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
