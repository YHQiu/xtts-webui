import os.path
import uuid
from pathlib import Path

import srt
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
from fastapi.responses import FileResponse
from pydub import AudioSegment
from moviepy.editor import VideoFileClip

from scripts.funcs import resemble_enhance_audio
from scripts.tts_funcs import TTSWrapper

app = FastAPI()
api = TTSWrapper()
os.makedirs("output", exist_ok=True)
this_dir = Path(__file__).parent.resolve()

@app.post("/generate_audio/")
async def generate_audio(
        text: str = Form(...),
        speaker_wav: UploadFile = File(...),
        language: str = Form(...),
        speed: Optional[float] = Form(1.0),
):
    api.load_local_model(this_dir)

    output_file = os.path.join("output", f"{uuid.uuid4()}_output.wav")  # 你可以根据需要修改输出文件名
    options = {"speed": speed, "temperature": 0.85, "length_penalty": 1.0, "repetition_penalty": 5.0,
    "top_k": 50,
    "top_p": 0.85,}
    speaker_wav_path = f"temp/{uuid.uuid4()}{speaker_wav.filename}"  # 保存上传的说话者音频文件
    with open(speaker_wav_path, "wb") as f:
        f.write(await speaker_wav.read())

    api.local_generation(this_dir, text=text, ref_speaker_wav=None, speaker_wav=speaker_wav_path, language=language, options=options,
                             output_file=output_file)

    return FileResponse(output_file, media_type='audio/wav')


def save_temp_file(upload_file: UploadFile, extension: str):
    temp_file_path = f"temp/{uuid.uuid4()}.{extension}"
    with open(temp_file_path, "wb") as f:
        f.write(upload_file.file.read())
    return temp_file_path


def extract_audio_from_video(video_path: str) -> str:
    video_clip = VideoFileClip(video_path)
    audio_path = video_path.rsplit('.', 1)[0] + ".wav"
    video_clip.audio.write_audiofile(audio_path)
    return audio_path


@app.post("/generate_audio_with_srt/")
async def generate_audio_with_srt(
        srt_file: UploadFile = File(...),
        ref_audio: UploadFile = File(...),
        language: str = Form(...),
        speed: Optional[float] = Form(1.0),
):
    api.load_local_model(this_dir)

    # Save the uploaded reference audio/video to a temporary file
    ref_audio_path = save_temp_file(ref_audio, ref_audio.filename.split('.')[-1])

    # Check if the reference audio is a video file and extract audio if necessary
    if ref_audio.filename.lower().endswith(('mp4', 'mkv', 'avi', 'mov', 'flv', 'wmv')):
        ref_audio_path = extract_audio_from_video(ref_audio_path)

    # Read and parse the SRT file
    srt_content = (await srt_file.read()).decode("utf-8")
    srt_segments = list(srt.parse(srt_content))
    ref_audio_segment = AudioSegment.from_file(ref_audio_path)

    output_segments = []
    work_space = os.path.join("temp", f"{uuid.uuid4()}")
    os.makedirs(work_space, exist_ok=True)

    for segment in srt_segments:
        start_time = (segment.start.total_seconds()) * 1000  # Convert to milliseconds
        end_time = (segment.end.total_seconds() ) * 1000  # Convert to milliseconds
        duration = end_time - start_time

        segment_audio = ref_audio_segment[start_time:end_time]

        # Loop the reference audio segment to be at least 1.5 seconds long if it is shorter
        min_duration = 750  # 1.5 seconds in milliseconds
        while len(segment_audio) < min_duration:
            segment_audio += segment_audio

        temp_speaker_wav_path = f"{work_space}/{uuid.uuid4()}{start_time}-{end_time}_segment.wav"
        segment_audio.export(temp_speaker_wav_path, format="wav")
        uuid_path = f"{uuid.uuid4()}"
        output_file = f"{work_space}/{uuid_path}_0_output.wav"
        options = {"speed": speed, "temperature": 0.85, "length_penalty": 1.0, "repetition_penalty": 5.0,
                   "top_k": 50, "top_p": 0.85}

        api.local_generation(this_dir, text=segment.content, ref_speaker_wav=temp_speaker_wav_path, speaker_wav=temp_speaker_wav_path,
                             language=language, options=options, output_file=output_file)

        generated_audio = AudioSegment.from_file(output_file)

        # max_test = 2
        # audio_map = {}
        # audio_map[len(generated_audio)] = 0
        # min_duration = len((generated_audio))
        # while(len(generated_audio) > duration):
        #     output_file = f"{work_space}/{uuid_path}_{max_test}_output.wav"
        #     api.local_generation(this_dir, text=segment.content, ref_speaker_wav=temp_speaker_wav_path,
        #                          speaker_wav=temp_speaker_wav_path,
        #                          language=language, options=options, output_file=output_file)
        #     generated_audio = AudioSegment.from_file(output_file)
        #     min_duration = len((generated_audio))
        #     audio_map[len(generated_audio)] = max_test
        #     max_test -= 1
        #     if max_test == 0:
        #         break
        #
        # if max_test == 0:
        #     output_file = f"{work_space}/{uuid_path}_{audio_map[min_duration]}_output.wav"
        #     generated_audio = AudioSegment.from_file(output_file)

        if len(generated_audio) > duration:
            generated_audio = generated_audio.speedup(playback_speed=(len(generated_audio) / duration))

        padded_audio = AudioSegment.silent(duration=duration)
        padded_audio = padded_audio.overlay(generated_audio)

        output_segments.append((start_time, padded_audio))

    final_output = AudioSegment.silent(duration=len(ref_audio_segment))

    for start_time, segment_audio in output_segments:
        final_output = final_output.overlay(segment_audio, position=start_time)

    final_output_path = os.path.join("output", f"{uuid.uuid4()}_final_output.wav")
    final_output.export(final_output_path, format="wav")

    resemble_enhance_settings = {
        "chunk_seconds": 8,
        "chunks_overlap": 1,
        "solver": 'Midpoint',
        "nfe": 64,
        "tau": 0.5,
        "denoising": True,
        "use_enhance": False
    }
    output_file = resemble_enhance_audio(
        **resemble_enhance_settings, audio_path=final_output_path, output_type="wav")[0]

    return FileResponse(final_output_path, media_type='audio/wav')

def start_app():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_app()