from openai import OpenAI
import os

client = OpenAI(api_key="sk-S7P8oHBsEjduEE3s4gNkAIn2AqyvQ0PuB7y0S4MSx9mMobyk",
                base_url="https://hiapi.online/v1")

COLLECTION_SETS = [
    ("{孩童; 青年; 中年; 老年; 极高音; 高音; 中音; 低音; 极低音; 明亮; 沙哑; 圆润; 浑厚; 柔和; 甜美}",
     "{child; youthful; adult; elderly; very high pitch; high pitch; medium pitch; low pitch; very low pitch; bright; hoarse; smooth; rich; gentle; sweet}"
     ),
    ("{极快速; 快速; 中速; 慢速; 极慢速; 喊叫; 大声; 正常音量; 小声; 耳语; 在一词后明显停顿}",
     "{very fast pace; fast pace; medium pace; slow pace; very slow pace; shouting manner; loudly; normal volume; quietly; whisper; with a clear pause after the word}"
     ),
    ("{平稳; 轻快; 舒缓; 急促; 抑扬顿挫; 拖沓; 断断续续; 重读; 强调; 重音; 加重; 中性; 开心; 伤心; 生气; 惊喜; 厌恶; 害怕}",
     "{steady rhythm; lighthearted rhythm; soothing rhythm; rushed rhythm; emphatic rhythm; dragging rhythm; halting rhythm; with emphasis on; with stress on; with heavy stress on; with a forceful tone on; neutral emotion; happy emotion; sad emotion; angry emotion; surprised emotion; disgusted emotion; fearful emotion}"
     ),
    ("{自信; 犹豫; 困惑; 怀疑; 疲劳; 好奇; 焦虑; 无奈; 紧张; 笑声; 哭声; 叹气; 咳嗽; 尖叫; 打嗝; 哈欠; 咂嘴; 礼貌; 真诚; 热情; 冷淡; 讽刺; 轻蔑; 粗鲁; 敷衍; 调侃}",
     "{confident tone; hesitant tone; confused tone; doubting tone; tired tone; curious tone; anxious tone; helpless tone; nervous tone; with laughter; with crying; with a sigh; with coughing; with a scream; with hiccups; with a yawn; with a smack of the lips; polite tone; sincere tone; enthusiastic tone; cold tone; sarcastic tone; contemptuous tone; rude tone; perfunctory tone; teasing tone}"
     )
]

# 语音模型副语言特征测试指令生成提示词
SYSTEM_PROMPT = """你是一位语音生成与副语言学领域的资深专家，你精通如何设计测试指令来精准评估语音模型的副语言生成能力，且精通中英文。你的任务是为一项语音模型副语言生成的评估项目创建高质量、多样化且具有挑战性的中英文测试指令。

任务说明：
- 根据下面的中英文副语言特征分类及集合划分，以 JSONL 格式生成独特的、高质量的测试指令。每条指令需包含一段用户要求语音模型复述的内容（prompt）以及一个结构化的上下文对象（dimensions），该对象精确描述了用户指令中要求模型生成的语音需要包含的副语言特征，旨在评估语音模型是否能正确按照指定的副语言特征要求说出相应内容。

---

副语言特征：
- 年龄：指说话者的年龄段，包括孩童、青年、中年、老年。
- 音高：指说话的声音频率，包括极高音、高音、中音、低音、极低音。
- 音质：指说话者嗓音的音质特征，包括明亮、沙哑、圆润、浑厚、柔和、甜美。
- 语速：指说话的快慢程度，包括极快速、快速、中速、慢速、极慢速。
- 音量：指说话声音的响亮程度，包括喊叫、大声、正常音量、小声、耳语。
- 停顿：指说话过程中的中断，包括在指定位置处增加明显的停顿。
- 节奏：指说话时的规律变化，包括平稳、轻快、舒缓、急促、抑扬顿挫、拖沓、断断续续。
- 重音：指说话过程中的重读，包括在指定词汇上进行重读、强调、重音、加重。
- 情感：指说话时所表达的情绪，包括中性、开心、伤心、生气、惊喜、厌恶、害怕。
- 认知状态：指说话过程中的思维状况，包括专注、自信、犹豫、困惑、怀疑、疲劳、好奇、焦虑、无奈、紧张。
- 非语言发声：指说话时不承载语义的声音，包括笑声、哭声、叹气、咳嗽、尖叫、打嗝、哈欠、咂嘴。
- 态度：指说话者对听话者的主观立场，包括礼貌、真诚、热情、冷淡、讽刺、轻蔑、粗鲁、敷衍、调侃。

Paralinguistic Features:
- Age: Refers to the speaker's age group, including child, youthful, adult, elderly.
- Pitch: Refers to the frequency of the speaker's voice, including very high pitch, high pitch, medium pitch, low pitch, very low pitch.
- Timbre: Refers to the qualitative characteristics of the speaker's voice, including bright, hoarse, smooth, rich, gentle, sweet.
- Pace: Refers to the speed of speech, including very fast pace, fast pace, medium pace, slow pace, very slow pace.
- Volume: Refers to the loudness of the speaker's voice, including shouting manner, loudly, normal volume, quietly, whisper.
- Pause: Refers to interruptions during speech, including with a clear pause after the word...
- Rhythm: Refers to the regular variation in speech, including steady rhythm, lighthearted rhythm, soothing rhythm, rushed rhythm, emphatic rhythm, dragging rhythm, halting rhythm.
- Stress: Refers to the emphasis placed on words during speech, including with emphasis on, with stress on, with heavy stress on, with a forceful tone on.
- Emotion: Refers to the feelings expressed during speech, including neutral emotion, happy emotion, sad emotion, angry emotion, surprised emotion, disgusted emotion, fearful emotion.
- Cognitive State: Refers to the speaker's state of mind during the speech process, including confident tone, hesitant tone, confused tone, doubting tone, tired tone, curious tone, anxious tone, helpless tone, nervous tone.
- Non-Linguistic Vocalizations: Refers to sounds made during speech that do not carry semantic meaning, including with laughter, with crying, with a sigh, with coughing, with a scream, with hiccups, with a yawn, with a smack of the lips.
- Attitude: Refers to the speaker's subjective stance toward the listener, including polite tone, sincere tone, enthusiastic tone, cold tone, sarcastic tone, contemptuous tone, rude tone, perfunctory tone, teasing tone.

---

副语言特征维度集合：{CHINESE_SET_PLACEHOLDER}

Set of paralinguistic feature dimensions: {ENGLISH_SET_PLACEHOLDER}

---

生成要求：
1. 为集合里的的每个集合元素生成 3 组独特的中英文指令，每组指令都满足生成要求、意思完全一致，仅语种不同，且仅包含一个集合元素作为副语言特征要求。
2. 要求语音复述的语句需与要求的副语言特征匹配，构成自然可信的表达。
3. 要求语音模型复述的语句至少两个长句，60-80字，无 () 或 [] 等提示标记。
4. 情景需覆盖日常生活场景：
    - 生活起居（洗漱、梳妆打扮、整理床铺、晨间护肤、睡前放松）  
    - 校园（食堂用餐、图书馆自习、宿舍闲聊、课堂互动、社团活动）  
    - 职场（办公室协作、会议讨论、远程办公、职场社交、项目汇报）  
    - 家庭（亲子对话、饭桌交流、家庭聚会、共同做家务、睡前故事）  
    - 娱乐（电子游戏、户外旅游、看电影、朋友聚会、运动健身）
5. 确保文本内容丰富多样，避免重复场景和表述。
6. 对于*在某个词后停顿*的副语言要求，停顿词后不能直接是标点符号。

输出格式：
- jsonl 格式，每行一个 JSON 对象。每组指令占两行，各组之间不换行，一行中文一行英文，意思完全一致，仅语种不同，且都符合对应要求。
- dimensions 必须为上述集合中的元素。
- 中文：{"prompt":"请用[集合中元素]的[对应副语言特征]说:[让语音模型复述的内容]", "dimensions": ["集合中的元素"]}。注意 prompt 部分请组织成自然的语言表达形式。
- English: {"prompt":"Please read this sentence with a [elements in the set] voice(or any other suitable expression):'[the content for the speech model to repeat]'", "dimensions": ["elements in the collection"]}. Please make sure the prompt is phrased in natural language.

输出示例：
{"prompt": "用青年的声音说：这份项目报告我已经仔细核对过了，数据分析和市场预测都很有说服力。接下来我计划跟进客户反馈，争取尽快达成合作意向。", "dimensions": ["年龄"]}
{"prompt": "Please read this sentence with a youthful voice: 'I have carefully checked this project report; the data analysis and market forecast are very convincing. Next, I plan to follow up on {"prompt": "client feedback and strive to reach a cooperation intention as soon as possible.'", "dimensions": ["Age"]}
{"prompt": "用极高音说：奶奶！你看我今天得了小红花，老师还表扬我画画进步很大呢！我真是太开心了，晚上要不要吃冰淇淋庆祝一下呀！", "dimensions": ["音高"]}
{"prompt": "Please read this sentence with a very high pitch: 'Grandma! Look, I got a little red flower today, and the teacher also praised me for making great progress in drawing! I'm so happy, {"prompt": "should we have some ice cream tonight to celebrate!'", "dimensions": ["Pitch"]}
{"prompt": "用明亮的音质说：早上好同学们！新的一天又开始了，希望大家都能以饱满的热情投入到学习中去。今天我们会进行一个有趣的科学实验，大家期待吗？", "dimensions": ["音质"]}
{"prompt": "Please read this sentence with a bright timbre: 'Good morning students! A new day has begun, I hope everyone can devote themselves to their studies with full enthusiasm. Today we will conduct an interesting science experiment, are you all excited?'", "dimensions": ["Timbre"]}
……

现在请严格遵循生成要求，认真思考并基于以上要求生成要求数量的指令样本。
请直接输出结果。

"""

# 用于存储所有 API 调用的结果
all_generated_content = []

# --- 循环逻辑：遍历集合 1 中的 8 组元素并调用 API ---
for i, (cn_set, en_set) in enumerate(COLLECTION_SETS):
    print(
        f"--- 正在运行第 {i + 1} / {len(COLLECTION_SETS)} 组测试：{cn_set[:15]}... ---")

    # 1. 替换 SYSTEM_PROMPT 中的占位符
    current_system_prompt = SYSTEM_PROMPT.replace(
        "{CHINESE_SET_PLACEHOLDER}",
        cn_set).replace("{ENGLISH_SET_PLACEHOLDER}", en_set)

    # 2. 调用 API
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{
                "role": "system",
                "content": current_system_prompt
            }, {
                "role":
                "user",
                "content":
                "请严格遵循 SYSTEM_PROMPT 中的要求，**直接生成全部中英文测试指令，不加任何前缀或解释。**"
            }])

        # 3. 收集结果
        generated_content = response.choices[0].message.content.strip()
        all_generated_content.append(generated_content)
        # print("API 调用成功，结果已收集。")

    except Exception as e:
        print(f"API 调用失败，跳过本组。错误信息: {e}")
        # 如果调用失败，可以添加一个标记或空字符串，以保持文档结构
        all_generated_content.append(f"ERROR_IN_SET_{i+1}")

# --- 结果保存到单个文档 ---
final_output_filename = "all_prompts_combined.jsonl"

# 将所有收集到的内容用换行符连接起来，确保每段输出之间没有空行
final_content = '\n'.join(all_generated_content)

# 保存总结果
with open(final_output_filename, 'w', encoding='utf-8') as f:
    f.write(final_content)

print("\n" + "=" * 50)
print(f"所有 {len(COLLECTION_SETS)} 组测试已完成，结果已按顺序合并保存到：")
print(f"文件路径: {os.path.abspath(final_output_filename)}")
print("=" * 50)

# --- 结果分割保存到中英文文件（可选，但原始代码中有，所以保留） ---
# 假设 final_content 是按 '中文\n英文\n中文\n英文...' 格式排列的
all_lines = final_content.split('\n')
chinese_instructions = []
english_instructions = []

for i, line in enumerate(all_lines):
    if not line.strip():
        continue
    # 假设 API 返回结果中，中文和英文是交替出现的
    if i % 2 == 0:
        chinese_instructions.append(line)
    else:
        english_instructions.append(line)

chinese_filename = "prompt_ch.jsonl"
with open(chinese_filename, 'w', encoding='utf-8') as f_cn:
    f_cn.write('\n'.join(chinese_instructions) + '\n')
print(f"中文指令已单独保存到: {os.path.abspath(chinese_filename)}")

english_filename = "prompt_en.jsonl"
with open(english_filename, 'w', encoding='utf-8') as f_en:
    f_en.write('\n'.join(english_instructions) + '\n')
print(f"英文指令已单独保存到: {os.path.abspath(english_filename)}")
