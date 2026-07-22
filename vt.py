import aiohttp
import asyncio

from config import VT_API_KEY


UPLOAD_URL = "https://www.virustotal.com/api/v3/files"


ANALYSIS_URL = (
    "https://www.virustotal.com/api/v3/analyses/"
)



async def upload_file(file_path):

    headers = {
        "x-apikey": VT_API_KEY
    }


    async with aiohttp.ClientSession() as session:


        # ==========================
        # Upload file
        # ==========================

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



        # ==========================
        # Error check
        # ==========================

        if "error" in upload_result:


            error_code = (
                upload_result
                ["error"]
                .get("code")
            )


            # File already scanned before
            if error_code == "AlreadySubmittedError":


                return {
                    "already_submitted": True,
                    "message":
                    "File already exists in VirusTotal"
                }


            return upload_result




        # ==========================
        # Get analysis ID
        # ==========================

        analysis_id = (
            upload_result
            .get("data", {})
            .get("id")
        )


        if not analysis_id:


            return {
                "error": {
                    "message":
                    "No analysis ID returned"
                }
            }




        # ==========================
        # Wait for VT result
        # ==========================

        for attempt in range(12):


            await asyncio.sleep(5)



            url = (
                ANALYSIS_URL
                +
                analysis_id
            )



            async with session.get(
                url,
                headers=headers
            ) as response:


                result = await response.json()



            if "data" not in result:

                continue



            attributes = (
                result
                ["data"]
                .get("attributes", {})
            )


            status = attributes.get(
                "status"
            )



            if status == "completed":


                return result



        return {

            "error": {

                "message":
                "VirusTotal scan timeout"

            }

        }






async def get_analysis(analysis_id):


    headers = {
        "x-apikey": VT_API_KEY
    }


    async with aiohttp.ClientSession() as session:


        url = (
            ANALYSIS_URL
            +
            analysis_id
        )


        async with session.get(
            url,
            headers=headers
        ) as response:


            return await response.json()
