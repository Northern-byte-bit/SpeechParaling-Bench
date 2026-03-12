"""
SpeechParaling-Bench Sample Run Script
======================================
Using Qwen-Omni API (Alibaba DashScope)
This script demonstrates how to run a speech-to-speech model on the SpeechParaling-Bench dataset.
Prerequisites:
1. Get API key from: https://dashscope.console.aliyun.com/
2. Install dependencies: pip install openai soundfile numpy
Usage:
    # Run on Chinese dataset (sample - first 3 files)
    python run_qwen_omni.py --input_dir ../../audio_dataset_ch/para_con/con_short_sin --output_dir output_ch/para_con/con_short_sin --api_key YOUR_API_KEY
    # Run on English dataset
    python run_qwen_omni.py --input_dir ../../audio_dataset_en/para_con/con_short_sin --output_dir output_en/para_con/con_short_sin --api_key YOUR_API_KEY --language en
"""
import os
import sys
import base64
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path
from openai import OpenAI


def encode_audio(audio_path):
    """Encode audio file to Base64 string."""
    try:
        with open(audio_path, "rb") as audio_file:
            audio_file.seek(0, os.SEEK_END)
            if audio_file.tell() == 0:
                print(f"  Warning: File {audio_path} is empty, skipping.")
                return None
            audio_file.seek(0)
            return base64.b64encode(audio_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"  Error: File {audio_path} not found.")
        return None
    except Exception as e:
        print(f"  Error encoding file {audio_path}: {e}")
        return None


def process_audio_file(client, input_path, output_path, language="zh"):
    """Process a single audio file: encode, call API, decode and save."""
    print(f"  > Processing: {os.path.basename(input_path)}")
    base64_audio = encode_audio(input_path)
    if not base64_audio:
        return False
    # Instruction text based on language
    if language == "zh":
        instruction = "请按照用户的要求，直接用指定的语气生成用户要求的句子，不包含任何前置语句。"
    else:
        instruction = "Please directly speak the sentence with the specified tone as requested, without any introductory phrases."
    messages_content = [
        {
            "type": "input_audio",
            "input_audio": {
                "data": f"data:audio/wav;base64,{base64_audio}",
                "format": "wav",
            },
        },
        {
            "type": "text",
            "text": instruction,
        },
    ]
    audio_string = ""
    transcript = ""
    try:
        completion = client.chat.completions.create(
            model="qwen3-omni-flash",
            messages=[{
                "role": "user",
                "content": messages_content
            }],
            modalities=["text", "audio"],
            audio={
                "voice": "Cherry",
                "format": "wav"
            },
            stream=True,
            stream_options={"include_usage": True},
        )
        for chunk in completion:
            if chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(
                        delta,
                        "audio") and delta.audio and delta.audio.get("data"):
                    audio_string += delta.audio.get("data", "")
                if hasattr(delta, "text") and delta.text:
                    transcript += delta.text
        if audio_string:
            wav_bytes = base64.b64decode(audio_string)
            audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
            sf.write(output_path, audio_np, samplerate=24000)
            print(f"    - Saved: {os.path.basename(output_path)}")
            if transcript:
                print(f"    - Transcript: {transcript.strip()[:50]}...")
            return True
        else:
            print(f"    - Warning: No audio data in response")
            return False
    except Exception as e:
        print(f"    - Error: {e}")
        return False


def process_directory(input_dir,
                      output_dir,
                      api_key,
                      language="zh",
                      max_files=None):
    """Process all audio files in a directory."""

    # Initialize OpenAI client for DashScope
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Get all wav files
    wav_files = [
        f for f in os.listdir(input_dir) if f.lower().endswith(".wav")
    ]
    wav_files.sort()

    if max_files:
        wav_files = wav_files[:max_files]

    print(f"\nInput:  {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Files:  {len(wav_files)}")
    print("-" * 40)

    success_count = 0
    for i, filename in enumerate(wav_files):
        print(f"[{i+1}/{len(wav_files)}]", end=" ")

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        if process_audio_file(client, input_path, output_path, language):
            success_count += 1

    print("-" * 40)
    print(f"Done! Success: {success_count}/{len(wav_files)}")
    print(f"Output saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Sample run script for SpeechParaling-Bench using Qwen-Omni"
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="../../audio_dataset_ch/para_con/con_short_sin",
        help="Directory containing input audio files")
    parser.add_argument(
        "--output_dir",
        type=str,
        default="../../api_models/qwen-omni/output_ch/para_con/con_short_sin",
        help="Directory to save output audio")
    parser.add_argument("--api_key",
                        type=str,
                        required=True,
                        help="DashScope API key")
    parser.add_argument("--language",
                        type=str,
                        default="zh",
                        choices=["zh", "en"],
                        help="Language: zh (Chinese) or en (English)")
    parser.add_argument(
        "--max_files",
        type=int,
        default=None,
        help="Maximum number of files to process (for testing)")

    args = parser.parse_args()

    print("=" * 60)
    print("SpeechParaling-Bench - Qwen-Omni Sample Run")
    print("=" * 60)

    process_directory(args.input_dir, args.output_dir, args.api_key,
                      args.language, args.max_files)


if __name__ == "__main__":
    main()
