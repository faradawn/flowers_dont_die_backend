import whisper
import os

model = whisper.load_model("tiny.en")
print("whisper ai model loaded: tiny.en")

def whisper_transcribe(audio_file_name):
    # AUDIO_FOLDER = "/home/cc/audio_submissions"
    # file_path = os.path.join(AUDIO_FOLDER, f"{audio_file_name}.m4a")
    result = model.transcribe(audio_file_name)
    return result["text"]