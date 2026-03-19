import os
import subprocess
import argparse

# Configuration
# Base directories in the project
DATASET_ROOTS = ["audio_dataset_ch", "audio_dataset_en"]
OUTPUT_ROOT = "api_models/qwen-omni"


def run_evaluation(api_key, language, max_workers):
    """
    Traverse dataset directories and run parallel evaluation for each sub-directory.
    """
    for dataset_root in DATASET_ROOTS:
        if not os.path.exists(dataset_root):
            print(
                f"[Warning] Dataset root not found: {dataset_root}, skipping.")
            continue

        # Determine language suffix based on folder name
        lang_suffix = "ch" if "ch" in dataset_root else "en"

        # Walk through all subdirectories
        for root, dirs, files in os.walk(dataset_root):
            # Check if this directory contains wav files
            wav_files = [f for f in files if f.lower().endswith(".wav")]
            if not wav_files:
                continue

            # Construct relative path to maintain structure
            rel_path = os.path.relpath(root, dataset_root)

            # Set input and output directories
            input_dir = root
            # Example mapping: audio_dataset_ch/para_con/con_short_sin -> output_ch/para_con/con_short_sin
            output_dir = os.path.join(OUTPUT_ROOT, f"output_{lang_suffix}",
                                      rel_path)

            print(f"\n{'='*60}")
            print(f"Processing: {rel_path} ({lang_suffix})")
            print(f"Input: {input_dir}")
            print(f"Output: {output_dir}")
            print(f"{'='*60}")

            # Run the parallel evaluation script
            try:
                subprocess.run([
                    "python",
                    "api_models/qwen-omni-eval/run_sample_parallel_v2.py",
                    "--input_dir", input_dir, "--output_dir", output_dir,
                    "--api_key", api_key, "--language", lang_suffix,
                    "--max_workers",
                    str(max_workers)
                ],
                               check=True)
            except subprocess.CalledProcessError as e:
                print(f"[Error] Failed to process {rel_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run parallel evaluation on all datasets.")
    parser.add_argument("--api_key",
                        type=str,
                        required=True,
                        help="DashScope API key")
    parser.add_argument("--max_workers",
                        type=int,
                        default=5,
                        help="Number of parallel workers")

    args = parser.parse_args()

    run_evaluation(args.api_key, None, args.max_workers)
