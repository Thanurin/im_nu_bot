import aiohttp
import asyncio
import json
from config import VT_API_KEY


UPLOAD_URL = "https://www.virustotal.com/api/v3/files"


async def upload_file(file_path):

    headers = {
        "x-apikey": VT_API_KEY
    }

    async with aiohttp.ClientSession() as session:

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

                text = await response.text()

                print("VT Upload Status:", response.status)
                print("VT Response:", text)

                try:
                    upload_data = json.loads(text)
                except:
                    raise Exception(
                        f"VirusTotal returned non JSON:\n{text}"
                    )


        if "data" not in upload_data:
            raise Exception(upload_data)


        analysis_id = upload_data["data"]["id"]


        await asyncio.sleep(15)


        analysis_url = (
            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        )


        async with session.get(
            analysis_url,
            headers=headers
        ) as response:

            text = await response.text()

            print("Analysis Status:", response.status)
            print("Analysis Response:", text)

            result = json.loads(text)

            return result
        
