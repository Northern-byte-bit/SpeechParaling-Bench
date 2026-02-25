# SpeechParaling-Bench: A Comprehensive Benchmark for Paralinguistic-Aware Speech Generation

[📄 Paper (arXiv)]() · [🌐 Project Page](https://Northern-byte-bit.github.io/SpeechParaling-Bench) · [🤗 Dataset](https://huggingface.co/datasets/Ruohan2) · [💻 Code](https://github.com/Northern-byte-bit/SpeechParaling-Bench)

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
│   └── score_culculate/           # Score calculation scripts
└── text_jsonl_generator/          # Codes for generating jsonl_prompt
```

## 🗃️ Dataset Access

The SpeechParaling-Bench dataset is available on 🤗 HuggingFace:

### Main Audio Datasets

| Dataset                                                                                               | Description           | Size   | Samples |
| ----------------------------------------------------------------------------------------------------- | --------------------- | ------ | ------- |
| [SpeechParaling-Bench-Chinese](https://huggingface.co/datasets/Ruohan2/SpeechParaling-Bench-Chinese) | Chinese audio dataset | ~361MB | 1001    |
| [SpeechParaling-Bench-English](https://huggingface.co/datasets/Ruohan2/SpeechParaling-Bench-English) | English audio dataset | ~438MB | 1001    |

### Baseline Model Outputs

| Dataset                                                                                                       | Description                    | Notes                    |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------ | ------------------------ |
| [SpeechParaling-Bench-Baseline-Doubao](https://huggingface.co/datasets/Ruohan2/SpeechParaling-Bench-Baseline-Doubao)   | Doubao Chinese outputs (output_ch)  | Chinese baseline model   |
| [SpeechParaling-Bench-Baseline-Gemini](https://huggingface.co/datasets/Ruohan2/SpeechParaling-Bench-Baseline-Gemini)   | Gemini English outputs (output_en)  | English baseline model   |

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

You need to download both the main audio datasets and the baseline model outputs.

#### 2.1 Main Audio Datasets

##### Option A: Using Python Script

```python
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
```

Run the script:
```bash
pip install huggingface_hub
python download_data.py
```

##### Option B: Using huggingface-cli

```bash
# Install huggingface_hub
pip install huggingface_hub

# Download Chinese dataset
huggingface-cli download \
    --repo-type dataset \
    Ruohan2/SpeechParaling-Bench-Chinese \
    --local-dir ./audio_dataset_ch \
    --local-dir-use-symlinks False

# Download English dataset
huggingface-cli download \
    --repo-type dataset \
    Ruohan2/SpeechParaling-Bench-English \
    --local-dir ./audio_dataset_en \
    --local-dir-use-symlinks False
```

#### 2.2 Baseline Model Outputs

Download the baseline model outputs for evaluation comparison:

##### Option A: Using Python Script

```python
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
```

##### Option B: Using huggingface-cli

```bash
# Download Doubao Chinese baseline
huggingface-cli download \
    --repo-type dataset \
    Ruohan2/SpeechParaling-Bench-Baseline-Doubao \
    --local-dir ./api_models/doubao/output_ch \
    --local-dir-use-symlinks False

# Download Gemini English baseline
huggingface-cli download \
    --repo-type dataset \
    Ruohan2/SpeechParaling-Bench-Baseline-Gemini \
    --local-dir ./api_models/gemini/output_en \
    --local-dir-use-symlinks False
```

### 3. Prepare Your Model Output

Run your **speech-to-speech (S2S)** model on the SpeechParaling-Bench dataset and generate audio responses.

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

### 4. Run Evaluation

Use the evaluation codes in `judge_data/judge_code/`:

1. **Add your API_KEY** in the evaluation script
2. **Modify the paths** in `MODEL_DIRS` and `OUTPUT_DIRS`:

```python
# Example: judge_data/judge_code/dyn_var/dyn_var_ch.py

API_KEY = "YOUR_API_KEY"

MODEL_DIRS = {
    "doubao": "api_models/doubao/output_ch/dyn_var",
    "YOUR_MODEL_NAME": "api_models/YOUR_MODEL/output_ch/dyn_var",  # Add your model
}

OUTPUT_DIRS = {
    "doubao": "judge_data/result_v5/result_v5_dyn_var/judge_json/judge_json_v5_dyn_ch/doubao",
    "YOUR_MODEL_NAME": "judge_data/result_v5/result_v5_dyn_var/judge_json/judge_json_v5_dyn_ch/YOUR_MODEL_NAME",  # Add your output path
}
```

3. **Run the evaluation**:

```bash
# Dynamic Variation - Chinese
python judge_data/judge_code/dyn_var/dyn_var_ch.py

# Dynamic Variation - English
python judge_data/judge_code/dyn_var/dyn_var_en.py

# Paralanguage Control - various configurations
python judge_data/judge_code/para_con/para_con_long_sin_ch.py
python judge_data/judge_code/para_con/para_con_short_sin_ch.py
python judge_data/judge_code/para_con/para_con_abstract_ch.py
# ... etc

# Situational Adaptation
python judge_data/judge_code/sit_ada/sit_ada_sin_ch.py
python judge_data/judge_code/sit_ada/sit_ada_multi_ch.py
# ... etc
```

### 5. Calculate Scores

After evaluation, calculate the leaderboard scores (use dynamic variation as an example):

```bash
python judge_data/score_culculate/score_culculate_dyn_var.py
```

Results will be saved in `judge_data/result_v5/result_v5_dyn_var/judge_result/`.

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
@misc{speechparaling-bench2026,
      title={SpeechParaling-Bench: A Comprehensive Benchmark for Paralinguistic-Aware Speech Generation}, 
      author={},
      year={2026},
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

For questions and feedback, please open an issue on GitHub or contact [221900134@smail.nju.edu.cn].
