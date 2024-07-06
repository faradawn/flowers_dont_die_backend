from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from typing import Dict, List, Optional
import httpx
import random
import os
import requests
import hashlib
import base64
import json
import hmac
import time
from time import mktime
from datetime import datetime
from urllib.parse import urlencode
import ssl
import threading
import websocket
from wsgiref.handlers import format_date_time
from pydub import AudioSegment

router = APIRouter()

STATUS_FIRST_FRAME = 0  # The identity of the first frame
STATUS_CONTINUE_FRAME = 1  # Intermediate frame identification
STATUS_LAST_FRAME = 2  # The identity of the last frame

class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {"domain": "iat", "language": "en_us", "accent": "", "vinfo": 1, "vad_eos": 10000}

    def create_url(self):
        url = 'wss://iat-api-sg.xf-yun.com/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = f"host: iat-api-sg.xf-yun.com\ndate: {date}\nGET /v2/iat HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'), hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode('utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": "iat-api-sg.xf-yun.com"
        }
        url = url + '?' + urlencode(v)
        return url

transcription_result = []

def on_message(ws, message):
    global transcription_result
    try:
        data = json.loads(message)["data"]["result"]["ws"]
        for i in data:
            for w in i["cw"]:
                transcription_result.append(w["w"])
    except Exception as e:
        print("receive msg, but parse exception:", e)

def on_error(ws, error):
    print("### error:", error)

def on_close(ws, close_status_code, close_msg):
    print(f"### closed ### code: {close_status_code}, message: {close_msg}")
    global transcription_result
    print("Final transcription: ", " ".join(transcription_result))

def on_open(ws, wsParam):
    def run(*args):
        frameSize = 8000  # The size of each frame to send
        interval = 0.04   # Interval between frames (in seconds)
        status = STATUS_FIRST_FRAME

        with open(wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                if not buf:
                    status = STATUS_LAST_FRAME

                if status == STATUS_FIRST_FRAME:
                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    status = STATUS_CONTINUE_FRAME
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                time.sleep(interval)
        ws.close()

    threading.Thread(target=run).start()

@router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    global transcription_result
    transcription_result = []
    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        audio = AudioSegment.from_file(file_location)
        wav_file_location = file_location.replace(".mp3", ".wav")
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_file_location, format="wav")

        APPID = "ga401c82"
        API_KEY = "faee560d6949cb096f31c7d62bf78fe3"
        API_SECRET = "773bfcdf533aec7e74d70d325fb7fe14"
        wsParam = Ws_Param(APPID, API_KEY, API_SECRET, wav_file_location)

        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = lambda ws: on_open(ws, wsParam)
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        return {"status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while uploading the file: {str(e)}")

@router.get("/get-transcription/")
async def get_transcription():
    global transcription_result
    return {"transcription": " ".join(transcription_result)}