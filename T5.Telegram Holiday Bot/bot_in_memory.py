"""Telegram holiday bot that keeps each chat's holidays in memory.

Holidays are lost when the bot restarts. See bot_mysql.py for the version
that stores them in a database.

Usage in Telegram:
    add holiday <date> <name>   e.g. "add holiday 2023-12-25 Christmas"
    list holidays
    /start, /help, /sayhello, /echo <text>, /time
"""

import datetime
import os

import telebot
from telebot import types

bot = telebot.TeleBot(os.environ["TELEGRAM_BOT_TOKEN"])

# Maps a chat ID to the list of "name (date)" strings added in that chat.
holidays_by_chat = {}

# Reply keyboard shown under every bot message.
menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_markup.row(types.KeyboardButton("Add Holiday"), types.KeyboardButton("List Holidays"))


def reply(message, text):
    """Send `text` to the chat that sent `message`, with the menu keyboard."""
    bot.send_message(message.chat.id, text, reply_markup=menu_markup)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    reply(message, "Welcome to your modern interactive Telegram bot. Here are some available commands:")


@bot.message_handler(commands=["sayhello"])
def send_hello(message):
    reply(message, "Hello! How can I assist you today?")


@bot.message_handler(commands=["echo"])
def send_echo(message):
    _, _, text = message.text.partition(" ")
    reply(message, f"You said: {text}")


@bot.message_handler(commands=["time"])
def send_current_time(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reply(message, f"The current time is: {current_time}")


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

        holidays_by_chat.setdefault(chat_id, []).append(f"{holiday_name} ({holiday_date})")
        reply(message, f"Added '{holiday_name}' on {holiday_date} to your list of holidays.")

    elif text == "list holidays":
        if chat_id in holidays_by_chat:
            holiday_list = "\n".join(holidays_by_chat[chat_id])
            reply(message, f"Here's the list of your holidays:\n{holiday_list}")
        else:
            reply(message, "You haven't added any holidays yet.")

    else:
        reply(message, "I'm sorry, I don't understand that command. "
                       "Type 'Add Holiday' or 'List Holidays' or use the menu.")


if __name__ == "__main__":
    bot.polling()
