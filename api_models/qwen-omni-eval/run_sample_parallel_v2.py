"""
SpeechParaling-Bench Sample Run Script (Parallel + Resume + Retry on rate limit)
======================================
Using Qwen-Omni API (Alibaba DashScope)
This script demonstrates how to run a speech-to-speech model on the SpeechParaling-Bench dataset.
"""
import os
import sys
import time
import random
import base64
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed


def encode_audio(audio_path):
    """Encode audio file to Base64 string."""
    try:
        with open(audio_path, "rb") as audio_file:
            audio_file.seek(0, os.SEEK_END)
            if audio_file.tell() == 0:
                print(f"  [Warning] File {audio_path} is empty, skipping.")
                return None
            audio_file.seek(0)
            return base64.b64encode(audio_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"  [Error] File {audio_path} not found.")
        return None
    except Exception as e:
        print(f"  [Error] Encoding file {audio_path}: {e}")
        return None


def process_audio_file(client,
                       input_path,
                       output_path,
                       language="ch",
                       max_retries=5):
    """Process a single audio file with retry logic on RateLimit (429)."""
    filename = os.path.basename(input_path)
    print(f"  > Processing: {filename}")

    base64_audio = encode_audio(input_path)
    if not base64_audio:
        return False

    if language == "ch":
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

    for attempt in range(max_retries):
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
                    if hasattr(delta, "audio"
                               ) and delta.audio and delta.audio.get("data"):
                        audio_string += delta.audio.get("data", "")
                    if hasattr(delta, "text") and delta.text:
                        transcript += delta.text

            if audio_string:
                wav_bytes = base64.b64decode(audio_string)
                audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
                sf.write(output_path, audio_np, samplerate=24000)

                log_msg = f"    - [SUCCESS] Saved: {filename}"
                if transcript:
                    log_msg += f" | Transcript: {transcript.strip()[:50]}..."
                print(log_msg)
                return True
            else:
                print(
                    f"    - [WARNING] No audio data in response for: {filename}"
                )
                return False

        except Exception as e:
            error_msg = str(e)
            # hit rate limit, try with larger waiting time.
            # an exponential backoff strategy
            if "Error code: 429" in error_msg:
                if attempt < max_retries - 1:
                    sleep_time = (2**attempt) * 2.0 + random.uniform(0.1, 1.5)
                    print(
                        f"    - [RATE LIMIT 429] {filename} is rate limited. Retrying in {sleep_time:.1f}s (Attempt {attempt+1}/{max_retries})"
                    )
                    time.sleep(sleep_time)
                    continue
                else:
                    print(
                        f"    - [ERROR] Failed on {filename} after {max_retries} retries due to Rate Limit."
                    )
                    return False
            else:
                print(f"    - [ERROR] Failed on {filename}: {e}")
                return False

    return False


def process_directory(input_dir,
                      output_dir,
                      api_key,
                      language="ch",
                      max_files=None,
                      max_workers=5,
                      max_retries=5):
    """Process all audio files in a directory using parallel workers."""

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    wav_files = [
        f for f in os.listdir(input_dir) if f.lower().endswith(".wav")
    ]
    wav_files.sort()

    if max_files:
        wav_files = wav_files[:max_files]

    print(f"\nInput:  {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Total Files: {len(wav_files)}")
    print(f"Concurrency: {max_workers} threads")
    print("-" * 60)

    success_count = 0
    skipped_count = 0
    files_to_process = []

    for filename in wav_files:
        output_path = os.path.join(output_dir, filename)
        if os.path.exists(output_path):
            print(f"  > [SKIP] Already exists: {filename}")
            skipped_count += 1
            success_count += 1
        else:
            files_to_process.append(filename)

    if not files_to_process:
        print("-" * 60)
        print("All files have already been processed! No API calls made.")
        print(f"Total Completed: {success_count}/{len(wav_files)}")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {}
        for filename in files_to_process:
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            future = executor.submit(process_audio_file, client, input_path,
                                     output_path, language, max_retries)
            future_to_file[future] = filename

        for future in as_completed(future_to_file):
            filename = future_to_file[future]
            try:
                result = future.result()
                if result:
                    success_count += 1
            except Exception as exc:
                print(
                    f"    - [FATAL ERROR] {filename} generated an exception: {exc}"
                )

    print("-" * 60)
    print(
        f"Done! Overall Success (including skipped): {success_count}/{len(wav_files)}"
    )
    print(f"Skipped (Already Existed): {skipped_count}")
    print(f"Actually Processed this run: {len(files_to_process)}")
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
                        default="ch",
                        choices=["ch", "en"],
                        help="Language: ch (Chinese) or en (English)")
    parser.add_argument(
        "--max_files",
        type=int,
        default=None,
        help="Maximum number of files to process (for testing)")
    parser.add_argument("--max_workers",
                        type=int,
                        default=3,
                        help="Maximum number of parallel workers (threads)")
    parser.add_argument(
        "--max_retries",
        type=int,
        default=5,
        help="Maximum number of retries when hitting rate limits (429)")

    args = parser.parse_args()

    print("=" * 60)
    print(
        "SpeechParaling-Bench - Qwen-Omni Sample Run (Parallel & Auto-Retry)")
    print("=" * 60)

    process_directory(args.input_dir, args.output_dir, args.api_key,
                      args.language, args.max_files, args.max_workers,
                      args.max_retries)


if __name__ == "__main__":
    main()
