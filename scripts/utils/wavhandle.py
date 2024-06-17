import librosa
import soundfile as sf
import numpy as np
from scipy.stats import norm
from pydub import AudioSegment

from scripts.utils import ffmpeg_tools


def remove_silence(input_file, output_file, confidence_level=0.95):
    """
    Remove low energy segments from a WAV file.

    Args:
        input_file (str): Path to the input WAV file.
        output_file (str): Path to save the processed WAV file.
        confidence_level (float): Confidence level for determining energy threshold.
                                   Defaults to 0.95.

    Returns:
        None
    """
    # Load audio file
    y, sr = librosa.load(input_file, sr=None)

    # Calculate the root mean square (RMS) energy of the audio signal
    rms = librosa.feature.rms(y=y)[0]

    # Calculate energy threshold using confidence level
    # energy_threshold = norm.ppf(confidence_level, loc=mean, scale=std)
    energy_threshold = 0.020

    # Create mask for high energy segments
    high_energy_mask = rms >= energy_threshold

    # Find the start and end indices of high energy segments
    segment_indices = []
    start_idx = None
    for i, value in enumerate(high_energy_mask):
        if value and start_idx is None:
            start_idx = i
        elif not value and start_idx is not None:
            segment_indices.append((start_idx, i))
            start_idx = None
    if start_idx is not None:
        segment_indices.append((start_idx, len(high_energy_mask)))

    # Concatenate high energy segments
    trimmed_audio = np.concatenate([y[start * len(y)//len(rms):end * len(y)//len(rms)] for start, end in segment_indices])

    # Save processed audio using soundfile
    sf.write(output_file, trimmed_audio, sr)

    return output_file

def wav_speedup(audio, playback_speed, output_file_path=None, sample_rate =24000):
    ffmpeg_tools.adjust_audio_speed(audio, output_file_path, playback_speed)
    return output_file_path

if __name__ == "__main__":
    # Example usage
    input_file_path = 'test_2.wav'
    output_file_path = 'test_handle.wav'

    # wav_speedup(input_file_path, playback_speed=1.0044444444444445, output_file_path=output_file_path)
    wav_speedup(input_file_path, playback_speed=1.0044444444444445, output_file_path=output_file_path)

    # remove_silence(input_file_path, output_file_path)
