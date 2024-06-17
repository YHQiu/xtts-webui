import ffmpeg

def get_audio_duration(audio_path):
    """ 获取音频文件的时长 """
    try:
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['streams'][0]['duration'])
        return duration
    except Exception as e:
        print(f"Error getting duration of {audio_path}: {str(e)}")
        return 0

def adjust_audio_speed(input_path, output_path, speed):
    current_duration = get_audio_duration(input_path)
    if current_duration == 0:
        return

    # 计算所需的总速度调整
    target_duration = int(current_duration*speed)
    total_adjustment = round(current_duration / target_duration, 2)

    if total_adjustment >= 100:
        total_adjustment = 50

    # 创建ffmpeg的输入
    audio_input = ffmpeg.input(input_path)

    # 当总调整小于0.5时，分解成多个步骤
    while total_adjustment < 0.5:
        audio_input = audio_input.filter('atempo', '0.5')
        total_adjustment /= 0.5
        total_adjustment = round(total_adjustment, 2)

    # 添加最后一步的调整
    audio_input = audio_input.filter('atempo', str(total_adjustment))

    # 应用ffmpeg过滤器链并输出文件
    audio_input.output(output_path).run(overwrite_output=True)

    return output_path