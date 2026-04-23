import http.client
import json
import base64
import os

# Configuration
INPUT_DIR = "audio_dataset_en/para_con/con_long_sin"
OUTPUT_DIR = "api_models/gpt/output_en/para_con/con_long_sin"

API_HOST = ""
API_PATH = ""
API_KEY = ""

MODEL_NAME = "gpt-audio-2025-08-28"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Process input directory
for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".wav"):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    print(f"\n--- Processing file: {filename} ---")

    try:
        # Read wav file
        with open(input_path, "rb") as f:
            wav_data = f.read()

        print(f"Original wav size: {len(wav_data) / 1024:.2f} KB")

        # Base64 encode
        encoded_wav = base64.b64encode(wav_data).decode("utf-8")
        print(f"Base64 encoded length: {len(encoded_wav)}")

        # Construct request
        payload = json.dumps({
            "model":
            MODEL_NAME,
            "modalities": ["text", "audio"],
            "audio": {
                "voice": "alloy",
                "format": "wav"
            },
            "messages": [{
                "role":
                "user",
                "content": [{
                    "type":
                    "text",
                    "text":
                    "Directly speak the user's requested sentence in the specified tone without any prefix."
                }, {
                    "type": "input_audio",
                    "input_audio": {
                        "data": encoded_wav,
                        "format": "wav"
                    }
                }]
            }]
        })

        headers = {
            "Authorization": API_KEY,
            "Content-Type": "application/json"
        }

        # Send request
        conn = http.client.HTTPSConnection(API_HOST, timeout=60)
        conn.request("POST", API_PATH, payload, headers)

        res = conn.getresponse()
        raw = res.read().decode("utf-8")
        conn.close()

        # Parse response
        resp = json.loads(raw)

        text_reply = resp["choices"][0]["message"].get("content", [])
        print("Text reply:", text_reply)

        audio_info = resp["choices"][0]["message"].get("audio")

        # Save audio
        if audio_info and "data" in audio_info:
            audio_bytes = base64.b64decode(audio_info["data"])

            with open(output_path, "wb") as f:
                f.write(audio_bytes)

            print(f"Audio saved: {output_path}")
        else:
            print(f"Warning: No audio data in response for file: {filename}")

    except Exception as e:
        print(f"Error processing file {filename}: {e}")

print("\n--- Batch processing complete ---")
