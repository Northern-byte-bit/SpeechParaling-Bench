# Qwen-Omni Sample Run

This directory contains a sample script to run Qwen-Omni model on the SpeechParaling-Bench dataset.

## Prerequisites

1. **Get API Key**: Register at https://dashscope.console.aliyun.com/ to get your API key

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

## Quick Start

### Run on Chinese Dataset

```bash
# Run all files
python run_sample.py \
    --input_dir ../../audio_dataset_ch/para_con/con_short_sin \
    --output_dir output_ch/para_con/con_short_sin \
    --api_key YOUR_DASHSCOPE_API_KEY \
    --language zh

# Or run just first 3 files for testing
python run_sample.py \
    --input_dir ../../audio_dataset_ch/para_con/con_short_sin \
    --output_dir output_demo \
    --api_key YOUR_DASHSCOPE_API_KEY \
    --language zh \
    --max_files 3
```

### Run on English Dataset

```bash
python run_sample.py \
    --input_dir ../../audio_dataset_en/para_con/con_short_sin \
    --output_dir output_en/para_con/con_short_sin \
    --api_key YOUR_DASHSCOPE_API_KEY \
    --language en
```

## Output Structure

After running, the output follows this structure:

```
api_models/qwen-omni/
├── output_ch/
│   └── para_con/
│       └── con_short_sin/
│           ├── con_short_sin_001.wav
│           ├── con_short_sin_002.wav
│           └── ...
└── output_en/
    └── ...
```

## Available Tasks

| Task                                 | Input Directory                             |
| ------------------------------------ | ------------------------------------------- |
| Paralanguage Control (short, single) | `audio_dataset_ch/para_con/con_short_sin`   |
| Paralanguage Control (short, multi)  | `audio_dataset_ch/para_con/con_short_multi` |
| Paralanguage Control (long, single)  | `audio_dataset_ch/para_con/con_long_sin`    |
| Paralanguage Control (long, multi)   | `audio_dataset_ch/para_con/con_long_multi`  |
| Dynamic Variation                    | `audio_dataset_ch/dyn_var`                  |
| Situational Adaptation               | `audio_dataset_ch/sit_ada`                  |

## Notes

- The script uses Qwen3-Omni-Flash model via Alibaba DashScope
- Audio is generated at 24000Hz sample rate
- You can add more tasks by modifying the `BATCH_TASKS` list in the original `main.py`
- You can modify `instructions` to better generate audios in situational adaptation part.