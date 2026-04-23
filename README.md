# SpeechParaling-Bench: A Comprehensive Benchmark for Paralinguistic-Aware Speech Generation

![Speech Generation](https://img.shields.io/badge/Task-Speech_Generation-red)
![Paralanguage](https://img.shields.io/badge/Task-Paralanguage-red)
![Dataset](https://img.shields.io/badge/Dataset-SpeechParaling--Bench-blue)
![Gemini](https://img.shields.io/badge/Model-Gemini-green)
![Doubao](https://img.shields.io/badge/Model-Doubao-green)
![GPT](https://img.shields.io/badge/Model-GPT-green)
![Qwen](https://img.shields.io/badge/Model-Qwen-green)

<p align="center">
    <img src="./pic.png" width="100%" height="100%">
</p>

<font size=7><div align='center' >[[📖 Paper](https://arxiv.org/abs/2604.20842)] [[🌐 Project Page](https://speechparaling-bench.github.io/)] [[🤗 Dataset](https://huggingface.co/datasets/Ruohan2/SpeechParaling-Bench)]</div></font>

**SpeechParaling-Bench** is a comprehensive benchmark designed to evaluate **paralinguistic-aware speech generation** capabilities of large audio-language models (LALMs). It features **100+ paralinguistic dimensions** and **1000+ Chinese-English evaluation samples**, using a **baseline-candidate comparative evaluation** approach to produce a leaderboard for mainstream multimodal large models.

## 🗒 SpeechParaling-Bench Overview

The benchmark covers three core evaluation dimensions:

- **Paralanguage Control (可控生成)**: Evaluates single-dimensional and multi-dimensional paralinguistic information generation capabilities
- **Dynamic Variation (动态调节)**: Assesses models' ability to dynamically adjust paralinguistic features
- **Situational Adaptation (情景共情)**: Tests situational empathy and context-appropriate paralinguistic expression

All instructions are aligned in both Chinese and English, covering diverse real-life scenarios such as daily life, campus, workplace, family, and entertainment. The generated content naturally and reasonably matches the required paralinguistic information.

SpeechParaling-Bench aims to reflect the challenges of LALM paralinguistic generation and support fair, transparent, and extensible evaluation of next-generation LALM models.

## 📁 Repository Structure

```
SpeechParaling-Bench/
├── api_models/                    # API calling codes for mainstream models
│   ├── doubao/                    # Chinese baseline model
│   │   ├── output_ch/             # Chinese output audio
│   │   └── output_en/             # English output audio
│   ├── gemini/                    # English baseline model
│   │   ├── output_ch/
│   │   └── output_en/
│   ├── gpt/
│   ├── qwen-omni/
│   └── qwen-omni-realtime/
├── audio_dataset_ch/              # Chinese audio dataset (3 dimensions)
│   ├── dyn_var/                   # Dynamic variation
│   ├── para_con/                  # Paralanguage control
│   │   ├── con_abs/
│   │   ├── con_long_multi/
│   │   ├── con_long_sin/
│   │   ├── con_short_multi/
│   │   └── con_short_sin/
│   └── sit_ada/                   # Situational adaptation
│       ├── sit_multi/
│       └── sit_sin/
├── audio_dataset_en/              # English audio dataset (3 dimensions)
│   ├── dyn_var/
│   ├── para_con/
│   └── sit_ada/
├── jsonl_prompt_ch/               # Chinese JSONL prompts & dimensions
├── jsonl_prompt_en/               # English JSONL prompts & dimensions
├── judge_data/                    # Evaluation data and codes
│   ├── judge_code/                # Evaluation codes for 3 dimensions
│   ├── result_v5/                 # Evaluation outputs
│   │   ├── judge_json/            # Model evaluations & scores
│   │   ├── metadata/              # Key data for score calculation
│   │   └── judge_result/          # Leaderboard results
│   └── score_calculate/           # Score calculation scripts
└── text_jsonl_generator/          # Codes for generating jsonl_prompt
```

## 🗃️ Dataset Access

The SpeechParaling-Bench dataset is available on 🤗 HuggingFace:

### Main Audio Datasets (Input)


| Dataset                                                                              | Description                      | Size   | Samples |
| ------------------------------------------------------------------------------------ | -------------------------------- | ------ | ------- |
| [SpeechParaling-Bench](https://huggingface.co/datasets/Ruohan2/SpeechParaling-Bench) | Chinese + English audio datasets | ~800MB | 2002    |


### Baseline Model Outputs


| Dataset                                                                                                | Description                         | Size   |
| ------------------------------------------------------------------------------------------------------ | ----------------------------------- | ------ |
| [SpeechParaling-Bench-Baseline](https://huggingface.co/datasets/Ruohan2/SpeechParaling-Bench-Baseline) | Doubao (Chinese) + Gemini (English) | ~480MB |


### Dataset Statistics


| Dimension | Chinese          | English          | Description            |
| --------- | ---------------- | ---------------- | ---------------------- |
| dyn_var   | 120 samples      | 120 samples      | Dynamic variation      |
| para_con  | 691 samples      | 691 samples      | Paralanguage control   |
| sit_ada   | 190 samples      | 190 samples      | Situational adaptation |
| **Total** | **1001 samples** | **1001 samples** |                        |


## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Northern-byte-bit/SpeechParaling-Bench.git
cd SpeechParaling-Bench
```

### 2. Download the Dataset

You need to download both the main audio datasets and the baseline model outputs:

```bash
pip install huggingface_hub

# Download main audio datasets
python script/download_data.py

# Download baseline model outputs
python script/download_baseline.py
```

### 3.  (Optional) Run Existing API Models

If you want to run the API models yourself to generate outputs, install the dependencies and run the scripts:

```bash
cd api_models
pip install -r requirements.txt
# Configure your API key and run MODEL_NAME/main.py
```

### 4. Prepare Your Model Output

Run your **speech-to-speech (S2S)** model on the SpeechParaling-Bench dataset and generate audio responses.

#### Sample Run Script

We provide sample run scripts using **Qwen-Omni API** in `api_models/qwen-omni-eval/` to help you get started quickly. The scripts support parallel processing and auto-retry on rate limits.

**Get API Key**: Register at [https://dashscope.console.aliyun.com/](https://dashscope.console.aliyun.com/) to get your DashScope API key.

**Install Dependencies**:
```bash
cd api_models/qwen-omni-eval
pip install -r requirements.txt
```

##### Option 1: Run All Tasks at Once (Recommended)

The `run_all_tasks.py` script automatically traverses all subdirectories in `audio_dataset_ch` and `audio_dataset_en`, processing every `.wav` file in parallel:

```bash
python api_models/qwen-omni-eval/run_all_tasks.py \
    --api_key YOUR_DASHSCOPE_API_KEY \
    --max_workers 5
```

##### Option 2: Run a Specific Folder Manually

If you only want to process a specific dataset folder, use `run_sample_parallel_v2.py` directly:

```bash
# Example: Process Chinese Short Single-dimension dataset
python api_models/qwen-omni-eval/run_sample_parallel_v2.py \
    --input_dir audio_dataset_ch/para_con/con_short_sin \
    --output_dir api_models/qwen-omni/output_ch/para_con/con_short_sin \
    --api_key YOUR_DASHSCOPE_API_KEY \
    --language ch \
    --max_workers 5

# Example: Process English dataset
python api_models/qwen-omni-eval/run_sample_parallel_v2.py \
    --input_dir audio_dataset_en/para_con/con_short_sin \
    --output_dir api_models/qwen-omni/output_en/para_con/con_short_sin \
    --api_key YOUR_DASHSCOPE_API_KEY \
    --language en \
    --max_workers 5
```

For testing, you can use `--max_files N` to process only N files:

```bash
python api_models/qwen-omni-eval/run_sample_parallel_v2.py \
    --input_dir audio_dataset_ch/para_con/con_short_sin \
    --output_dir api_models/qwen-omni/output_demo \
    --api_key YOUR_DASHSCOPE_API_KEY \
    --language ch \
    --max_files 3
```

**Arguments for `run_sample_parallel_v2.py`:**
- `--input_dir`: Path to the directory containing input audio files.
- `--output_dir`: Path to the directory to save generated output audio.
- `--api_key`: Your DashScope API key (required).
- `--language`: Language of the task, either `ch` (Chinese) or `en` (English).
- `--max_files`: (Optional) Limit number of files to process (useful for testing).
- `--max_workers`: Number of parallel threads to run (default: 3).
- `--max_retries`: Maximum retries on Rate Limit (429) errors (default: 5).

#### Output Directory Structure

Format your audio output according to the structure in `api_models/doubao/output_ch/`:

```
api_models/YOUR_MODEL/
├── output_ch/
│   ├── dyn_var/          # Dynamic variation outputs
│   │   ├── dyn_var_001.wav
│   │   ├── dyn_var_002.wav
│   │   └── ...
│   ├── para_con/         # Paralanguage control outputs
│   │   ├── con_abs/
│   │   ├── con_long_multi/
│   │   ├── con_long_sin/
│   │   ├── con_short_multi/
│   │   └── con_short_sin/
│   └── sit_ada/          # Situational adaptation outputs
│       ├── sit_multi/
│       └── sit_sin/
└── output_en/
    ├── dyn_var/
    ├── para_con/
    └── sit_ada/
```

### 5. Run Evaluation

Use the evaluation codes in `judge_data/judge_code/`:

1. **Configure your settings** in `judge_data/config.py`:

```python
# judge_data/config.py

API_KEY = "YOUR_API_KEY"
MY_MODEL_NAME = "YOUR_MODEL_NAME"
BASE_URL = "BASE_URL"
```

2. **Run the evaluation** (no further modification of evaluation scripts needed):

```bash
# Run all evaluations automatically
python judge_data/run_all_evaluations.py
```

### 6. Calculate Scores

After evaluation, you can calculate all module scores and the overall leaderboard score in one go:

```bash
python judge_data/run_all_calculate.py
```

- Detailed per-module scores are saved in `judge_data/result_v5/result_v5_[module]/judge_result/`.
- Final normalized aggregated scores are saved in `judge_data/score_calculate/final_results/`.

---

## 📊 Evaluation Dimensions


| Dimension    | Description            | Configurations                                                |
| ------------ | ---------------------- | ------------------------------------------------------------- |
| **dyn_var**  | Dynamic Variation      | Chinese/English                                               |
| **para_con** | Paralanguage Control   | Long/Short, Single/Multi-dimension, Abstract, Chinese/English |
| **sit_ada**  | Situational Adaptation | Single/Multi-dimension, Chinese/English                       |


## 📄 Citation

If you use SpeechParaling-Bench in your research, please cite:

```bibtex
@article{speechparaling-bench,
      title={SpeechParaling-Bench: A Comprehensive Benchmark for Paralinguistic-Aware Speech Generation}, 
      author={Liu, Ruohan and Yin, Shukang and Wang, Tao and Zhang, Dong and Zhuang, Weiji and Ren, Shuhuai and He, Ran and Shan, Caifeng and Fu, Chaoyou},
      journal={arXiv preprint arXiv:2604.20842},
      year={2026}
}
```

## 📜 License

This project is licensed under the Apache-2.0 License.

## 🙏 Acknowledgements

We thank the following models and tools that made this benchmark possible:

- Gemini-2.5-Flash / Gemini-3 Pro (Evaluation)
- Doubao Realtime (Baseline)
- Gemini Audio (Baseline)
- GPT Audio
- Qwen-Omni
- Index-TTS

## 📧 Contact

For questions and feedback, please open an issue on GitHub or contact [[221900134@smail.nju.edu.cn](mailto:221900134@smail.nju.edu.cn)].
