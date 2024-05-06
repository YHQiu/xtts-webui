import librosa
import soundfile as sf
import numpy as np

def remove_silence(input_file, output_file, energy_threshold=0.1):
    """
    Remove silence or low energy segments from a WAV file.

    Args:
        input_file (str): Path to the input WAV file.
        output_file (str): Path to save the processed WAV file.
        energy_threshold (float): Energy threshold to determine silence segments.
                                  Defaults to 0.001.

    Returns:
        None
    """
    # Load audio file
    y, sr = librosa.load(input_file, sr=None)

    # Calculate short-time Fourier transform
    D = librosa.stft(y)

    # Calculate energy for each time window
    energy = np.sum(np.abs(D) ** 2, axis=0)

    # Create mask for silence segments
    silence_mask = energy < energy_threshold

    # Repeat the mask for each frame in the STFT
    silence_mask = np.repeat(silence_mask, np.ceil(len(y) / len(silence_mask)))

    # Remove silence segments
    trimmed_audio = y[np.logical_not(silence_mask[:len(y)])]

    # Check if the trimmed audio length is less than original audio length
    print(len(trimmed_audio))
    print(len(y))
    if len(trimmed_audio) >= len(y):
        print("Error: Trimmed audio length is not less than original audio length.")
        return

    # Save processed audio
    # Save processed audio using soundfile
    sf.write(output_file, trimmed_audio, sr)

    return output_file

if __name__ == "__main__":
    # 使用示例
    input_file_path = 'test_3.wav'
    output_file_path = 'test_handle.wav'
    remove_silence(input_file_path, output_file_path)
