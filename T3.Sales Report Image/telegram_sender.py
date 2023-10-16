"""Send an image to a Telegram chat, reporting any failure to the same chat."""

from io import BytesIO

import telegram


async def send_image(bot_token, chat_id, image_path):
    """Upload `image_path` as a photo. On failure, send the error message instead."""
    bot = telegram.Bot(token=bot_token)
    try:
        with open(image_path, "rb") as image_file:
            await bot.send_photo(chat_id=chat_id, photo=BytesIO(image_file.read()))
    except Exception as error:
        await bot.send_message(chat_id=chat_id, text=f"An error occurred while sending the image: {error}")
