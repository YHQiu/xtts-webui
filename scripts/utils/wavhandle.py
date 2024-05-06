import librosa
import soundfile as sf
import numpy as np

def overlap_add(signal_frames, frame_length, hop_length):
    """
    Perform overlap-add method to reconstruct signal from frames.

    Args:
        signal_frames (np.ndarray): 2D array of signal frames.
        frame_length (int): Length of each frame.
        hop_length (int): Hop length (frame shift).

    Returns:
        np.ndarray: Reconstructed signal.
    """
    num_frames = signal_frames.shape[0]
    signal_length = (num_frames - 1) * hop_length + frame_length
    reconstructed_signal = np.zeros(signal_length)

    for i in range(num_frames):
        start_index = i * hop_length
        end_index = start_index + frame_length
        reconstructed_signal[start_index:end_index] += signal_frames[i]

    return reconstructed_signal

def remove_silence(input_file, output_file, energy_threshold=1.0):
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

    # Reconstruct signal using overlap-add method
    frame_length = 512  # You can adjust this according to your needs
    hop_length = 256  # You can adjust this according to your needs
    signal_frames = librosa.util.frame(trimmed_audio, frame_length=frame_length, hop_length=hop_length).T
    reconstructed_audio = overlap_add(signal_frames, frame_length, hop_length)

    # Check if the reconstructed audio length is less than original audio length
    if len(reconstructed_audio) >= len(y):
        print("Error: Reconstructed audio length is not less than original audio length.")
        return

    # Save processed audio using soundfile
    sf.write(output_file, reconstructed_audio, sr)

    return output_file

if __name__ == "__main__":
    # 使用示例
    input_file_path = 'test_3.wav'
    output_file_path = 'test_handle.wav'
    remove_silence(input_file_path, output_file_path)
