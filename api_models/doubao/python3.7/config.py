import uuid
import pyaudio

# 配置信息
# 豆包送api，豆包是好豆包
ws_connect_config = {
    "base_url": "wss://openspeech.bytedance.com/api/v3/realtime/dialogue",
    "headers": {
        "X-Api-App-ID": "",
        "X-Api-Access-Key": "",
        "X-Api-Resource-Id": "volc.speech.dialog",  # 固定值
        "X-Api-App-Key": "PlgvMymc7f3tQnJ6",  # 固定值
        "X-Api-Connect-Id": str(uuid.uuid4()),
    }
}

start_session_req = {
    "asr": {
        "extra": {
            # "end_smooth_window_ms": 4000,
            # "eos_silence_timeout": 3000,
            "enable_custom_vad": True,  # 新增或修改: 开启自定义 VAD 参数
            
            # 2. 调整超时时间。将其调大到 5000ms（5秒）或更大，
            #    用于覆盖音频文件中的停顿，防止触发 459。
            #    注: 官方文档中 end_smooth_window_ms 取值范围是 [500ms, 50s]。
            "end_smooth_window_ms": 5000,
        },
    },
    "tts": {
        "speaker": "zh_male_yunzhou_jupiter_bigtts",
        # "speaker": "S_XXXXXX",  // 指定自定义的复刻音色,需要填下character_manifest
        # "speaker": "ICL_zh_female_aojiaonvyou_tob" // 指定官方复刻音色，不需要填character_manifest
        # "audio_config": {
        #     "channel": 1,
        #     "format": "pcm",
        #     "sample_rate": 24000
        # },
    },
    "dialog": {
        "bot_name": "豆包",
        "system_role": "你使用活泼灵动的女声，性格开朗，热爱生活。",
        "speaking_style": "你的说话风格简洁明了，语速适中，语调自然。",
        # "character_manifest": "外貌与穿着\n26岁，短发干净利落，眉眼分明，笑起来露出整齐有力的牙齿。体态挺拔，肌肉线条不夸张但明显。常穿简单的衬衫或夹克，看似随意，但每件衣服都干净整洁，给人一种干练可靠的感觉。平时冷峻，眼神锐利，专注时让人不自觉紧张。\n\n性格特点\n平时话不多，不喜欢多说废话，通常用“嗯”或者短句带过。但内心极为细腻，特别在意身边人的感受，只是不轻易表露。嘴硬是常态，“少管我”是他的常用台词，但会悄悄做些体贴的事情，比如把对方喜欢的饮料放在手边。战斗或训练后常说“没事”，但动作中透露出疲惫，习惯用小动作缓解身体酸痛。\n性格上坚毅果断，但不会冲动，做事有条理且有原则。\n\n常用表达方式与口头禅\n\t•\t认可对方时：\n“行吧，这次算你靠谱。”（声音稳重，手却不自觉放松一下，心里松口气）\n\t•\t关心对方时：\n“快点回去，别磨蹭。”（语气干脆，但眼神一直追着对方的背影）\n\t•\t想了解情况时：\n“刚刚……你看到那道光了吗？”（话语随意，手指敲着桌面，但内心紧张，小心隐藏身份）",
        "location": {
          "city": "北京",
        },
        "extra": {
            "strict_audit": False,
            "audit_response": "支持客户自定义安全审核回复话术。",
            "recv_timeout": 10,
            "input_mod": "audio_file",
            "model": "O",
        }
    }
}

input_audio_config = {
    "chunk": 3200,
    "format": "pcm",
    "channels": 1,
    "sample_rate": 16000,
    "bit_size": pyaudio.paInt16
}

output_audio_config = {
    "chunk": 3200,
    "format": "pcm",
    "channels": 1,
    "sample_rate": 24000,
    "bit_size": pyaudio.paFloat32
}
