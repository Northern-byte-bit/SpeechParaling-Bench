import os
import base64
import numpy as np
import json
import soundfile as sf
from openai import OpenAI
from pathlib import Path

# Configuration and Constants
API_KEY = ""
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen3-omni-flash"

# Batch tasks: (input_dir, output_dir)
BATCH_TASKS = [
    ("audio_dataset_ch/para_con/con_short_multi",
     "api_models/qwen-omni/output_ch/para_con/con_short_multi"),
]

# Initialize OpenAI client
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


def encode_audio(audio_path):
    """Encode a local audio file to a Base64 string."""
    try:
        with open(audio_path, "rb") as audio_file:
            audio_file.seek(0, os.SEEK_END)
            if audio_file.tell() == 0:
                print(f"Warning: File {audio_path} is empty, skipping.")
                return None
            audio_file.seek(0)
            return base64.b64encode(audio_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: File {audio_path} not found.")
        return None
    except Exception as e:
        print(f"Error encoding file {audio_path}: {e}")
        return None


def process_audio_file(input_path, output_path):
    """Process a single audio file: encode, call API, decode, and save."""
    print(f"  > Processing file: {os.path.basename(input_path)}")

    base64_audio = encode_audio(input_path)
    if not base64_audio:
        return

    messages_content = [
        {
            "type": "input_audio",
            "input_audio": {
                "data": f"data:audio/wav;base64,{base64_audio}",
                "format": "wav",
            },
        },
        {
            "type":
            "text",
            "text":
            "Please directly speak the sentence with the specified tone as requested, without any introductory phrases.",
        },
    ]

    audio_string = ""
    transcript = ""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
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
            print(f"    - Success: Audio saved to {output_path}")
            if transcript:
                print(f"    - Transcript: {transcript.strip()}")
        else:
            print(f"    - Warning: No audio data in response")

    except Exception as e:
        print(f"    - Error: {e}")


def process_audio_batch():
    """Execute batch audio processing and generation."""
    print("--- Starting batch audio file processing ---")

    for input_dir, output_dir in BATCH_TASKS:
        print(f"\n--- Processing directory: {input_dir} ---")

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        print(f"Output directory ready: {output_dir}")

        try:
            for filename in os.listdir(input_dir):
                if filename.lower().endswith(".wav"):
                    input_path = os.path.join(input_dir, filename)
                    output_path = os.path.join(output_dir, filename)
                    process_audio_file(input_path, output_path)

        except FileNotFoundError:
            print(f"Warning: Input directory {input_dir} not found. Skipping.")
        except Exception as e:
            print(f"Error processing directory {input_dir}: {e}")

    print("\n--- All batch processing tasks completed ---")


if __name__ == "__main__":
    process_audio_batch()
