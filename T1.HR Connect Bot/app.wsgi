# mod_wsgi entry point for deploying the HR Connect Bot behind Apache.
# Set FLASK_SECRET_KEY, OPENAI_API_KEY, and MONGO_HOST in the server environment.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application  # noqa: E402
