"""Application settings for the HR Connect Bot.

Every value that is a secret or depends on the deployment is read from an
environment variable, so credentials never have to live in source control.
"""

import os

# Single sign-on (SSO) service that issues and validates employee sessions.
CSQ_SSO_BASE_URL = os.getenv("CSQ_SSO_BASE_URL", "https://employee-login.liveconnect.in")

# Public URL of this application and the page users land on after login.
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://askhr.csquare.in")
APP_HOME_URL = "/chat"

# Key used by Flask to sign session cookies.
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me")

# OpenAI key used by LlamaIndex to embed documents and answer questions.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# MongoDB that stores chat sessions and their message history.
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "csquare_chat_bot")
MONGO_CONN_POOL_SIZE = int(os.getenv("MONGO_CONN_POOL_SIZE", "200"))

# MongoDB that stores local user accounts for the signup and login pages.
AUTH_MONGO_HOST = os.getenv("AUTH_MONGO_HOST", "mongodb://localhost:27017/")
AUTH_MONGO_DB = "AUTHENTICATION"
AUTH_MONGO_COLLECTION = "IDS"

# Folder of HR documents that the chatbot indexes and answers from.
DOCS_DIRECTORY = "docs"
