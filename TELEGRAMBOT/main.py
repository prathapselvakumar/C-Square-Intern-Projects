import telebot
import mysql.connector
from telebot import types

# Replace 'YOUR_API_TOKEN' with your actual Telegram Bot API token
bot = telebot.TeleBot('6491032940:AAF1RD_hM54yKDlWGIZw9SzjyaTspnavIW0')

# Connect to the MySQL database with a specific port
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,  # Replace with your database port
    user="host",
    password="Tmpt__636113",
    database="bot_message"
)

cursor = db.cursor()

# Create a table to store holidays if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS holidays (
        chat_id INT,
        holiday_name VARCHAR(255),
        holiday_date DATE
    )
""")
db.commit()

# Create a custom keyboard with modern buttons
menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_item_add_holiday = types.KeyboardButton('Add Holiday ')
menu_item_list_holidays = types.KeyboardButton('List Holidays ')
menu_markup.row(menu_item_add_holiday, menu_item_list_holidays)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome to your modern interactive Telegram bot. Here are some available commands:", reply_markup=menu_markup)

# ... other message handlers ...

@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    text = message.text.lower()

    if text.startswith("add holiday"):
        chat_id = message.chat.id
        input_parts = text.split(' ')
        if len(input_parts) >= 3:
            holiday_date = input_parts[2]
            holiday_name = ' '.join(input_parts[3:])
            if holiday_name and holiday_date:
                # Insert the data into the database
                cursor.execute("INSERT INTO holidays (chat_id, holiday_name, holiday_date) VALUES (%s, %s, %s)", (chat_id, holiday_name, holiday_date))
                db.commit()
                bot.send_message(message.chat.id, f"Added '{holiday_name}' on {holiday_date} to your list of holidays.", reply_markup=menu_markup)
            else:
                bot.send_message(message.chat.id, "Please specify the holiday name and date after 'add holiday'.", reply_markup=menu_markup)
    elif text == "list holidays":
        chat_id = message.chat.id
        # Fetch the data from the database for the current user
        cursor.execute("SELECT holiday_name, holiday_date FROM holidays WHERE chat_id = %s", (chat_id,))
        result = cursor.fetchall()
        if result:
            holiday_list = "\n".join([f"{row[0]} ({row[1]})" for row in result])
            bot.send_message(message.chat.id, f"Here's the list of your holidays:\n{holiday_list}", reply_markup=menu_markup)
        else:
            bot.send_message(message.chat.id, "You haven't added any holidays yet.", reply_markup=menu_markup)
    else:
        bot.send_message(message.chat.id, "I'm sorry, I don't understand that command. Type 'Add Holiday' or 'List Holidays' or use the menu.", reply_markup=menu_markup)

bot.polling()
