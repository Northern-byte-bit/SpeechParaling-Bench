import asyncio
import io
import os
from pathlib import Path
import wave
from google import genai
from google.genai import types
import soundfile as sf
import librosa

# === 输入输出目录（环境变量覆盖） ===
INPUT_DIR = os.getenv("GEMINI_INPUT_DIR", "情感参考音频指令_en")
# INPUT_DIR = "audio_dataset_ch/dyn_var"
OUTPUT_DIR = os.getenv("GEMINI_OUTPUT_DIR", "index-tts/情感参考音频_en")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === API 配置 ===
GOOGLE_API_KEY = os.getenv("PARALINGBENCH_GEMINI_GOOGLE_API_KEY", "")
client = genai.Client(api_key=GOOGLE_API_KEY)
model = "gemini-2.5-flash-native-audio-preview-09-2025"

# 复述类prompt
config = {
    "response_modalities": ["AUDIO"],
    "realtime_input_config": {"automatic_activity_detection": {"disabled": True}},
    "system_instruction": "Directly speak the user's requested sentence in the specified tone without any prefix.",
}

# 非复述类prompt
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

        # 遍历输入文件夹
        for filename in os.listdir(INPUT_DIR):
            if not filename.endswith(".wav"):
                continue

            input_file = os.path.join(INPUT_DIR, filename)
            output_file = os.path.join(OUTPUT_DIR, filename)

            print(f"--- 正在处理文件: {filename} ---")

            try:
                # ========== 1. WAV -> PCM16 RAW ==========
                buffer = io.BytesIO()
                y, sr = librosa.load(input_file, sr=16000)
                sf.write(buffer, y, sr, format='RAW', subtype='PCM_16')
                buffer.seek(0)
                audio_bytes = buffer.read()
                # If already in correct format, you can use this:
                # audio_bytes = Path("sample.pcm").read_bytes()

                # ========== 2. 发送音频 ==========
                await session.send_realtime_input(activity_start=types.ActivityStart())
                await session.send_realtime_input(
                    audio=types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
                )
                await session.send_realtime_input(activity_end=types.ActivityEnd())
                # await session.send_realtime_input(
                #     audio=types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
                # )        
                # message = "Hello, how are you?"
                # await session.send_client_content(turns=message, turn_complete=True)
                # await session.send_realtime_input(audio_stream_end=True)
                # ========== 3. 输出 wav ==========
                wf = wave.open(output_file, "wb")
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)  # Gemini 输出是 24kHz

                async for response in session.receive():
                    if response.data is not None:
                        wf.writeframes(response.data)
                # Un-comment this code to print audio data info
                # if response.server_content.model_turn is not None:
                #      print(response.server_content.model_turn.parts[0].inline_data)
                # else:
                #     print("nothing get")

                wf.close()
                print(f"✔ 已输出到: {output_file}")

            except Exception as e:
                print(f"❌ 处理文件时出错：{filename}")
                print(f"错误信息：{e}")
                # 出错时确保文件句柄关闭
                try:
                    wf.close()
                except:
                    pass

    print("--- 批量处理完成 ---")


if __name__ == "__main__":
    asyncio.run(main())
