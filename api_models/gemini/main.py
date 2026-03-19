import asyncio
import io
import os
from pathlib import Path
import wave
from google import genai
from google.genai import types
import soundfile as sf
import librosa

# === Input/Output directories ===
INPUT_DIR = "audio_dataset_en/para_con/con_long_sin"
OUTPUT_DIR = "api_models/gemini/output_en/para_con/con_long_sin"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === API Configuration ===
GOOGLE_API_KEY = config.API_KEY
client = genai.Client(api_key=GOOGLE_API_KEY)
model = "gemini-2.5-flash-native-audio-preview-09-2025"

# Paraphrasing prompt
config = {
    "response_modalities": ["AUDIO"],
    "realtime_input_config": {
        "automatic_activity_detection": {
            "disabled": True
        }
    },
    "system_instruction":
    "Directly speak the user's requested sentence in the specified tone without any prefix.",
}


# Non-paraphrasing prompt
# from google.genai.types import LiveConnectConfig, RealtimeInputConfig, AutomaticActivityDetection, StartSensitivity, EndSensitivity, Blob

# config = LiveConnectConfig(
#     response_modalities=["AUDIO"],
#     realtime_input_config=RealtimeInputConfig(
#         automatic_activity_detection=AutomaticActivityDetection(
#             disabled=True,  # default
#         )
#     ),
#     system_instruction="You're a great conversationalist, please chat with users in an appropriate tone and keep responses concise and to the point.",
# )
async def main():
    async with client.aio.live.connect(model=model, config=config) as session:

        # Process input directory
        for filename in os.listdir(INPUT_DIR):
            if not filename.endswith(".wav"):
                continue

            input_file = os.path.join(INPUT_DIR, filename)
            output_file = os.path.join(OUTPUT_DIR, filename)

            print(f"--- Processing file: {filename} ---")

            try:
                # Convert WAV to PCM16 RAW
                buffer = io.BytesIO()
                y, sr = librosa.load(input_file, sr=16000)
                sf.write(buffer, y, sr, format='RAW', subtype='PCM_16')
                buffer.seek(0)
                audio_bytes = buffer.read()

                # Send audio
                await session.send_realtime_input(
                    activity_start=types.ActivityStart())
                await session.send_realtime_input(audio=types.Blob(
                    data=audio_bytes, mime_type="audio/pcm;rate=16000"))
                await session.send_realtime_input(
                    activity_end=types.ActivityEnd())

                # Output wav
                wf = wave.open(output_file, "wb")
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)  # Gemini outputs at 24kHz

                async for response in session.receive():
                    if response.data is not None:
                        wf.writeframes(response.data)

                wf.close()
                print(f"Saved: {output_file}")

            except Exception as e:
                print(f"Error processing file: {filename}")
                print(f"Error message: {e}")
                # Ensure file handle is closed on error
                try:
                    wf.close()
                except:
                    pass

    print("--- Batch processing complete ---")


if __name__ == "__main__":
    asyncio.run(main())
