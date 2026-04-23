# download_data.py
from huggingface_hub import hf_hub_download
import zipfile
import os

def download_and_extract():
    # Download Chinese audio dataset
    print("Downloading audio_dataset_ch.zip...")
    zip_path = hf_hub_download(
        repo_id="Ruohan2/SpeechParaling-Bench",
        filename="audio_dataset_ch.zip",
        local_dir="./",
        repo_type="dataset"
    )
    print("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("./")
    os.remove(zip_path)
    print("audio_dataset_ch extracted!")
    
    # Download English audio dataset
    print("Downloading audio_dataset_en.zip...")
    zip_path = hf_hub_download(
        repo_id="Ruohan2/SpeechParaling-Bench",
        filename="audio_dataset_en.zip",
        local_dir="./",
        repo_type="dataset"
    )
    print("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("./")
    os.remove(zip_path)
    print("audio_dataset_en extracted!")
    
    print("Download completed!")

if __name__ == "__main__":
    download_and_extract()
