# Qwen-Omni Parallel Evaluation Tool

This directory contains scripts for parallelized evaluation of the Qwen-Omni model on the SpeechParaling-Bench dataset, designed to handle large datasets efficiently with auto-retry on rate limits.

## Prerequisites

1. **Get API Key**: Register at https://dashscope.console.aliyun.com/ to get your DashScope API key.

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

## Quick Start

### Running via Shell Script (Recommended)

The `run_task.sh` script is a wrapper for running parallel tasks. Ensure you have set your API key and configured the paths within the script if necessary.

```bash
# Make the script executable if not already
chmod +x run_task.sh

# Run the task
./run_task.sh
```

### Running Manually via Python

You can run the parallel evaluation script directly with custom arguments:

```bash
# Example: Run parallel evaluation on Chinese Short Single-dimension dataset
python run_sample_parallel_v2.py \
    --input_dir ../../audio_dataset_ch/para_con/con_short_sin \
    --output_dir ../../api_models/qwen-omni/output_ch/para_con/con_short_sin \
    --api_key YOUR_DASHSCOPE_API_KEY \
    --language zh \
    --max_workers 5
```

### Available Arguments

- `--input_dir`: Path to the directory containing input audio files.
- `--output_dir`: Path to the directory to save generated output audio.
- `--api_key`: Your DashScope API key (required).
- `--language`: Language of the task, either `zh` or `en`.
- `--max_files`: (Optional) Limit number of files to process (useful for testing).
- `--max_workers`: Number of parallel threads to run (default: 3).
- `--max_retries`: Maximum retries on Rate Limit (429) errors (default: 5).

## Features

- **Parallel Processing**: Uses `ThreadPoolExecutor` to process multiple audio files simultaneously.
- **Rate Limit Handling**: Implements exponential backoff retry logic for 429 errors.
- **Resume Capability**: Checks if output files already exist in `output_dir` and skips them automatically.
