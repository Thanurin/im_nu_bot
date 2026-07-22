import os
import asyncio

from flask import Flask

from telegram.ext import Application

from config import BOT_TOKEN
from handlers import setup_handlers
from database import init_database


app = Flask(__name__)


telegram_app = None


@app.route("/")
def home():
    return "🛡 CyberScan Bot is running!"



async def start_bot():

    global telegram_app

    init_database()

    telegram_app = Application.builder().token(
        BOT_TOKEN
    ).build()


    setup_handlers(telegram_app)


    await telegram_app.initialize()

    await telegram_app.start()

    await telegram_app.updater.start_polling()



def run_telegram():

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        start_bot()
    )


@app.before_request
def start_once():

    global telegram_app

    if telegram_app is None:

        import threading

        threading.Thread(
            target=run_telegram,
            daemon=True
        ).start()



if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port
    )
