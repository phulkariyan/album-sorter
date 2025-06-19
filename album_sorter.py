



import os
import shutil
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wavpack import WavPack
from mutagen.aiff import AIFF
from mutagen.mp4 import MP4
from mutagen.m4a import M4A
from mutagen.apev2 import APEv2
from mutagen.id3 import ID3NoHeaderError

def get_audio_duration(filepath):
    try:
        if filepath.lower().endswith('.mp3'):
            audio = MP3(filepath)
        elif filepath.lower().endswith('.flac'):
            audio = FLAC(filepath)
        elif filepath.lower().endswith('.ogg'):
            audio = OggVorbis(filepath)
        elif filepath.lower().endswith('.wav'):
            return None
        elif filepath.lower().endswith(('.m4a', '.mp4')):
            audio = MP4(filepath)
        elif filepath.lower().endswith('.aiff'):
            audio = AIFF(filepath)
        elif filepath.lower().endswith('.wv'):
            audio = WavPack(filepath)
        elif filepath.lower().endswith('.ape'):
            audio = APEv2(filepath)
        else:
            return None

        return audio.info.length
    except ID3NoHeaderError:
        try:
            from mutagen.mp3 import Header
            header = Header(filepath)
            if header:
                return header.length
            return None
        except Exception:
            return None
    except Exception as e:
        return None

def reorder_album(directory_path, sort_criterion='alphabetical', reverse=False,
                  file_extensions=('.mp3', '.flac', '.wav', '.ogg', '.m4a', '.mp4', '.aiff', '.wv', '.ape')):
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' not found.")
        return

    print(f"Processing directory: {directory_path}")

    audio_files_with_paths = []
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if os.path.isfile(filepath) and any(filename.lower().endswith(ext) for ext in file_extensions):
            audio_files_with_paths.append((filename, filepath))

    if not audio_files_with_paths:
        print("No audio files found with the specified extensions in this directory.")
        return

    print(f"Found {len(audio_files_with_paths)} audio files.")

    if sort_criterion == 'alphabetical':
        print("Sorting by alphabetical order (forward)...")
        audio_files_with_paths.sort(key=lambda item: os.path.splitext(item[0])[0].lower(), reverse=reverse)
    elif sort_criterion == 'reverse_alphabetical':
        print("Sorting by reverse alphabetical order...")
        audio_files_with_paths.sort(key=lambda item: os.path.splitext(item[0])[0].lower(), reverse=True)
    elif sort_criterion == 'duration':
        print("Sorting by duration...")
        files_with_duration = []
        for filename, filepath in audio_files_with_paths:
            duration = get_audio_duration(filepath)
            if duration is not None:
                files_with_duration.append((filename, filepath, duration))
            else:
                print(f"Skipping '{filename}' for duration sort as duration could not be determined.")

        if not files_with_duration:
            print("No files with readable duration found. Cannot sort by duration.")
            return

        files_with_duration.sort(key=lambda item: item[2], reverse=reverse)
        audio_files_with_paths = [(item[0], item[1]) for item in files_with_duration]

    else:
        print(f"Error: Unknown sort criterion '{sort_criterion}'.")
        return

    temp_dir = os.path.join(directory_path, "temp_reorder_album")
    os.makedirs(temp_dir, exist_ok=True)
    print(f"Created temporary directory: {temp_dir}")

    for i, (original_filename, original_filepath) in enumerate(audio_files_with_paths):
        file_name_without_ext, file_extension = os.path.splitext(original_filename)

        new_filename = f"Track {i+1:02d} - {file_name_without_ext}{file_extension}"
        new_temp_path = os.path.join(temp_dir, new_filename)

        print(f"Renaming '{original_filename}' to '{new_filename}'")
        try:
            shutil.move(original_filepath, new_temp_path)
        except Exception as e:
            print(f"Error moving file '{original_filename}': {e}")
            shutil.rmtree(temp_dir)
            return

    print("Moving reordered files back to original directory...")
    for filename in os.listdir(temp_dir):
        shutil.move(os.path.join(temp_dir, filename), os.path.join(directory_path, filename))

    shutil.rmtree(temp_dir)
    print("Reordering complete. Temporary directory removed.")
    print("\nIMPORTANT: You may need to refresh your music player's library for changes to reflect.")

if __name__ == "__main__":
    album_path = "C:\\Users\\yourusername\\Music\\TestAlbum"

    if not os.path.exists(album_path):
        os.makedirs(album_path)
        print(f"Created dummy directory: {album_path}")
        with open(os.path.join(album_path, "Zebra Song.mp3"), "w") as f: f.write("a" * 1000)
        with open(os.path.join(album_path, "Apple Tune.mp3"), "w") as f: f.write("a" * 5000)
        with open(os.path.join(album_path, "Banana Beat.flac"), "w") as f: f.write("a" * 2000)
        with open(os.path.join(album_path, "Cat's Cradle.wav"), "w") as f: f.write("a" * 3000)
        with open(os.path.join(album_path, "Doggy Day.ogg"), "w") as f: f.write("a" * 1500)
        print("Created dummy audio files for testing (their 'duration' will be based on byte size, not actual audio length).")
        print("For accurate duration sorting, replace these with actual audio files.")
        print("\nPlease run the script again after verifying the path, or replace with your actual album.")
    else:
        print(f"\n--- Options for Reordering Album '{album_path}' ---")
        print("1. Alphabetical (A-Z)")
        print("2. Reverse Alphabetical (Z-A)")
        print("3. By Duration (Shortest to Longest)")
        print("4. By Duration (Longest to Shortest)")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            reorder_album(album_path, sort_criterion='alphabetical', reverse=False)
        elif choice == '2':
            reorder_album(album_path, sort_criterion='reverse_alphabetical')
        elif choice == '3':
            reorder_album(album_path, sort_criterion='duration', reverse=False)
        elif choice == '4':
            reorder_album(album_path, sort_criterion='duration', reverse=True)
        else:
            print("Invalid choice. No action taken.")
