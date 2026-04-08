import mysql.connector
import telegram
from telegram.ext import Updater
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import asyncio
import json




# Connect to the MySQL database
conn = mysql.connector.connect(
    host="127.0.0.1",
     port=3306,
    user="root",
    password="Tmpt__636113",
    database="chat_id"
)

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Query to retrieve the chat id and API token
query = "SELECT chat_id, api_token FROM telegram_table"

# Execute the query
cursor.execute(query)

# Fetch the chat id and API token
chat_id, api_token = cursor.fetchone()
bot = telegram.Bot(token=api_token)

# Close the cursor and database connection
cursor.close()
conn.close()

async def send_image(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            image_bytes = BytesIO(image_file.read())
            await bot.send_photo(chat_id=chat_id, photo=image_bytes)
    except Exception as exc:
        error_message = f"An error occurred while sending the image: {exc}"
        await bot.send_message(chat_id=chat_id, text=error_message)

async def main():
    # Generate the image using your other Python script and save it to a file
    # For example, assuming you have an image file 'output.png'

    # Load data from the JSON file
    with open('data.json', 'r') as f:
        data = json.load(f)

  # Load images
    img1 = Image.open('mainimg.jpg')
    img2 = Image.open('up_arrow.jpg')
    img3 = Image.open('down_arrow.jpg')

    # Copy the background image
    new = img1.copy()
    draw = ImageDraw.Draw(new)
    font = ImageFont.truetype('impact.ttf', 40)

    colors = {
        "C": (199, 21, 133),
        "P": (199, 21, 133)
    }

    if data[0]["InvoiceTotal"] < data[1]["InvoiceTotal"]:
        img3 = img3.resize((30, 60))
        new.paste(img3, (240, 370))
    else:
        img2 = img2.resize((30, 60))
        new.paste(img2, (240, 370))

    if data[0]["InvoiceCount"] < data[1]["InvoiceCount"]:
        img3 = img3.resize((30, 60))
        new.paste(img3, (240, 470))
    else:
        img2 = img2.resize((30, 60))
        new.paste(img2, (240, 470))

    if data[0]["InvoiceAvg"] < data[1]["InvoiceAvg"]:
        img3 = img3.resize((30, 60))
        new.paste(img3, (240, 570))
    else:
        img2 = img2.resize((30, 60))
        new.paste(img2, (240, 570))

    if data[0]["InvoiceCustomerCount"] < data[1]["InvoiceCustomerCount"]:
        img3 = img3.resize((30, 60))
        new.paste(img3, (240, 670))
    else:
        img2 = img2.resize((30, 60))
        new.paste(img2, (240, 670))

    if data[0]["InvoiceLineCount"] < data[1]["InvoiceLineCount"]:
        img3 = img3.resize((30, 60))
        new.paste(img3, (240, 770))
    else:
        img2 = img2.resize((30, 60))
        new.paste(img2, (240, 770))

    if data[0]["NetSale"] < data[1]["NetSale"]:
        img3 = img3.resize((40, 70))
        new.paste(img3, (235, 1110))
    else:
        img2 = img2.resize((40, 70))
        new.paste(img2, (235, 1110))

    for i in range(2):
        day_type = data[i]['dayType']
        color = colors.get(day_type, (0, 0, 0))
        draw.text((275 if i == 0 else 10, 280), data[i]['DocDt'], font=font, fill=color)
        draw.text((275 if i == 0 else 10, 380), data[i]['InvoiceTotal'], font=font, fill=color)
        draw.text((290 if i == 0 else 50, 480), data[i]['InvoiceCount'], font=font, fill=color)
        draw.text((290 if i == 0 else 50, 580), data[i]['InvoiceAvg'], font=font, fill=color)
        draw.text((290 if i == 0 else 50, 680), data[i]['InvoiceCustomerCount'], font=font, fill=color)
        draw.text((290 if i == 0 else 50, 780), data[i]['InvoiceLineCount'], font=font, fill=color)
        net_sale = float(data[i]['NetSale']) / 100000
        net_sale_formatted = "{:,.3f}".format(net_sale)
        draw.text((300 if i == 0 else 40, 1120), str(net_sale_formatted) + "L", font=font, fill=color)

    image_path = 'output.png'
    await send_image(image_path)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
