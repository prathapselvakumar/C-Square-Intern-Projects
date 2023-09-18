"""Shared application core for the HR Connect Bot.

This module creates the Flask app and everything the route modules share:
JSON serialisation, request tracing, the LlamaIndex document index, the
chat-history database, and the session helpers that integrate with the
C-Square single sign-on (SSO) service.
"""

import base64
import datetime
import json
import os
import uuid
from functools import wraps

import flask
import openai
import orjson
import requests
from flask import abort, redirect, request, session
from flask.json.provider import JSONProvider
from flask_cors import CORS
from llama_index import SimpleDirectoryReader, VectorStoreIndex

import config
from utils.crypto import Crypt
from utils.mongo_connector import MongoConnector

# ----------------------------------------------------------------------
# Flask application
# ----------------------------------------------------------------------
app = flask.Flask(__name__)
CORS(app)
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = config.SECRET_KEY

# Address of the development server. Redirect URLs built from it are
# rewritten to the public APP_BASE_URL so SSO sends users back correctly.
LOCAL_DEV_URL = "http://127.0.0.1:5003"

# When True, a visitor without a session is given a placeholder user instead
# of being sent to SSO. Useful for local testing; disable in production.
ALLOW_DUMMY_SESSION = True


class OrJSONProvider(JSONProvider):
    """JSON provider backed by orjson, which also serialises datetimes."""

    def dumps(self, obj, *, option=None, **kwargs):
        if option is None:
            option = orjson.OPT_APPEND_NEWLINE | orjson.OPT_NAIVE_UTC
        return orjson.dumps(obj, option=option).decode()

    def loads(self, s, **kwargs):
        return orjson.loads(s)


app.json = OrJSONProvider(app)


class RequestTracingMiddleware:
    """WSGI middleware that tags every request with a unique ID and a timestamp."""

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        environ["HTTP_X_REQUEST_ID"] = str(uuid.uuid4())
        environ["HTTP_X_REQUEST_TIME"] = str(datetime.datetime.utcnow().timestamp())
        return self.wsgi_app(environ, start_response)


app.wsgi_app = RequestTracingMiddleware(app.wsgi_app)

# ----------------------------------------------------------------------
# Document index for retrieval-augmented answers
# ----------------------------------------------------------------------
os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
openai.api_key = config.OPENAI_API_KEY

# Every file in the docs folder is embedded once at start-up. Questions are
# answered by retrieving the most relevant passages and passing them to the LLM.
print("Loading documents")
documents = SimpleDirectoryReader(config.DOCS_DIRECTORY).load_data()
print("Building vector index")
document_index = VectorStoreIndex.from_documents(documents)
print("Vector index ready")
query_engine = document_index.as_query_engine()

# ----------------------------------------------------------------------
# Shared services
# ----------------------------------------------------------------------
crypt_helper = Crypt()
chat_db = MongoConnector(config.MONGO_HOST, config.MONGO_DB, config.MONGO_CONN_POOL_SIZE)


# ----------------------------------------------------------------------
# Single sign-on
# ----------------------------------------------------------------------
def set_session_from_token(token):
    """Validate an SSO token with the SSO service and copy the user into the session.

    The token is Base64-encoded JSON that carries the SSO session ID and the
    user's code, name, and mobile number.
    """
    token_data = json.loads(base64.b64decode(token))
    if session.get("auth_token") == token:
        return

    validation_url = f"{config.CSQ_SSO_BASE_URL}/csquare/login/session/{token_data['session_id']}?flag=1"
    response = requests.get(validation_url)
    if response.status_code != 200:
        # Keep an existing login for the same user even if this token has expired.
        if session.get("logged_in") and session["code"] == token_data["user_code"]:
            return
        session.clear()
        abort(401)

    session.clear()
    session["logged_in"] = True
    session["mobile"] = token_data["mobile"]
    session["code"] = token_data["user_code"]
    session["name"] = token_data["user_name"]
    session["session_id"] = token_data["session_id"]
    session["auth_token"] = token
    session["user"] = encode_session_value(str(token_data["mobile"]))
    session["profile"] = {
        "name": token_data["user_name"],
        "note": "C-Square",
        "csqLicAdmin": True,
    }


def build_redirect_url(base_url):
    """Return `base_url` with the current query string, minus the auth token."""
    url = base_url.replace(LOCAL_DEV_URL, config.APP_BASE_URL)
    query_string = "&".join(
        f"{name}={request.args.get(name)}" for name in request.args if name != "auth_token"
    )
    if query_string:
        url += "?" + query_string
    return url


def get_home_url():
    """Return the public URL of the chat home page."""
    return build_redirect_url(request.host_url + config.APP_HOME_URL)


@app.errorhandler(401)
def handle_unauthorized(error):
    """Send unauthenticated users to SSO, asking it to return them to this page."""
    return_url = build_redirect_url(request.base_url)
    return redirect(f"{config.CSQ_SSO_BASE_URL}/csquare/login?redirect_url={return_url}")


@app.before_request
def handle_before_request():
    """Start a session when SSO redirects back with an auth_token parameter."""
    auth_token = request.args.get("auth_token")
    if auth_token:
        set_session_from_token(auth_token)


# ----------------------------------------------------------------------
# Encrypted session values
# ----------------------------------------------------------------------
def encode_session_value(value):
    """Encrypt `value` with a per-session key so it can be stored in the cookie."""
    session_key = session.get("key")
    if not session_key:
        session_key = crypt_helper.encrypt(str(uuid.uuid4()), app.config["SECRET_KEY"])
        session["key"] = session_key

    plain_key = crypt_helper.decrypt(session_key, app.config["SECRET_KEY"])
    return crypt_helper.encrypt(value, plain_key)


def decode_session_value(value):
    """Reverse `encode_session_value`."""
    plain_key = crypt_helper.decrypt(session.get("key"), app.config["SECRET_KEY"])
    return crypt_helper.decrypt(value, plain_key)


def create_dummy_session():
    """Fill the session with a placeholder user for local testing."""
    session.clear()
    session["user"] = encode_session_value("dummyuser")
    session["profile"] = {
        "name": "Dummy User",
        "note": "C-Square Info-Solutions Limited",
    }


def session_required(view):
    """Decorator that passes the logged-in user's ID to `view` or rejects the request."""

    @wraps(view)
    def validate(*args, **kwargs):
        encoded_user = session.get("user")
        if not encoded_user:
            if not ALLOW_DUMMY_SESSION:
                abort(401)
            create_dummy_session()
            encoded_user = session.get("user")

        try:
            user = decode_session_value(encoded_user)
        except Exception:
            abort(401)
        if not user:
            abort(401)

        return view(user, *args, **kwargs)

    return validate
