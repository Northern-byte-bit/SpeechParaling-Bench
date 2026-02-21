import http.client
import json
import base64
import os

# -------------------------------
# 1. 配置
# -------------------------------
INPUT_DIR = "audio_dataset_en/para_con/con_long_sin"
OUTPUT_DIR = "api_models/gpt/output_en/para_con/con_long_sin"

API_HOST = ""
API_PATH = ""
API_KEY = ""

MODEL_NAME = "gpt-audio-2025-08-28"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------
# 2. 遍历输入目录
# -------------------------------
for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".wav"):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    print(f"\n--- 正在处理文件: {filename} ---")

    try:
        # -------------------------------
        # 3. 读取 wav
        # -------------------------------
        with open(input_path, "rb") as f:
            wav_data = f.read()

        print(f"原始 wav 大小: {len(wav_data) / 1024:.2f} KB")

        # -------------------------------
        # 4. Base64 编码
        # -------------------------------
        encoded_wav = base64.b64encode(wav_data).decode("utf-8")
        print(f"Base64 编码长度: {len(encoded_wav)}")

        # -------------------------------
        # 5. 构造请求
        # -------------------------------
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
                "content": [
                    {
                        "type":
                        "text",
                        "text":
                        "Directly speak the user's requested sentence in the specified tone without any prefix."
                        # "text": "Please chat with users in an appropriate tone and keep responses concise and to the point."
                    },
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": encoded_wav,
                            "format": "wav"
                        }
                    }
                ]
            }]
        })

        headers = {
            "Authorization": API_KEY,
            "Content-Type": "application/json"
        }

        # -------------------------------
        # 6. 发送请求
        # -------------------------------
        conn = http.client.HTTPSConnection(API_HOST, timeout=60)
        conn.request("POST", API_PATH, payload, headers)

        res = conn.getresponse()
        raw = res.read().decode("utf-8")
        conn.close()

        # -------------------------------
        # 7. 解析返回
        # -------------------------------
        resp = json.loads(raw)

        text_reply = resp["choices"][0]["message"].get("content", [])
        print("文本回复：", text_reply)

        audio_info = resp["choices"][0]["message"].get("audio")

        # -------------------------------
        # 8. 保存音频
        # -------------------------------
        if audio_info and "data" in audio_info:
            audio_bytes = base64.b64decode(audio_info["data"])

            with open(output_path, "wb") as f:
                f.write(audio_bytes)

            print(f"✅ 音频已保存为: {output_path}")
        else:
            print(f"⚠️ 返回中没有 audio 字段，文件：{filename}")

    except Exception as e:
        print(f"❌ 处理文件 {filename} 时发生错误: {e}")

print("\n--- 批量处理完成 ---")
