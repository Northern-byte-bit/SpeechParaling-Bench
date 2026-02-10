# pip install websocket-client
import json
import websocket
import os
import base64
import wave

# -------------------------------
# 1. 配置
# -------------------------------
import json
BATCH_TASKS = json.loads(os.getenv("QWEN_REALTIME_BATCH_TASKS_JSON", json.dumps([
    (
        # "audio_dataset_ch/dyn_var",
        "realtime_adj_ch",
        "api_models/qwen-omni-realtime/output_ch/dyn_var"
    ),
    # (
    #     "audio_dataset_ch/para_con/控制_抽象",
    #     "api_models/qwen-omni-realtime/output_ch/para_con/控制_抽象"
    # ),
    (
        # "audio_dataset_ch/para_con/控制_短单",
        "realtime_short_sin_ch",
        "api_models/qwen-omni-realtime/output_ch/para_con/控制_短单"
    ),
    # (
    #     "audio_dataset_ch/para_con/控制_短多",
    #     "api_models/qwen-omni-realtime/output_ch/para_con/控制_短多"
    # ),
    # (
    #     "audio_dataset_ch/para_con/控制_长单",
    #     "api_models/qwen-omni-realtime/output_ch/para_con/控制_长单"
    # ),
    # (
    #     "audio_dataset_ch/para_con/控制_长多",
    #     "api_models/qwen-omni-realtime/output_ch/para_con/控制_长多"
    # ),
    (
        # "audio_dataset_en/dyn_var",
        "realtime_adj_en",
        "api_models/qwen-omni-realtime/output_en/dyn_var"
    ),
    # (
    #     # "audio_dataset_en/para_con/控制_抽象",
    #     "realtime_abs_en",
    #     "api_models/qwen-omni-realtime/output_en/para_con/控制_抽象"
    # ),
    # (
    #     "audio_dataset_en/para_con/控制_短单",
    #     "api_models/qwen-omni-realtime/output_en/para_con/控制_短单"
    # ),
    # (
    #     "audio_dataset_en/para_con/控制_短多",
    #     "api_models/qwen-omni-realtime/output_en/para_con/控制_短多"
    # ),
    # (
    #     "audio_dataset_en/para_con/控制_长单",
    #     "api_models/qwen-omni-realtime/output_en/para_con/控制_长单"
    # ),
    (
        # "audio_dataset_en/para_con/控制_长多",
        "realtime_long_multi_en",
        "api_models/qwen-omni-realtime/output_en/para_con/控制_长多"
    ),
    # (
    #     "audio_dataset_ch/sit_ada/适应_单维度",
    #     "api_models/qwen-omni-realtime/output/sit_ada/适应_单维度"
    # ),
    # (
    #     "audio_dataset_ch/sit_ada/适应_多维度",
    #     "api_models/qwen-omni-realtime/output/sit_ada/适应_多维度"
    # ),
    # (
    #     "audio_dataset_en/sit_ada/适应_单维度",
    #     "api_models/qwen-omni-realtime/output_en/sit_ada/适应_单维度"
    # ),
    # (
    #     "audio_dataset_en/sit_ada/适应_多维度",
    #     "api_models/qwen-omni-realtime/output_en/sit_ada/适应_多维度"
    # ),
    # 可以继续添加更多任务
]))

API_KEY = os.getenv("PARALINGBENCH_QWEN_REALTIME_API_KEY", "")
API_URL = os.getenv("QWEN_REALTIME_API_URL", "wss://dashscope.aliyuncs.com/api-ws/v1/realtime?model=qwen3-omni-flash-realtime")

HEADERS = [
    "Authorization: Bearer " + API_KEY
]

# -------------------------------
# 2. 工具函数
# -------------------------------
def wav_to_pcm16_chunks(wav_path, chunk_samples=3200):
    chunks = []
    with wave.open(wav_path, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2      # PCM16

        while True:
            data = wf.readframes(chunk_samples)
            if not data:
                break
            chunks.append(data)
    return chunks


def save_output_audio(output_path, frames):
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)   # pcm16
        wf.setframerate(24000)
        wf.writeframes(b"".join(frames))


# -------------------------------
# 3. 单文件处理函数
# -------------------------------
def process_one_wav(input_path, output_path):
    output_frames = []

    def on_open(ws):
        # session 初始化
        ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": "Cherry",
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "instructions": "请按照用户的要求，直接用指定的语气生说用户要求的句子，不包含任何前置语句和其它内容。",
                # "instructions": "请用合适的语气与用户聊天。",
                "turn_detection": None
            }
        }))

        # 发送音频
        pcm_chunks = wav_to_pcm16_chunks(input_path)
        for chunk in pcm_chunks:
            ws.send(json.dumps({
                "type": "input_audio_buffer.append",
                "audio": base64.b64encode(chunk).decode()
            }))

        ws.send(json.dumps({
            "type": "input_audio_buffer.commit"
        }))

    def on_message(ws, message):
        data = json.loads(message)
        t = data.get("type")

        if t == "input_audio_buffer.committed":
            ws.send(json.dumps({
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

    ws = websocket.WebSocketApp(
        API_URL,
        header=HEADERS,
        on_open=on_open,
        on_message=on_message
    )

    ws.run_forever()


# -------------------------------
# 4. 批量遍历
# -------------------------------
for input_dir, output_dir in BATCH_TASKS:
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n=== 开始处理文件夹: {input_dir} ===")

    for filename in os.listdir(input_dir):
        if not filename.endswith(".wav"):
            continue

        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        print(f"\n--- 正在处理: {filename} ---")
        process_one_wav(input_path, output_path)
        print(f"✅ 完成: {output_path}")

print("\n--- 所有文件夹处理完成 ---")
