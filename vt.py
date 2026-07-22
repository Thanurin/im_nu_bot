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

                upload_result = await response.json()


        # Check upload error
        if "error" in upload_result:
            return upload_result


        if "data" not in upload_result:
            return {
                "error": {
                    "message": "No analysis ID returned",
                    "details": upload_result
                }
            }


        analysis_id = upload_result["data"]["id"]


        # Wait for VirusTotal analysis
        for i in range(10):

            await asyncio.sleep(5)


            check_url = (
                f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
            )


            async with session.get(
                check_url,
                headers=headers
            ) as response:

                result = await response.json()


            if "data" in result:

                status = (
                    result["data"]
                    ["attributes"]
                    .get("status")
                )


                if status == "completed":
                    return result


        return {
            "error": {
                "message": "VirusTotal scan timeout"
            }
        }
