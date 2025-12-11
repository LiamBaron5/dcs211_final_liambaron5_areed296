import os
import librosa
import numpy as np

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
# Change this path if your audio folder is elsewhere
AUDIO_FOLDER = "audio_files"


# ------------------------------------------------------------
# TEMPO DETECTION
# ------------------------------------------------------------
def get_tempo(y, sr):
    """
    Estimates tempo (beats per minute) using librosa's beat tracker.
    """
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return float(tempo)


# ------------------------------------------------------------
# KEY ESTIMATION (simple method)
# ------------------------------------------------------------
def get_key(y, sr):
    """
    Estimates the key by calculating the chroma and finding
    the most dominant pitch class.

    NOTE:
    - This is a simplified approach.
    - It detects the dominant pitch but does NOT determine major/minor scale.
    """

    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)

    pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F',
                     'F#', 'G', 'G#', 'A', 'A#', 'B']

    key_index = int(np.argmax(chroma_mean))
    return pitch_classes[key_index]


# ------------------------------------------------------------
# LIST FILES IN THE AUDIO DIRECTORY
# ------------------------------------------------------------
def list_audio_files(folder):
    """
    Lists all .mp3 and .wav files in the given folder.
    Returns a list of filenames.
    """

    supported = (".mp3", ".wav")
    files = [f for f in os.listdir(folder) if f.lower().endswith(supported)]
    return sorted(files)


# ------------------------------------------------------------
# MAIN PROGRAM LOGIC
# ------------------------------------------------------------
def main():
    print(f"\n🔍 Scanning folder: {AUDIO_FOLDER}\n")

    files = list_audio_files(AUDIO_FOLDER)

    if not files:
        print("⚠️  No audio files found in the folder!")
        print("Make sure you place .mp3 or .wav files inside the 'audio_files' directory.")
        return

    # Display files
    print("Available audio files:")
    for idx, filename in enumerate(files, 1):
        print(f"{idx}. {filename}")

    # Ask the user to choose one
    choice = int(input("\nEnter the number of the file you want to analyze: "))

    if choice < 1 or choice > len(files):
        print("❌ Invalid selection.")
        return

    selected_file = files[choice - 1]
    file_path = os.path.join(AUDIO_FOLDER, selected_file)

    print(f"\n📂 Loading: {selected_file}\n")

    # Load audio
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
    except Exception as e:
        print("❌ Error loading audio file:", e)
        return

    # Analyze
    tempo = get_tempo(y, sr)
    key = get_key(y, sr)

    # Output results
    print("🎵 --- Analysis Results ---")
    print(f"File: {selected_file}")
    print(f"Tempo (BPM): {round(tempo, 2)}")
    print(f"Estimated Key: {key}")
    print("---------------------------\n")


# ------------------------------------------------------------
# PROGRAM ENTRY POINT
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
