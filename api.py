import os.path
import uuid

from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
from fastapi.responses import FileResponse
from scripts.tts_funcs import TTSWrapper

app = FastAPI()
api = TTSWrapper()
os.makedirs("output", exist_ok=True)

@app.post("/generate_audio/")
async def generate_audio(
        text: str = Form(...),
        speaker_wav: UploadFile = File(...),
        language: str = Form(...),
        speed: Optional[float] = Form(1.0),
):
    output_file = os.path.join("output", f"{uuid.uuid4()}_output.wav")  # 你可以根据需要修改输出文件名
    options = {"speed": speed}
    speaker_wav_path = f"temp/{uuid.uuid4()}{speaker_wav.filename}"  # 保存上传的说话者音频文件
    with open(speaker_wav_path, "wb") as f:
        f.write(await speaker_wav.read())

    api.api_generation(text=text, speaker_wav=speaker_wav_path, language=language, options=options,
                             output_file=output_file)

    return FileResponse(output_file, media_type='audio/wav')
