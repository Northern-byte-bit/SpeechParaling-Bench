# download_baseline.py
from huggingface_hub import hf_hub_download
import zipfile
import os

def download_and_extract():
    print("Downloading api_models.zip...")
    zip_path = hf_hub_download(
        repo_id="Ruohan2/SpeechParaling-Bench-Baseline",
        filename="api_models.zip",
        local_dir="./",
        repo_type="dataset"
    )
    print("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("./")
    os.remove(zip_path)
    print("api_models extracted!")
    print("Download completed!")

if __name__ == "__main__":
    download_and_extract()
