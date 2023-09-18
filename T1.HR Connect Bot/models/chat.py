"""Chat sessions, message history, and the chat API endpoints.

Chat data lives in two MongoDB collections:
    session_mst  one document per chat session (owner, start/end time, status)
    session_det  one document per question-and-answer pair in a session
"""

import datetime

from bson.objectid import ObjectId
from flask import request, session

from core import app, chat_db, document_index, query_engine, session_required

SESSION_COLLECTION = "session_mst"
HISTORY_COLLECTION = "session_det"

SESSION_OPEN = 1
SESSION_CLOSED = 0


class ChatUser:
    """A user's chat session and its stored history."""

    def __init__(self, mobile):
        self.mobile = mobile
        self.session_id = None
        self.session_status = SESSION_CLOSED
        self.session_history = []

    def get_session(self, session_id=None):
        """Load `session_id` if given, otherwise the user's open session, otherwise a new one."""
        if session_id and self.load_session(session_id):
            return self.session_id

        open_session = chat_db.db[SESSION_COLLECTION].find_one(
            {"mobile": self.mobile, "status": SESSION_OPEN}
        )
        if not open_session:
            return self.create_session()

        self.session_id = str(open_session["_id"])
        self.session_status = open_session["status"]
        self.get_history()
        return self.session_id

    def reset_session(self):
        """Forget the current session in memory without touching the database."""
        self.session_id = None
        self.session_status = SESSION_CLOSED
        self.session_history = []

    def load_session(self, session_id):
        """Load an existing session by ID. Returns True when it exists."""
        self.reset_session()
        stored_session = chat_db.db[SESSION_COLLECTION].find_one({"_id": ObjectId(session_id)})
        if not stored_session:
            return False

        self.session_id = session_id
        self.session_status = stored_session["status"]
        self.get_history()
        return True

    def create_session(self):
        """Open a new chat session for this user and return its ID."""
        now = datetime.datetime.utcnow()
        new_session = {
            "mobile": self.mobile,
            "start_time": now,
            "end_time": None,
            "status": SESSION_OPEN,
            "last_update": now,
        }
        result = chat_db.db[SESSION_COLLECTION].insert_one(new_session)

        self.reset_session()
        self.session_id = str(result.inserted_id)
        self.session_status = SESSION_OPEN
        return self.session_id

    def get_history(self):
        """Load every question-and-answer pair stored for the current session."""
        if not self.session_id:
            return []

        self.session_history = list(
            chat_db.db[HISTORY_COLLECTION].find({"session_id": ObjectId(self.session_id)})
        )
        return self.session_history

    def add_history(self, question, answer):
        """Store one question-and-answer pair and update the session timestamp."""
        entry = {"session_id": ObjectId(self.session_id), "q": question, "a": answer}
        self.session_history.append(entry)

        chat_db.db[HISTORY_COLLECTION].insert_one(entry)
        chat_db.db[SESSION_COLLECTION].update_one(
            {"_id": ObjectId(self.session_id)},
            {"$set": {"last_update": datetime.datetime.utcnow()}},
        )

    def close_session(self, session_id):
        """Mark a session as closed so the next message starts a fresh one."""
        if not chat_db.db[SESSION_COLLECTION].find_one({"_id": ObjectId(session_id)}):
            self.reset_session()
            return

        now = datetime.datetime.utcnow()
        chat_db.db[SESSION_COLLECTION].update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"last_update": now, "end_time": now, "status": SESSION_CLOSED}},
        )


class ChatMessage:
    """One incoming message and the logic that produces the bot's reply."""

    def __init__(self, from_user, to_user, text=None):
        self.user = ChatUser(from_user)
        self.user.get_session(session_id=session.get("chat_session_id"))
        session["chat_session_id"] = self.user.session_id

        self.to_user = to_user
        self.text = text
        self.history = [(entry["q"], entry["a"]) for entry in self.user.session_history]

    def get_reply(self):
        """Answer the message from the indexed HR documents (stateless)."""
        print(self.text)
        response = query_engine.query(self.text)
        print(response)
        return response.response

    def send_chat(self):
        """Answer the message with a chat engine and save the exchange to history."""
        chat_engine = document_index.as_chat_engine(verbose=True)
        reply = str(chat_engine.chat(self.text)).strip()
        self.add_history(self.text, reply)
        return reply

    def add_history(self, question, answer):
        """Record an exchange in memory and in MongoDB."""
        self.history.append((question, answer))
        self.user.add_history(question, answer)


@app.route("/chat/send-message", methods=["POST"])
@session_required
def chat_send_message(user):
    """Receive a message from the chat page and return the bot's answer."""
    payload = request.json
    message = ChatMessage(user, payload["to"], text=payload["text"])
    return {"status": True, "statusMessage": "Message sent", "response": message.get_reply()}


@app.route("/chat/clear-history", methods=["GET"])
@session_required
def chat_clear_history(user):
    """Close the current chat session and open a new, empty one."""
    chat_user = ChatUser(user)
    chat_user.close_session(session_id=session.get("chat_session_id"))
    session["chat_session_id"] = chat_user.create_session()
    return "History cleared"
