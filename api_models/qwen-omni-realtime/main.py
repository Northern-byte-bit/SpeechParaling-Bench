# pip install websocket-client
import json
import websocket
import os
import base64
import wave

# Configuration
BATCH_TASKS = [
    ("audio_dataset_ch/para_con/con_short_multi",
     "api_models/qwen-omni-realtime/output_ch/para_con/con_short_multi"),
]

API_KEY = ""
API_URL = "wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen3-omni-flash-realtime"

HEADERS = ["Authorization: Bearer " + API_KEY]


# Helper functions
def wav_to_pcm16_chunks(wav_path, chunk_samples=3200):
    chunks = []
    with wave.open(wav_path, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2  # PCM16

        while True:
            data = wf.readframes(chunk_samples)
            if not data:
                break
            chunks.append(data)
    return chunks


def save_output_audio(output_path, frames):
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # pcm16
        wf.setframerate(24000)
        wf.writeframes(b"".join(frames))


# Single file processing function
def process_one_wav(input_path, output_path):
    output_frames = []

    def on_open(ws):
        # Session initialization
        ws.send(
            json.dumps({
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "voice": "Cherry",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "instructions":
                    "Please directly speak the sentence with the specified tone as requested, without any introductory phrases.",
                    "turn_detection": None
                }
            }))

        # Send audio
        pcm_chunks = wav_to_pcm16_chunks(input_path)
        for chunk in pcm_chunks:
            ws.send(
                json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": base64.b64encode(chunk).decode()
                }))

        ws.send(json.dumps({"type": "input_audio_buffer.commit"}))

    def on_message(ws, message):
        data = json.loads(message)
        t = data.get("type")

        if t == "input_audio_buffer.committed":
            ws.send(
                json.dumps({
                    "type": "response.create",
                    "response": {
                        "modalities": ["audio"]
                    }
                }))

        elif t == "response.audio.delta":
            output_frames.append(base64.b64decode(data["delta"]))

        elif t == "response.audio.done":
            save_output_audio(output_path, output_frames)

        elif t == "response.done":
            ws.close()

    ws = websocket.WebSocketApp(API_URL,
                                header=HEADERS,
                                on_open=on_open,
                                on_message=on_message)

    ws.run_forever()


# Batch processing
for input_dir, output_dir in BATCH_TASKS:
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n=== Starting to process directory: {input_dir} ===")

    for filename in os.listdir(input_dir):
        if not filename.endswith(".wav"):
            continue

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        print(f"\n--- Processing: {filename} ---")
        process_one_wav(input_path, output_path)
        print(f"Done: {output_path}")

print("\n--- All directories processed ---")
