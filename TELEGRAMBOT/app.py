import telebot
from telebot import types

# Replace 'YOUR_API_TOKEN' with your actual Telegram Bot API token
bot = telebot.TeleBot('6491032940:AAF1RD_hM54yKDlWGIZw9SzjyaTspnavIW0')

holidays = {}

# Create a custom keyboard with modern buttons
menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu_item_add_holiday = types.KeyboardButton('Add Holiday ')
menu_item_list_holidays = types.KeyboardButton('List Holidays ')
menu_markup.row(menu_item_add_holiday, menu_item_list_holidays)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome to your modern interactive Telegram bot. Here are some available commands:", reply_markup=menu_markup)

@bot.message_handler(commands=['sayhello'])
def send_hello(message):
    bot.send_message(message.chat.id, "Hello! How can I assist you today?", reply_markup=menu_markup)

@bot.message_handler(commands=['echo'])
def echo_message(message):
    text = message.text.split('/echo ')[1]
    bot.send_message(message.chat.id, f"You said: {text}", reply_markup=menu_markup)

@bot.message_handler(commands=['time'])
def get_current_time(message):
    import datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bot.send_message(message.chat.id, f"The current time is: {current_time}", reply_markup=menu_markup)

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
                if chat_id in holidays:
                    holidays[chat_id].append(f"{holiday_name} ({holiday_date})")
                else:
                    holidays[chat_id] = [f"{holiday_name} ({holiday_date})"]
                bot.send_message(message.chat.id, f"Added '{holiday_name}' on {holiday_date} to your list of holidays.", reply_markup=menu_markup)
            else:
                bot.send_message(message.chat.id, "Please specify the holiday name and date after 'add holiday'.", reply_markup=menu_markup)
        else:
            bot.send_message(message.chat.id, "Please provide the holiday name and date after 'add holiday'.", reply_markup=menu_markup)
    elif text == "list holidays":
        chat_id = message.chat.id
        if chat_id in holidays:
            holiday_list = "\n".join(holidays[chat_id])
            bot.send_message(message.chat.id, f"Here's the list of your holidays:\n{holiday_list}", reply_markup=menu_markup)
        else:
            bot.send_message(message.chat.id, "You haven't added any holidays yet.", reply_markup=menu_markup)
    else:
        bot.send_message(message.chat.id, "I'm sorry, I don't understand that command. Type 'Add Holiday' or 'List Holidays' or use the menu.", reply_markup=menu_markup)

bot.polling()
