"""Build the sales report card and send it to Telegram.

The bot token and chat ID come from the TELEGRAM_BOT_TOKEN and
TELEGRAM_CHAT_ID environment variables. To read them from MySQL instead,
use send_report_from_db.py.
"""

import asyncio
import os

from report_image import save_report_image
from telegram_sender import send_image


async def main():
    image_path = save_report_image()
    await send_image(os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"], image_path)


if __name__ == "__main__":
    asyncio.run(main())
