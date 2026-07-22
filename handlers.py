from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from database import (
    add_user,
    increase_scan_count,
)

from vt import upload_file

import os



WELCOME_TEXT = """

👋 សួស្តី!

តើមានអ្វីសង្ស័យឲខ្ញុំជួយមែនទេ?


📄 សូមផ្ញើ ឬ Forward File មកខ្ញុំ។

ខ្ញុំនឹងស្កេនវាជាមួយ VirusTotal
ហើយបង្ហាញលទ្ធផលឲអ្នកភ្លាមៗ។

"""



async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Save user
    add_user(update.effective_user)


    keyboard = [

        [

            InlineKeyboardButton(
                "❤️ ជួយឧបត្ថម្ភខ្ញុំ",
                callback_data="donate"
            )

        ]

    ]


    await update.message.reply_text(

        WELCOME_TEXT,

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )





async def donate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()


    caption = """

❤️ សូមថ្លែងអំណរគុណចំពោះលោកអ្នក

ដែលបានជួយគាំទ្រ និងឧបត្ថម្ភខ្ញុំ។


ការឧបត្ថម្ភរបស់លោកអ្នក

គឺជាកម្លាំងចិត្តដ៏មានតម្លៃ

សម្រាប់ខ្ញុំក្នុងការបន្តអភិវឌ្ឍ

CyberScan Bot។


សូមអរគុណ! 🙏

"""


    with open("qr.jpg", "rb") as photo:

        await query.message.reply_photo(

            photo=photo,

            caption=caption

        )





# ==========================
# FILE SCANNER
# ==========================

async def scan_file(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    document = update.message.document


    if not document:
        return



    status = await update.message.reply_text(

        "🔍 កំពុងទទួល File..."

    )



    file = await context.bot.get_file(
        document.file_id
    )



    file_path = f"temp_{document.file_name}"



    await file.download_to_drive(
        file_path
    )



    await status.edit_text(

        "☁️ កំពុង Upload ទៅ VirusTotal..."

    )



    try:

        result = await upload_file(
            file_path
        )


        await status.edit_text(

            f"""
🛡 CyberScan Report


📄 File:
{document.file_name}


📊 VirusTotal Result:


{result}

"""

        )


        # Increase scan count

        increase_scan_count(
            update.effective_user.id
        )


    except Exception as e:


        await status.edit_text(

            f"""
❌ Scan Failed


Error:

{e}
"""

        )



    finally:


        if os.path.exists(file_path):

            os.remove(file_path)





def setup_handlers(app):


    # Start command

    app.add_handler(

        CommandHandler(
            "start",
            start
        )

    )



    # Donation button

    app.add_handler(

        CallbackQueryHandler(

            donate,

            pattern="donate"

        )

    )



    # File scanner

    app.add_handler(

        MessageHandler(

            filters.Document.ALL,

            scan_file

        )

    )