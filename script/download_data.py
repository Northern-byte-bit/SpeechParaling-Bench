import os
import shutil
from huggingface_hub import snapshot_download

def setup_dataset():
    repo_id = "Ruohan2/SpeechParaling-Bench"
    local_dir = "./temp_hf_download"
    
    # 1. Download the repository
    print(f"Downloading dataset from {repo_id}...")
    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        repo_type="dataset",
        allow_patterns=["ch/audio_files/*", "en/audio_files/*"]
    )

    # Define the mapping from HF structure to your desired local structure
    mapping = {
        "ch/audio_files": "audio_dataset_ch",
        "en/audio_files": "audio_dataset_en"
    }

    for src_subpath, target_name in mapping.items():
        src_path = os.path.join(local_dir, src_subpath)
        target_path = os.path.join(os.getcwd(), target_name)

        if os.path.exists(src_path):
            # Remove target dir if it already exists to avoid nesting
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            
            # Move the content to the top level as requested
            print(f"Organizing {target_name}...")
            shutil.move(src_path, target_path)
        else:
            print(f"Warning: Source path {src_path} not found.")

    # 2. Clean up temporary download artifacts
    if os.path.exists(local_dir):
        shutil.rmtree(local_dir)
    
    print("Dataset download and reorganization complete!")
    print(f"Structure created: \n - {os.path.abspath('audio_dataset_ch/')} \n - {os.path.abspath('audio_dataset_en/')}")

if __name__ == "__main__":
    # Ensure you have huggingface_hub installed: pip install huggingface_hub
    setup_dataset()
