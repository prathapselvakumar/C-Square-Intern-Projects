"""Telegram holiday bot that stores each chat's holidays in MySQL.

Usage in Telegram:
    add holiday <date> <name>   date as YYYY-MM-DD, e.g. "add holiday 2023-12-25 Christmas"
    list holidays
    /start, /help
"""

import os

import mysql.connector
import telebot
from telebot import types

bot = telebot.TeleBot(os.environ["TELEGRAM_BOT_TOKEN"])

db_connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "127.0.0.1"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DATABASE", "bot_message"),
)
cursor = db_connection.cursor()

# One row per holiday, owned by the Telegram chat that added it.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS holidays (
        chat_id INT,
        holiday_name VARCHAR(255),
        holiday_date DATE
    )
""")
db_connection.commit()

# Reply keyboard shown under every bot message.
menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_markup.row(types.KeyboardButton("Add Holiday"), types.KeyboardButton("List Holidays"))


def reply(message, text):
    """Send `text` to the chat that sent `message`, with the menu keyboard."""
    bot.send_message(message.chat.id, text, reply_markup=menu_markup)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    reply(message, "Welcome to your modern interactive Telegram bot. Here are some available commands:")


@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    """Handle the 'add holiday' and 'list holidays' text commands."""
    text = message.text.strip().lower()
    chat_id = message.chat.id

    if text.startswith("add holiday"):
        # Expected form: add holiday <date> <name...>
        words = text.split(" ")
        if len(words) < 3:
            reply(message, "Please provide the holiday name and date after 'add holiday'.")
            return

        holiday_date = words[2]
        holiday_name = " ".join(words[3:])
        if not (holiday_name and holiday_date):
            reply(message, "Please specify the holiday name and date after 'add holiday'.")
            return

        cursor.execute(
            "INSERT INTO holidays (chat_id, holiday_name, holiday_date) VALUES (%s, %s, %s)",
            (chat_id, holiday_name, holiday_date),
        )
        db_connection.commit()
        reply(message, f"Added '{holiday_name}' on {holiday_date} to your list of holidays.")

    elif text == "list holidays":
        cursor.execute(
            "SELECT holiday_name, holiday_date FROM holidays WHERE chat_id = %s",
            (chat_id,),
        )
        rows = cursor.fetchall()
        if rows:
            holiday_list = "\n".join(f"{name} ({date})" for name, date in rows)
            reply(message, f"Here's the list of your holidays:\n{holiday_list}")
        else:
            reply(message, "You haven't added any holidays yet.")

    else:
        reply(message, "I'm sorry, I don't understand that command. "
                       "Type 'Add Holiday' or 'List Holidays' or use the menu.")


if __name__ == "__main__":
    bot.polling()
