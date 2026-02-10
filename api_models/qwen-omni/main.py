import os
import base64
import numpy as np
import json
import soundfile as sf
from openai import OpenAI
from pathlib import Path

# --- 配置和常量 (Configuration and Constants) ---
# 警告：API 密钥和 Base URL 已从您的原始代码中保留。
# WARNING: API key and Base URL are preserved from your original code.
API_KEY = os.getenv("PARALINGBENCH_QWEN_API_KEY", "")
BASE_URL = os.getenv("PARALINGBENCH_QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
MODEL_NAME = "qwen3-omni-flash"

# 定义批量处理任务的输入和输出目录映射
# Defines the mapping for input and output directories for batch processing
import json as _json
BATCH_TASKS = _json.loads(os.getenv("QWEN_BATCH_TASKS_JSON", _json.dumps([
    (
        "qwen-omni_控制长单en",
        "api_models/qwen-omni/output_en/para_con/控制_长单"
    )
])))

# 初始化OpenAI客户端，使用您指定的配置
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

# --- 辅助函数 (Helper Functions) ---

def encode_audio(audio_path):
    """将本地音频文件编码为 Base64 字符串 (Encodes a local audio file to a Base64 string)."""
    try:
        with open(audio_path, "rb") as audio_file:
            # 检查文件是否为空 (Check if the file is empty)
            audio_file.seek(0, os.SEEK_END)
            if audio_file.tell() == 0:
                print(f"警告: 文件 {audio_path} 为空，跳过。 (Warning: File {audio_path} is empty, skipping.)")
                return None
            audio_file.seek(0)
            return base64.b64encode(audio_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"错误: 找不到文件 {audio_path}。请检查路径。 (Error: File not found {audio_path}. Please check the path.)")
        return None
    except Exception as e:
        print(f"编码文件 {audio_path} 时发生错误: {e} (Error encoding file {audio_path}: {e})")
        return None

def process_audio_file(input_path, output_path):
    """处理单个音频文件：编码、调用API、解码并保存 (Processes a single audio file: encode, call API, decode, and save)."""
    print(f"  > 正在处理文件: {os.path.basename(input_path)}")

    base64_audio = encode_audio(input_path)
    if not base64_audio:
        return

    # 构造 API 请求的消息内容 (Construct the message content for the API request)
    messages_content = [
        {
            "type": "input_audio",
            "input_audio": {
                # 使用 Base64 编码后的数据 (Use the Base64 encoded data)
                "data": f"data:audio/wav;base64,{base64_audio}",
                "format": "wav",
            },
        },
        {
            "type": "text",
            # 保持您原有的指令文本 (Keep your original instruction text)
            "text": "请按照用户的要求，直接用指定的语气生说用户要求的句子，不包含任何前置语句。",
            # "text": "请用合适的语气与用户聊天。",
        },
    ]

    audio_string = ""
    transcript = ""
    
    try:
        # 调用 API (Call the API)
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": messages_content}],
            modalities=["text","audio"],
            audio={"voice": "Cherry", "format": "wav"},
            stream=True,
            stream_options={"include_usage": True},
        )

        # 接收并拼接音频数据和文本转录 (Receive and concatenate audio data and text transcript)
        for chunk in completion:
            if chunk.choices:
                delta = chunk.choices[0].delta
                # 拼接音频数据 (Concatenate audio data)
                if hasattr(delta, "audio") and delta.audio and delta.audio.get("data"):
                    audio_string += delta.audio.get("data", "")
                # 拼接文本转录 (Concatenate text transcript)
                if hasattr(delta, "text") and delta.text:
                    transcript += delta.text
            # 可以选择打印 usage 信息 (Optional: print usage information after completion)
            # else:
            #     print(chunk.usage)

        if audio_string:
            # 解码并保存音频文件 (Decode and save the audio file)
            wav_bytes = base64.b64decode(audio_string)
            # 假设 API 返回的是 24000Hz 采样率的 16 位 PCM 数据 (Assuming API returns 16-bit PCM data at 24000Hz)
            audio_np = np.frombuffer(wav_bytes, dtype=np.int16) 
            
            sf.write(output_path, audio_np, samplerate=24000)
            
            print(f"    - 成功生成音频文件并保存至: {output_path}")
            if transcript:
                print(f"    - 识别/生成的文本内容: {transcript.strip()}")
        else:
            print(f"    - 警告: API响应中没有音频数据，跳过保存。")

    except Exception as e:
        print(f"    - 错误: 调用 API 或保存文件时发生错误: {e}")

# --- 主逻辑 (Main Logic) ---

def process_audio_batch():
    """执行批量音频处理和生成 (Executes batch audio processing and generation)."""
    print("--- 开始批量处理音频文件 (Starting batch audio file processing) ---")

    for input_dir, output_dir in BATCH_TASKS:
        print(f"\n--- 正在处理目录: {input_dir} ---")

        # 1. 确保输出目录存在 (Ensure output directory exists)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        print(f"输出目录已准备好: {output_dir}")

        try:
            # 2. 遍历输入目录中的所有 .wav 文件 (Iterate through all .wav files in the input directory)
            for filename in os.listdir(input_dir):
                if filename.lower().endswith(".wav"):
                    input_path = os.path.join(input_dir, filename)
                    output_path = os.path.join(output_dir, filename)
                    
                    # 3. 处理文件 (Process the file)
                    process_audio_file(input_path, output_path)

        except FileNotFoundError:
            print(f"警告: 输入目录 {input_dir} 不存在。请创建该目录或检查路径是否正确。跳过此任务。")
        except Exception as e:
            print(f"处理目录 {input_dir} 时发生意外错误: {e}")

    print("\n--- 所有批量处理任务已完成 (All batch processing tasks completed) ---")

if __name__ == "__main__":
    process_audio_batch()
