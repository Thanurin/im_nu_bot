import os
import threading

from flask import Flask

from telegram.ext import Application

from config import BOT_TOKEN
from handlers import setup_handlers
from database import init_database


web = Flask(__name__)


@web.route("/")
def home():
    return "CyberScan Bot is running!"



def run_web():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    web.run(
        host="0.0.0.0",
        port=port
    )



def run_bot():

    print("Starting Telegram Bot...")

    init_database()

    application = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )


    setup_handlers(application)


    print("🛡 CyberScan Bot Started...")


    application.run_polling()



if __name__ == "__main__":

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()


    run_bot()
