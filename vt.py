import aiohttp
from config import VT_API_KEY


VT_URL = "https://www.virustotal.com/api/v3/files"



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
                VT_URL,
                headers=headers,
                data=data
            ) as response:


                result = await response.json()


                return result