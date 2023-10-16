"""Build the sales report card and send it to Telegram, using credentials from MySQL.

The bot token and chat ID are read from the `telegram_table` table (see
telegram_credentials.sql). MySQL connection details come from the MYSQL_*
environment variables.
"""

import asyncio
import os

import mysql.connector

from report_image import save_report_image
from telegram_sender import send_image


def load_telegram_credentials():
    """Return (chat_id, api_token) from the first row of telegram_table."""
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "chat_id"),
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT chat_id, api_token FROM telegram_table")
        chat_id, api_token = cursor.fetchone()
        cursor.close()
        return chat_id, api_token
    finally:
        connection.close()


async def main():
    chat_id, api_token = load_telegram_credentials()
    image_path = save_report_image()
    await send_image(api_token, chat_id, image_path)


if __name__ == "__main__":
    asyncio.run(main())
