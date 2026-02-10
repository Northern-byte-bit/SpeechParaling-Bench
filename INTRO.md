# SpeechParaling-Bench: A Comprehensive Benchmark for Paralinguistic-Aware Speech Generation

ParalingBench is a research-oriented benchmark suite designed to evaluate sub-language (paralinguistic) generation and situational empathy in large speech models. The core pipeline centers around Gemini-2.5-Flash for test instruction design, an audio synthesis stage via Index-TTS, multi-model audio generation (including closed and open models), and evaluation through Gemini-3 Pro with a transparent scoring scheme.

This repository hosts the data templates, sample prompts, and the orchestration scripts required to reproduce the evaluation pipeline end-to-end.

Note: The repository contained here is not yet a Git repository by default, but it is structured to be drop-in ready for GitHub hosting. The root folder is the release workspace that contains language prompts, audio prompts, and model-call sources.

## Highlights
- JSONL-based test instruction design for three modules:
  - Controllable generation module (prompt + dimensions)
  - Dynamic modulation module (prompt + dimensions)
  - Empathy/situation module (prompt + dimensions) with precise feature annotations
- Bilingual prompt coverage: Chinese and English prompts, designed to span campus, workplace, and other common life scenes.
- Audio pipeline: Index-TTS converts text instructions to audio; synthesis runs against multiple model APIs (doubao-realtime, Gemini-2.5-flash-audio, gpt-audio, qwen3-omni-flash-2025-12-01).
- Evaluation: Gemini-3 Pro compares audio outputs and returns per-pair JSONL results.
- Scoring and ranking: simple win/loss scoring with a baseline scoring formula and a leaderboard output in CSV/JSON.
- Reproducibility: explicit data formats, IDs, and versioned model configurations to enable repeatable experiments.

## Project Structure
The release folder contains the following key components. Paths are shown relative to the repository root.

- jsonl_prompt_ch/
  - sit_ada/
  - 适应_单维度.jsonl
  - 适应_多维度.jsonl
- jsonl_prompt_en/
  - sit_ada/
  - para_con/
  - dyn_var/
  - jsonl生成.py
- jsonl_prompt_ch/para_con/
- jsonl_prompt_en/para_con/
- jsonl_prompt_en/dyn_var/
- jsonl_prompt_en/sit_ada/
- audio_dataset_en/
- api_models/doubao/python3.7/README.md
- release/（当前项目工作区）

Notes:
- The JSONL prompt templates capture three modules:
  - Controllable generation: {"prompt": "<text>", "dimensions": ["<dimension>"]}
  - Dynamic modulation: {"prompt": "<text>", "dimensions": ["<dimension>"]}
  - Empathy/situation: {"prompt": "<text>", "dimensions": ["<dimension>"]}
- The audio assets under audio_dataset_en are prepared for quick reference and may be used to seed audio test vectors.

## Data Formats (JSONL)
Three representative formats are used to describe test instructions and sub-language dimensions. Each line is a JSON object.

- Controllable generation module example:
```json
{"prompt": "Please say in a child's voice: Mom, may I have another cookie?", "dimensions": ["age"]}
```

- Dynamic modulation module example:
```json
{"prompt": "Start with a merry rhythm, then switch to urgent: let me watch TV to unwind; no, why is this broken TV again?", "dimensions": ["tempo"]}
```

- Empathy/situation module example:
```json
{"prompt": "My puppy is missing, sob, I’ve looked all day; could something bad have happened?", "dimensions": ["nonverbal_sound: crying"]}
```

-campus/work scenes and events are pre-defined in the repository prompts to ensure diversity and realism. See jsonl_prompt_ch and jsonl_prompt_en for concrete files.

## Pipeline Overview
1) Instruction Design
- Generate three kinds of JSONL prompts across 5 life scenes × 5 events each. Dimensions are enumerated in advance to ensure coverage.
- Outputs: three JSONL files (one per module) with prompt and dimensions fields.

2) Audio Instruction Synthesis
- Use Index-TTS to synthesize text prompts into audio files.
- Feed audio prompts to multiple model APIs: doubao-realtime, Gemini-2.5-flash-audio, gpt-audio, and qwen3-omni-flash-2025-12-01.

3) Sub-Language Evaluation
- Pairwise compare model outputs using Gemini-3 Pro with evaluation prompts that embed sub-language criteria.
- Output per-pair results in JSONL.

4) Scoring and Leaderboard
- Scoring rules: win (+1) / loss (0) / draw (+0.5 each) per pair; baseline uses a weighted average over evaluation groups.
- Produce per-model scores and an overall ranking.

5) Output and Reproducibility
- Deliver three instruction JSONL files, audio data, per-pair evaluation JSONL, and leaderboard (CSV/JSON).
- Log model versions, prompts, and evaluation settings for traceability.

## Reproducibility and How to Run
Prerequisites:
- Python 3.10 (for any Python-based tooling in release)
- Node.js (if you plan to run JS tooling)
- FFmpeg and basic audio tooling for conversions
- Access to model APIs (doubao, Gemini-2.5-flash-audio, gpt-audio, qwen3-omni-flash-2025-12-01) or equivalent fixtures
- Index-TTS (local or API)

Quickstart (high level):
1) Inspect the prompt sets in:
- release/jsonl_prompt_ch/
- release/jsonl_prompt_en/
2) Generate JSONL instruction sets (if not already present) using:
```bash
python release/jsonl_prompt_en/jsonl生成.py
```
3) Synthesize instruction prompts to audio via Index-TTS and feed to the model APIs (mock or real endpoints as configured).
4) Run pairwise evaluation with Gemini-3 Pro and collect JSONL results.
5) Compute leaderboard and output results in CSV/JSON.

For detailed, step-by-step commands, see the dedicated scripts and READMEs inside:
- release/api_models/doubao/python3.7/README.md
- release/jsonl_prompt_en/… (various JSONL and tooling)

## Extending and Contributing
- Add new test prompts by editing or adding to the jsonl_prompt_ch or jsonl_prompt_en directories, following the existing JSONL schema.
- Extend the evaluation by integrating additional model APIs or alternate evaluation models; ensure a clear configuration for S_C_i weights and N in the baseline formula.
- Document any new scripts and maintain a changelog for reproducibility.

Contributions welcome. Please open issues or PRs with a concise description of changes and expected impact.

## Licensing and Authors
- Licensing: TBD (replace with your chosen license)
- Authors: (your team)

## Related Artifacts and References
- Gemini-2.5-Flash (test instruction design and audio prompts)
- Index-TTS (audio synthesis)
- Doubao realtime, Gemini-2.5-flash-audio, gpt-audio, qwen3-omni-flash-2025-12-01 (model APIs)
- Gemini-3 Pro (per-pair evaluation channel)
- The repository includes example prompts and workflow scripts under release/jsonl_prompt_ch and release/jsonl_prompt_en, plus a ready-to-inspect README in api_models/doubao/python3.7/README.md
