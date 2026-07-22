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
import asyncio



WELCOME_TEXT = """

👋 សួស្តី!

តើមានអ្វីសង្ស័យឲខ្ញុំជួយមែនទេ?


📄 សូមផ្ញើ File មកខ្ញុំ។

ខ្ញុំនឹងស្កេនវាជាមួយ VirusTotal
ហើយបង្ហាញលទ្ធផលឲអ្នក។


🛡 Powered by VirusTotal

"""



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
        reply_markup=InlineKeyboardMarkup(keyboard)
    )




async def donate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()


    caption = """

❤️ អរគុណសម្រាប់ការគាំទ្រ!

ការឧបត្ថម្ភរបស់អ្នក
ជួយឲ CyberScan Bot
បន្តអភិវឌ្ឍ។


🙏 Thank you!

"""


    with open("qr.jpg", "rb") as photo:

        await query.message.reply_photo(
            photo=photo,
            caption=caption
        )





# ======================
# VIRUSTOTAL SCANNER
# ======================


async def scan_file(update: Update, context: ContextTypes.DEFAULT_TYPE):


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
        "☁️ Upload ទៅ VirusTotal..."
    )



    try:


        result = await upload_file(
            file_path
        )



        # Check VirusTotal error

        if "error" in result:

            message = result["error"].get(
                "message",
                "Unknown error"
            )


            await status.edit_text(
                f"""
⚠️ VirusTotal Notice

{message}

Please try again later.
"""
            )

            return



        # Get analysis id

        analysis_id = (
            result
            .get("data", {})
            .get("id")
        )



        if not analysis_id:

            await status.edit_text(
                "❌ Cannot get VirusTotal analysis ID"
            )

            return



        await status.edit_text(
            "⏳ កំពុងរង់ចាំ VirusTotal វិភាគ..."
        )



        # wait for VT processing

        await asyncio.sleep(15)



        # ask VT again

        from vt import get_analysis


        analysis = await get_analysis(
            analysis_id
        )



        stats = (
            analysis
            .get("data", {})
            .get("attributes", {})
            .get("stats", {})
        )



        malicious = stats.get(
            "malicious",
            0
        )

        suspicious = stats.get(
            "suspicious",
            0
        )

        harmless = stats.get(
            "harmless",
            0
        )

        undetected = stats.get(
            "undetected",
            0
        )



        if malicious > 0:

            verdict = "🚨 MALWARE DETECTED"


        elif suspicious > 0:

            verdict = "⚠️ SUSPICIOUS"


        else:

            verdict = "✅ CLEAN"



        report = f"""

🛡 CyberScan Report


📄 File:
{document.file_name}


🔍 Result:

{verdict}


📊 Detection:


🚨 Malicious:
{malicious}


⚠️ Suspicious:
{suspicious}


✅ Clean:
{harmless}


❓ Undetected:
{undetected}



Powered by VirusTotal

"""


        await status.edit_text(
            report
        )



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


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )



    app.add_handler(
        CallbackQueryHandler(
            donate,
            pattern="donate"
        )
    )



    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            scan_file
        )
    )
