import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import requests
import json
import time

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
API_KEY = os.getenv("BAIDU_API_KEY")
SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")

async def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            data = await response.json()
            return str(data.get("access_token"))

async def create_task(audio_file_name):
    url = "https://aip.baidubce.com/rpc/2.0/aasr/v1/create?access_token=" + await get_access_token()
    payload = {
        "speech_url": f"https://backend.faradawn.site:8001/audio/{audio_file_name}",
        "format": "m4a",
        "pid": 1737,
        "rate": 16000
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            response_json = await response.json()
            return response_json.get("task_id")

async def get_res(task_id):
    url = "https://aip.baidubce.com/rpc/2.0/aasr/v1/query?access_token=" + await get_access_token()
    payload = {
        "task_ids": [task_id]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            return await response.json()

async def check_task_status(task_id, max_attempts=10, delay=1):
    for attempt in range(max_attempts):
        response = await get_res(task_id)
        print(f"Attempt {attempt + 1}: Checking task status...")
        if response.get("tasks_info"):
            task_status = response["tasks_info"][0]["task_status"]
            print(f"Current status: {task_status}")
            if task_status == "Success":
                return response["tasks_info"][0]["task_result"]
            elif task_status == "Failed":
                print("Task failed.")
                return None
        await asyncio.sleep(delay)
    print("Max attempts reached. Task not completed.")
    return None

async def convert_audio_to_text(file_path):
    audio_file_name = os.path.basename(file_path)
    
    task_id = await create_task(audio_file_name)
    if task_id:
        print(f"Task created with ID: {task_id}")
        result = await check_task_status(task_id)
        if result and "result" in result:
            return result["result"][0]
        else:
            print("Failed to get result from task.")
            return None
    else:
        print("Failed to create task.")
        return None
    

# expose the audio url for baidu text-to-speech to fetch (add to questions.py)
# @router.get("/audio/{filename}.m4a")
# async def get_m4a_audio(filename: str):
#     AUDIO_FOLDER = "audio_submissions"
#     file_path = os.path.join(AUDIO_FOLDER, f"{filename}.m4a")
    
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="M4A audio file not found")
    
#     return FileResponse(file_path, media_type="audio/m4a", filename=f"{filename}.m4a")