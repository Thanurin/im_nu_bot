import aiohttp
import asyncio
from config import VT_API_KEY


UPLOAD_URL = "https://www.virustotal.com/api/v3/files"


async def upload_file(file_path):

    headers = {
        "x-apikey": VT_API_KEY
    }


    async with aiohttp.ClientSession() as session:

        # Upload file
        with open(file_path, "rb") as file:

            form = aiohttp.FormData()

            form.add_field(
                "file",
                file,
                filename=file_path
            )


            async with session.post(
                UPLOAD_URL,
                headers=headers,
                data=form
            ) as response:

                upload_data = await response.json()


        if "data" not in upload_data:

            raise Exception(upload_data)


        analysis_id = upload_data["data"]["id"]


        # Wait VirusTotal scan
        await asyncio.sleep(15)


        analysis_url = (
            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        )


        async with session.get(
            analysis_url,
            headers=headers
        ) as response:


            result = await response.json()


            return result