# download_baseline.py
from huggingface_hub import snapshot_download

def download_baselines():
    # Download Doubao Chinese baseline outputs
    print("Downloading Doubao Chinese baseline...")
    snapshot_download(
        repo_id="Ruohan2/SpeechParaling-Bench-Baseline-Doubao",
        local_dir="./api_models/doubao/output_ch",
        repo_type="dataset",
        local_dir_use_symlinks=False
    )
    
    # Download Gemini English baseline outputs
    print("Downloading Gemini English baseline...")
    snapshot_download(
        repo_id="Ruohan2/SpeechParaling-Bench-Baseline-Gemini",
        local_dir="./api_models/gemini/output_en",
        repo_type="dataset",
        local_dir_use_symlinks=False
    )
    
    print("Baseline datasets download completed!")

if __name__ == "__main__":
    download_baselines()
