import os
import threading

from flask import Flask

from telegram.ext import Application

from config import BOT_TOKEN
from handlers import setup_handlers
from database import init_database


app = Flask(__name__)


@app.route("/")
def home():
    return "CyberScan Bot is running!"


def run_bot():

    init_database()

    bot = Application.builder().token(BOT_TOKEN).build()

    setup_handlers(bot)

    bot.run_polling()



threading.Thread(
    target=run_bot
).start()



if __name__ == "__main__":

    port = int(os.environ.get(
        "PORT",
        10000
    ))

    app.run(
        host="0.0.0.0",
        port=port
    )
