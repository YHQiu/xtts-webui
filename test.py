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
    url = "http://localhost:9880/generate_audio_with_srt"

    language = "en"
    speed = 1.15

    # Paths to your test SRT file and reference audio (or video)
    srt_file_path = "temp/11.srt"
    ref_audio_path = "temp/test.wav"  # This can be an audio file or a video file

    with open(srt_file_path, "rb") as srt_file, open(ref_audio_path, "rb") as ref_audio_file:
        files = {
            # 'srt_file': ('test.srt', srt_file, 'text/plain'),
            'ref_audio': ('test_video.wav', ref_audio_file, 'audio/wav'),  # Change MIME type if using an audio file
        }
        data = {'language': language, 'speed': speed, 'json_text': """[{'id': 1, 'start_time': '0:00:02.240000', 'end_time': '0:00:03.238000', 'text': 'It has nothing to do with you'}, {'id': 2, 'start_time': '0:00:03.359000', 'end_time': '0:00:04.479000', 'text': 'Let me say it again'}, {'id': 3, 'start_time': '0:00:04.480000', 'end_time': '0:00:05.759000', 'text': 'You are my party'}, {'id': 4, 'start_time': '0:00:05.799000', 'end_time': '0:00:07.639000', 'text': 'All your matters are related to me'}, {'id': 5, 'start_time': '0:00:07.639000', 'end_time': '0:00:09.519000', 'text': 'Then I can only consider changing law firm'}, {'id': 6, 'start_time': '0:00:09.800000', 'end_time': '0:00:10.759000', 'text': "Couldn't ask for more"}, {'id': 7, 'start_time': '0:00:10.880000', 'end_time': '0:00:11.958000', 'text': 'Then I just happen to let you'}, {'id': 8, 'start_time': '0:00:11.960000', 'end_time': '0:00:12.878000', 'text': 'Lose more thoroughly'}, {'id': 9, 'start_time': '0:00:13.839000', 'end_time': '0:00:15.198000', 'text': 'Since you have concealed something from me'}, {'id': 10, 'start_time': '0:00:15.320000', 'end_time': '0:00:17.079000', 'text': 'I also have the right to terminate your power of attorney'}, {'id': 11, 'start_time': '0:00:17.600000', 'end_time': '0:00:18.719000', 'text': 'Why'}, {'id': 12, 'start_time': '0:00:18.719000', 'end_time': '0:00:20.919000', 'text': 'Are you all forcing me'}, {'id': 13, 'start_time': '0:00:21.719000', 'end_time': '0:00:23.638000', 'text': 'What did I do wrong'}, {'id': 14, 'start_time': '0:00:25', 'end_time': '0:00:25.814000', 'text': 'Are you okay?'}, {'id': 15, 'start_time': '0:00:25.814000', 'end_time': '0:00:26.879000', 'text': 'Drink some water'}, {'id': 16, 'start_time': '0:00:26.960000', 'end_time': '0:00:28.559000', 'text': 'What should we do about Tang Lu'}, {'id': 17, 'start_time': '0:00:29.839000', 'end_time': '0:00:31.039000', 'text': 'Me'}, {'id': 18, 'start_time': '0:00:35.520000', 'end_time': '0:00:36.239000', 'text': 'Hello,'}, {'id': 19, 'start_time': '0:00:36.239000', 'end_time': '0:00:36.838000', 'text': '120?'}, {'id': 20, 'start_time': '0:00:36.960000', 'end_time': '0:00:38.518000', 'text': "There's someone who needs emergency help"}, {'id': 21, 'start_time': '0:00:41.960000', 'end_time': '0:00:43.279000', 'text': 'Family members are not allowed to enter'}, {'id': 22, 'start_time': '0:00:43.439000', 'end_time': '0:00:44.598000', 'text': 'What if something happens to her'}, {'id': 23, 'start_time': '0:00:44.719000', 'end_time': '0:00:45.639000', 'text': 'Will you be implicated?'}, {'id': 24, 'start_time': '0:00:45.759000', 'end_time': '0:00:46.518000', 'text': "She's fine."}, {'id': 25, 'start_time': '0:00:47.200000', 'end_time': '0:00:47.918000', 'text': 'Fake.'}, {'id': 26, 'start_time': '0:00:48', 'end_time': '0:00:48.838000', 'text': 'How do you know?'}, {'id': 27, 'start_time': '0:00:49', 'end_time': '0:00:50.759000', 'text': 'Did you see those injuries on her body?'}, {'id': 28, 'start_time': '0:00:51.079000', 'end_time': '0:00:52.558000', 'text': "That's not caused by self-harm at all."}, {'id': 29, 'start_time': '0:00:53.240000', 'end_time': '0:00:54.198000', 'text': 'Got beaten up.'}, {'id': 30, 'start_time': '0:00:54.200000', 'end_time': '0:00:55.639000', 'text': 'You speak so implicitly.'}, {'id': 31, 'start_time': '0:00:55.640000', 'end_time': '0:00:57.079000', 'text': 'If my guess is correct,'}, {'id': 32, 'start_time': '0:00:57.320000', 'end_time': '0:00:58.759000', 'text': 'It should be done by Cui Yan.'}]
"""}

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
