import os
import asyncio

from flask import Flask

from telegram.ext import Application

from config import BOT_TOKEN
from handlers import setup_handlers
from database import init_database


app = Flask(__name__)


@app.route("/")
def home():
    return "CyberScan Bot is running!"



async def start_bot():

    init_database()

    bot = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    setup_handlers(bot)

    print("🛡 CyberScan Bot Started...")

    await bot.initialize()
    await bot.start()

    await bot.updater.start_polling()




def run_async_bot():

    asyncio.run(
        start_bot()
    )



if __name__ == "__main__":

    import threading


    threading.Thread(
        target=run_async_bot,
        daemon=True
    ).start()


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
