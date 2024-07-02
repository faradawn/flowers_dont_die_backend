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

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def create_task(audio_file_name):
    url = "https://aip.baidubce.com/rpc/2.0/aasr/v1/create?access_token=" + get_access_token()
    payload = json.dumps({
        "speech_url": f"http://129.114.24.200:8001/audio/{audio_file_name}",
        "format": "m4a",
        "pid": 1737,
        "rate": 16000
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    return response_json.get("task_id")

def get_res(task_id):
    url = "https://aip.baidubce.com/rpc/2.0/aasr/v1/query?access_token=" + get_access_token()
    payload = json.dumps({
        "task_ids": [task_id]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

def check_task_status(task_id, max_attempts=10, delay=1):
    for attempt in range(max_attempts):
        response = get_res(task_id)
        print(f"Attempt {attempt + 1}: Checking task status...")
        if response.get("tasks_info"):
            task_status = response["tasks_info"][0]["task_status"]
            print(f"Current status: {task_status}")
            if task_status == "Success":
                return response["tasks_info"][0]["task_result"]
            elif task_status == "Failed":
                print("Task failed.")
                return None
        time.sleep(delay)
    print("Max attempts reached. Task not completed.")
    return None

async def convert_audio_to_text(file_path):
    # Extract just the filename from the full path
    audio_file_name = os.path.basename(file_path)
    
    task_id = create_task(audio_file_name)
    if task_id:
        print(f"Task created with ID: {task_id}")
        result = check_task_status(task_id)
        if result and "result" in result:
            return result["result"][0]
        else:
            print("Failed to get result from task.")
            return None
    else:
        print("Failed to create task.")
        return None

# If you need to test the function independently:
if __name__ == '__main__':
    import asyncio
    
    async def test():
        text = await convert_audio_to_text("path/to/your/audio/file.m4a")
        if text:
            print("Converted text:", text)
        else:
            print("Conversion failed.")

    asyncio.run(test())