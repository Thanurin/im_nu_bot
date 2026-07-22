from telegram.ext import Application

from config import BOT_TOKEN
from handlers import setup_handlers
from database import init_database


# Create database when bot starts
init_database()


app = Application.builder().token(BOT_TOKEN).build()


setup_handlers(app)


print("🛡 CyberScan Bot Started...")


app.run_polling()