# Qwen-Omni Evaluation Tool

This directory contains scripts for evaluating the Qwen-Omni model on the SpeechParaling-Bench dataset. It supports parallel processing and auto-retry on rate limits, running seamlessly on Windows, Linux, and macOS.

## Prerequisites

1. **Get API Key**: Register at https://dashscope.console.aliyun.com/ to get your DashScope API key.

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

## Quick Start

### Option 1: Run All Tasks at Once (Recommended)

The `run_all_tasks.py` script automatically traverses all subdirectories in `audio_dataset_ch` and `audio_dataset_en`, processing every `.wav` file in parallel. This is the easiest way to run the full benchmark evaluation.

```bash
python run_all_tasks.py --api_key YOUR_DASHSCOPE_API_KEY --max_workers 5
```

**Arguments for `run_all_tasks.py`:**
- `--api_key`: Your DashScope API key (required).
- `--max_workers`: Number of parallel threads per task (default: 5).

---

### Option 2: Run a Specific Folder Manually

If you only want to process a specific dataset folder, use `run_sample_parallel_v2.py` directly:

```bash
# Example: Process Chinese Short Single-dimension dataset
python run_sample_parallel_v2.py \
    --input_dir ../../audio_dataset_ch/para_con/con_short_sin \
    --output_dir ../../api_models/qwen-omni/output_ch/para_con/con_short_sin \
    --api_key YOUR_DASHSCOPE_API_KEY \
    --language zh \
    --max_workers 5
```

**Arguments for `run_sample_parallel_v2.py`:**
- `--input_dir`: Path to the directory containing input audio files.
- `--output_dir`: Path to the directory to save generated output audio.
- `--api_key`: Your DashScope API key (required).
- `--language`: Language of the task, either `zh` (Chinese) or `en` (English).
- `--max_files`: (Optional) Limit number of files to process (useful for testing).
- `--max_workers`: Number of parallel threads to run (default: 3).
- `--max_retries`: Maximum retries on Rate Limit (429) errors (default: 5).
