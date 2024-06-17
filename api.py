import datetime
import json
import os
import uuid
from pathlib import Path

import loguru
import srt
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
from fastapi.responses import FileResponse
from pydub import AudioSegment
from moviepy.editor import VideoFileClip

from scripts import config
from scripts.config import get_speed_refactor
from scripts.funcs import resemble_enhance_audio
from scripts.tts_funcs import TTSWrapper
from scripts.utils.wavhandle import wav_speedup

app = FastAPI()
api = TTSWrapper()
os.makedirs("output", exist_ok=True)
this_dir = Path(__file__).parent.resolve()
temp_root_dir = this_dir
logger = loguru.logger
# 生成次数
gen_count = 1

@app.post("/generate_audio/")
async def generate_audio(
        text: str = Form(...),
        speaker_wav: UploadFile = File(...),
        language: str = Form(...),
        speed: Optional[float] = Form(1.0),
):
    api.load_local_model(this_dir)

    output_file = os.path.join("output", f"{uuid.uuid4()}_output.wav")
    options = {"speed": speed, "temperature": 0.85, "length_penalty": 1.0, "repetition_penalty": 5.0,
               "top_k": 50, "top_p": 0.85}
    speaker_wav_path = f"temp/{uuid.uuid4()}{speaker_wav.filename}"
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


@app.post("/generate_audio_with_srt")
async def generate_audio_with_srt(
        srt_file: Optional[UploadFile] = File(None),
        ref_audio: UploadFile = File(...),
        json_text: Optional[str] = Form(None),
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
    if srt_file is not None:
        srt_content = (await srt_file.read()).decode("utf-8")
        srt_segments = list(srt.parse(srt_content))
    elif json_text is not None:
        json_data = json.dumps(json_text, indent=4, ensure_ascii=False)
        print(f"json_data is{json_data}")
        srt_segments = [
            srt.Subtitle(
                index=index,
                start=datetime.timedelta(
                    hours=int(seg['start_time'].split(':')[0]),
                    minutes=int(seg['start_time'].split(':')[1]),
                    seconds=int(seg['start_time'].split(':')[2].split(',')[0]),
                    milliseconds=int(seg['start_time'].split(',')[1])
                ),
                end=datetime.timedelta(
                    hours=int(seg['end_time'].split(':')[0]),
                    minutes=int(seg['end_time'].split(':')[1]),
                    seconds=int(seg['end_time'].split(':')[2].split(',')[0]),
                    milliseconds=int(seg['end_time'].split(',')[1])
                ),
                content=seg['text']
            )
            for index, seg in enumerate(json_data)
        ]
    else:
        raise ValueError("Either srt_file or json_text must be provided.")

    ref_audio_segment = AudioSegment.from_file(ref_audio_path)

    output_segments = []
    work_space = os.path.join(temp_root_dir, "temp", f"{uuid.uuid4()}")
    os.makedirs(work_space, exist_ok=True)

    # 时长调整因子
    duration_refactor = 1.0/config.get_speed_refactor(src_language=None, target_language=language)

    for segment in srt_segments:
        start_time = (segment.start.total_seconds()) * 1000  # Convert to milliseconds
        end_time = (segment.end.total_seconds()) * 1000  # Convert to milliseconds
        duration = end_time - start_time

        segment_audio = ref_audio_segment[start_time:end_time]

        # Loop the reference audio segment to be at least 1.5 seconds long if it is shorter
        min_duration = 500  # 1.5 seconds in milliseconds
        while len(segment_audio) < min_duration:
            segment_audio += segment_audio

        temp_speaker_wav_path = f"{work_space}/{start_time}-{end_time}_segment.wav"
        segment_audio.export(temp_speaker_wav_path, format="wav")
        test_options = {"speed": speed, "temperature": 0.75, "length_penalty": 1.0, "repetition_penalty": 5.0,
                   "top_k": 60, "top_p": 0.75}

        # 最大测试次数
        max_test = gen_count

        test_audio_map = {}
        best_test_duration = None
        while max_test > 0:
            test_output_file = f"{work_space}/{start_time}_{end_time}_{max_test}_test_output.wav"
            api.process_tts_to_file(this_dir, text=segment.content, ref_speaker_wav=temp_speaker_wav_path,
                                    language=language, options=test_options, file_name_or_path=test_output_file)
            generated_audio = AudioSegment.from_file(test_output_file)
            if best_test_duration is None:
                best_test_duration = len(generated_audio)
            elif best_test_duration > len(generated_audio):
                best_test_duration = len(generated_audio)
            test_audio_map[len(generated_audio)] = max_test
            max_test -= 1
            if max_test == 0:
                break
        test_output_file = f"{work_space}/{start_time}_{end_time}_{test_audio_map[best_test_duration]}_test_output.wav"

        gen_options = {"speed": speed, "temperature": 0.85, "length_penalty": 1.0, "repetition_penalty": 5.0,
                        "top_k": 50, "top_p": 0.85}

        # 最大生成次数
        max_gen = gen_count

        audio_map = {}
        best_gen_duration = None
        while max_gen > 0:
            output_file = f"{work_space}/{start_time}_{end_time}_{max_gen}_gen_output.wav"
            api.process_tts_to_file(this_dir, text=segment.content, ref_speaker_wav=test_output_file,
                                    language=language, options=gen_options, file_name_or_path=output_file)
            generated_audio = AudioSegment.from_file(output_file)
            if best_gen_duration is None:
                best_gen_duration = len(generated_audio)
            elif best_gen_duration > len(generated_audio):
                best_gen_duration = len(generated_audio)
            audio_map[len(generated_audio)] = max_gen
            max_gen -= 1
            if max_gen == 0:
                break

        output_file = f"{work_space}/{start_time}_{end_time}_{audio_map[best_gen_duration]}_gen_output.wav"
        generated_audio = AudioSegment.from_file(output_file)

        # if len(generated_audio) > int(duration*duration_refactor):
        # Calculate playback speed
        generated_duration = len(generated_audio)
        logger.info(f"generated_duration is {generated_duration}")

        start_time = int(start_time * duration_refactor)
        duration = int(duration * duration_refactor)
        playback_speed = (generated_duration / duration)

        # Ensure playback_speed is within reasonable bounds
        if playback_speed < 1.0:
            playback_speed = 1.0
        elif playback_speed > 2.0:
            playback_speed = 2.0

        print(f"playback_speed={playback_speed}")
        generated_audio = wav_speedup(generated_audio, playback_speed=playback_speed)

        padded_audio = AudioSegment.silent(duration=duration, frame_rate=24000)
        padded_audio = padded_audio.overlay(generated_audio)

        output_segments.append((int(start_time), padded_audio))

    final_output = AudioSegment.silent(duration=int(len(ref_audio_segment)*duration_refactor), frame_rate=24000)

    for start_time, segment_audio in output_segments:
        final_output = final_output.overlay(segment_audio, position=start_time)

    final_output_path = os.path.join("output", f"{uuid.uuid4()}_final_output.wav")
    final_output.export(final_output_path, format="wav")

    return FileResponse(final_output_path, media_type='audio/wav')


def start_app():
    uvicorn.run(app, host="0.0.0.0", port=8010)


if __name__ == "__main__":
    start_app()
