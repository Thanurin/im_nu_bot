import aiohttp
import asyncio
from config import VT_API_KEY


UPLOAD_URL = "https://www.virustotal.com/api/v3/files"


async def upload_file(file_path):

    headers = {
        "x-apikey": VT_API_KEY
    }


    async with aiohttp.ClientSession() as session:

        with open(file_path, "rb") as file:

            data = aiohttp.FormData()

            data.add_field(
                "file",
                file,
                filename=file_path
            )


            async with session.post(
                UPLOAD_URL,
                headers=headers,
                data=data
            ) as response:

                result = await response.json()


                if "error" in result:
                    return result


                analysis_id = result["data"]["id"]


        # wait for scan result
        await asyncio.sleep(15)


        result_url = (
            f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        )


        async with session.get(
            result_url,
            headers=headers
        ) as response:

            return await response.json()
