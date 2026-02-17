import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
REMOVE_BG_API = os.getenv("REMOVE_BG_API")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an image and I will remove its background 🎯")

async def remove_background(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = await update.message.photo[-1].get_file()
        await photo.download_to_drive("input.jpg")

        with open("input.jpg", "rb") as image_file:
            response = requests.post(
                "https://api.remove.bg/v1.0/removebg",
                files={"image_file": image_file},
                data={"size": "auto"},
                headers={"X-Api-Key": REMOVE_BG_API},
            )

        if response.status_code == 200:
            with open("output.png", "wb") as out:
                out.write(response.content)

            await update.message.reply_photo(photo=open("output.png", "rb"))
        else:
            await update.message.reply_text("Error removing background 😢")

    except Exception as e:
        await update.message.reply_text("Something went wrong ⚠️")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, remove_background))

    app.run_polling()

if __name__ == "__main__":
    main()
