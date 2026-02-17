import os
import requests
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load environment variables
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
REMOVE_BG_API = os.getenv("REMOVE_BG_API")

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send me an image and I will remove its background 🎯")

def remove_background(update: Update, context: CallbackContext):
    try:
        photo = update.message.photo[-1].get_file()
        photo.download("input.jpg")

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
            update.message.reply_photo(photo=open("output.png", "rb"))
        else:
            update.message.reply_text("Error removing background 😢")

    except Exception as e:
        update.message.reply_text("Something went wrong ⚠️")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, remove_background))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    keep_alive()
    main()
