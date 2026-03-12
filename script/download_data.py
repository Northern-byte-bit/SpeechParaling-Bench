# download_data.py
from huggingface_hub import snapshot_download
import os

def download_datasets():
    # Download Chinese audio dataset
    print("Downloading Chinese audio dataset...")
    snapshot_download(
        repo_id="Ruohan2/SpeechParaling-Bench-Chinese",
        local_dir="./audio_dataset_ch",
        repo_type="dataset",
        local_dir_use_symlinks=False
    )
    
    # Download English audio dataset
    print("Downloading English audio dataset...")
    snapshot_download(
        repo_id="Ruohan2/SpeechParaling-Bench-English",
        local_dir="./audio_dataset_en",
        repo_type="dataset",
        local_dir_use_symlinks=False
    )
    
    print("Main datasets download completed!")

if __name__ == "__main__":
    download_datasets()
