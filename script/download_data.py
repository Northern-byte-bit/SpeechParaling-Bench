# download_data.py
from huggingface_hub import snapshot_download
import os
import shutil


def download_dataset(lang):
    """Download a language dataset from Hugging Face."""

    target_dir = f"audio_dataset_{lang}"

    if os.path.exists(target_dir):
        print(f"{target_dir} already exists, skipping download...")
        return

    print(f"Downloading audio_dataset_{lang}...")

    source_folder = f"{lang}/audio_files"

    snapshot_download(
        repo_id="Ruohan2/SpeechParaling-Bench",
        local_dir="./",
        repo_type="dataset",
        allow_patterns=[f"{source_folder}/**"],
    )

    source_dir = source_folder
    if os.path.exists(source_dir):
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.move(source_dir, target_dir)
        print(f"audio_dataset_{lang} downloaded!")
    else:
        print(f"Error: {source_dir} not found")


def download_all():
    download_dataset("ch")
    download_dataset("en")
    print("Download completed!")


if __name__ == "__main__":
    download_all()
