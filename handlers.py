# handlers.py

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


from vt import upload_file, get_analysis


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





async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    add_user(
        update.effective_user
    )


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

❤️ អរគុណសម្រាប់ការគាំទ្រ!


ការឧបត្ថម្ភរបស់អ្នក
ជួយឲ CyberScan Bot
បន្តអភិវឌ្ឍ។


🙏 Thank you!

"""


    with open(
        "qr.jpg",
        "rb"
    ) as photo:


        await query.message.reply_photo(

            photo=photo,

            caption=caption

        )







# ==================================
# VIRUSTOTAL FILE SCANNER
# ==================================


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



    file_path = (

        f"temp_{document.file_name}"

    )



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



        # =========================
        # VT ERROR
        # =========================


        if "error" in result:


            error = result["error"].get(

                "message",

                "Unknown error"

            )


            await status.edit_text(

                f"""
⚠️ VirusTotal Error


{error}
"""

            )

            return





        # =========================
        # ALREADY SCANNED
        # =========================


        if result.get(

            "already_submitted"

        ):


            await status.edit_text(

                """
♻️ File already exists in VirusTotal

Checking previous scan...
"""

            )


            return





        # =========================
        # GET STATS DIRECTLY
        # =========================


        stats = (

            result

            .get("data", {})

            .get("attributes", {})

            .get("stats")

        )





        # =========================
        # NEW ANALYSIS
        # =========================


        if not stats:


            analysis_id = (

                result

                .get("data", {})

                .get("id")

            )



            if not analysis_id:


                await status.edit_text(

                    f"""
❌ Cannot get VirusTotal analysis ID


Response:

{result}
"""

                )

                return





            await status.edit_text(

                "⏳ VirusTotal កំពុងវិភាគ..."

            )



            await asyncio.sleep(15)



            analysis = await get_analysis(

                analysis_id

            )



            stats = (

                analysis

                .get("data", {})

                .get("attributes", {})

                .get("stats", {})

            )





        # =========================
        # RESULT
        # =========================


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


        if os.path.exists(

            file_path

        ):


            os.remove(

                file_path

            )









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
