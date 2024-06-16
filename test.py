import requests

def test_generate_audio():
    url = "http://localhost:8000/generate_audio/"

    text = "Hello, this is a test."
    language = "en"
    speed = 1.0

    # Assuming you have a sample speaker_wav file called 'sample.wav' in the current directory
    speaker_wav_path = "speakers/qhy-0.wav"

    with open(speaker_wav_path, "rb") as speaker_wav_file:
        files = {'speaker_wav': ('sample.wav', speaker_wav_file, 'audio/wav')}
        data = {'text': text, 'language': language, 'speed': speed}
        response = requests.post(url, data=data, files=files)

    if response.status_code == 200:
        output_path = "test_output.wav"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Audio file saved to {output_path}")
    else:
        print(f"Failed to generate audio. Status code: {response.status_code}")
        print(f"Response: {response.text}")


def test_generate_audio_with_srt():
    url = "http://localhost:8010/generate_audio_with_srt"

    language = "en"
    speed = 1.0

    # Paths to your test SRT file and reference audio (or video)
    srt_file_path = "temp/test1.srt"
    ref_audio_path = "temp/test.wav"  # This can be an audio file or a video file

    with open(srt_file_path, "rb") as srt_file, open(ref_audio_path, "rb") as ref_audio_file:
        files = {
            'srt_file': ('test.srt', srt_file, 'text/plain'),
            'ref_audio': ('test_video.wav', ref_audio_file, 'audio/wav'),  # Change MIME type if using an audio file
        }
        data = {'language': language, 'speed': speed}

        response = requests.post(url, data=data, files=files)

    if response.status_code == 200:
        output_path = "test_output.wav"
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Audio file saved to {output_path}")
    else:
        print(f"Failed to generate audio. Status code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_generate_audio_with_srt()
