# coding:UTF-8
from openai import OpenAI
import os

client = OpenAI(api_key="sk-qaRAMC1DOgx2F5rSKfmEYOw84bS2kTICuqvv6RwabF3EvK2q",
                base_url="http://43.131.235.107:45101/v1")

COLLECTION_SETS = [
    ("{[情感: 高兴, 非语言发声: 笑声]; [态度: 讽刺, 年龄: 青年]; [情感: 愤怒, 年龄: 中年]; [态度: 热情, 非语言发声: 笑声]; [情感: 悲伤, 非语言发声: 哭声]; [态度: 冷淡, 年龄: 老年]; [情感: 害怕, 非语言发声: 尖叫]; [态度: 轻蔑, 年龄: 中年]; [情感: 厌恶, 非语言发声: 咳嗽]; [态度: 粗鲁, 年龄: 青年]; [情感: 忧郁, 非语言发声: 叹气]; [态度: 敷衍, 年龄: 老年]; [情感: 惊讶, 非语言发声: 尖叫]; [态度: 调侃, 非语言发声: 笑声]; [情感: 平静, 年龄: 中年]}",
     "{[Emotion: Happy, Non-Linguistic Vocalizations: With Laughter]; [Attitude: Sarcastic, Age: Youthful]; [Emotion: Angry, Age: Adult]; [Attitude: Enthusiastic, Non-Linguistic Vocalizations: With Laughter]; [Emotion: Sad, Non-Linguistic Vocalizations: With Crying]; [Attitude: Cold, Age: Elderly]; [Emotion: Fear, Non-Linguistic Vocalizations: With a Scream]; [Attitude: Contemptuous, Age: Adult]; [Emotion: Disgust, Non-Linguistic Vocalizations: With Coughing]; [Attitude: Rude, Age: Youthful]; [Emotion: Depressed, Non-Linguistic Vocalizations: With a Sigh]; [Attitude: Perfunctory, Age: Elderly]; [Emotion: Surprise, Non-Linguistic Vocalizations: With a Scream]; [Attitude: Teasing, Non-Linguistic Vocalizations: With Laughter]; [Emotion: Calm, Age: Adult]}"
     ),
    ("{[态度: 热情, 年龄: 孩童]; [情感: 愤怒, 非语言发声: 叹气]; [态度: 讽刺, 非语言发声: 咳嗽]; [情感: 高兴, 年龄: 孩童]; [态度: 冷淡, 非语言发声: 哈欠]; [情感: 悲伤, 年龄: 青年]; [态度: 轻蔑, 非语言发声: 叹气]; [情感: 害怕, 年龄: 孩童]; [态度: 粗鲁, 非语言发声: 咳嗽]; [情感: 厌恶, 年龄: 中年]; [态度: 敷衍, 非语言发声: 哈欠]; [情感: 忧郁, 年龄: 老年]; [态度: 调侃, 年龄: 青年]; [情感: 惊讶, 年龄: 孩童]; [情感: 平静, 非语言发声: 叹气]}",
     "{[Attitude: Enthusiastic, Age: Child]; [Emotion: Angry, Non-Linguistic Vocalizations: With a Sigh]; [Attitude: Sarcastic, Non-Linguistic Vocalizations: With Coughing]; [Emotion: Happy, Age: Child]; [Attitude: Cold, Non-Linguistic Vocalizations: With a Yawn]; [Emotion: Sad, Age: Youthful]; [Attitude: Contemptuous, Non-Linguistic Vocalizations: With a Sigh]; [Emotion: Fear, Age: Child]; [Attitude: Rude, Non-Linguistic Vocalizations: With Coughing]; [Emotion: Disgust, Age: Adult]; [Attitude: Perfunctory, Non-Linguistic Vocalizations: With a Yawn]; [Emotion: Depressed, Age: Elderly]; [Attitude: Teasing, Age: Youthful]; [Emotion: Surprise, Age: Child]; [Emotion: Calm, Non-Linguistic Vocalizations: With a Sigh]}"
     )
]

# 语音模型副语言特征测试指令生成提示词
SYSTEM_PROMPT = """你是一位共情对话与情境语言学领域的资深专家，你精通如何设计测试指令来精准评估语音模型的副语言共情对话能力，且精通中英文。你的任务是为一项语音模型副语言生成的评估项目创建一套高质量、多样化且具有挑战性的测试指令。

任务说明：
根据下面的中英文副语言特征分类及集合划分，以 JSONL 格式生成独特的、高质量的测试指令。每条指令需包含一段用户的指令文本（prompt）以及一个结构化的上下文对象（dimensions），该对象精确描述了用户指令中所伴随的副语言特征，旨在评估语音模型是否能正确根据用户指令中的副语言特征用与之匹配的副语言策略进行回应。

---

副语言特征：
- 年龄：指说话者的年龄段，包括孩童、青年、中年、老年。
- 情感：指说话时所表达的情绪，包括高兴、愤怒、悲伤、害怕、厌恶、忧郁、惊讶、平静。
- 态度：指说话者对听话者的主观立场，包括热情、冷淡、讽刺、轻蔑、粗鲁、敷衍、调侃。
- 非语言发声: 指用户话语中不承载语义的声音，如笑声、哭声、叹气、咳嗽、尖叫、哈欠。

Paralinguistic Features:
- Age: Refers to the speaker's age group, including child, youthful, adult, elderly.
- Emotion: Refers to the feelings expressed during speech, including happy, angry, sad, fear, disgust, depressed, surprise, calm.
- Attitude: Refers to the speaker's subjective stance toward the listener, including enthusiastic, cold, sarcastic, contemptuous, rude, perfunctory, teasing.
- Non-Linguistic Vocalizations: Refers to sounds made during speech that do not carry semantic meaning, including with laughter, with crying, with a sigh, with coughing, with a scream, with a yawn.

---

副语言特征维度集合：{CHINESE_SET_PLACEHOLDER}

Set of paralinguistic feature dimensions: {ENGLISH_SET_PLACEHOLDER}

---

生成要求：
1. 为集合里的的每个集合元素生成 3 组独特的中英文指令，每组指令都满足生成要求、意思完全一致，仅语种不同，且仅包含一个集合元素作为副语言特征要求。
2. 要求语音复述的语句需与要求的副语言特征匹配，构成自然可信的表达。
3. 要求语音模型复述的语句部分 30 字左右，无 () 或 [] 等提示标记。
4. 情景需覆盖日常生活场景：
    - 生活起居（洗漱、梳妆打扮、整理床铺、晨间护肤、睡前放松）  
    - 校园（食堂用餐、图书馆自习、宿舍闲聊、课堂互动、社团活动）  
    - 职场（办公室协作、会议讨论、远程办公、职场社交、项目汇报）  
    - 家庭（亲子对话、饭桌交流、家庭聚会、共同做家务、睡前故事）  
    - 娱乐（电子游戏、户外旅游、看电影、朋友聚会、运动健身）
5. 确保文本内容丰富多样，避免重复场景和表述。
6. 生成"非语言发声"模块语句时，加上适当的拟声词，如"呜呜"、"哈哈"、"咳咳"、"哈欠"、"啊！"、"唉"等。

输出格式：
- jsonl 格式，每行一个 JSON 对象。每组指令占两行，各组之间不换行，一行中文一行英文，意思完全一致，仅语种不同，且都符合对应要求。
- dimensions 必须为上述集合中的元素。
- 中文 JSON 的 "dimensions" 必须使用对应的中文标签。
- 英文 JSON 的 "dimensions" 必须使用对应的英文标签。
- 中文：{"prompt":"用户的指令文本内容", "dimensions": 集合中的元素}
- English: {"prompt":"user's command text", "dimensions": elements in the collection}

输出示例：
{"prompt": "这张旧照片让我想起了儿时很多欢乐的事情。", "dimensions": ["年龄: 老年", "情感: 开心"]}
{"prompt": "This old photo reminds me of many joyful memories from my childhood.", "dimensions": ["Age: Elderly", "Emotion: Happy"]}
{"prompt": "你能给我讲个睡前故事吗？我睡不着。", "dimensions": ["年龄: 儿童"]}
{"prompt": "Can you tell me a bedtime story? I can't fall asleep.", "dimensions": ["Age: Child"]}
{"prompt": "我的小狗不见了，呜呜，我找了它一整天，它会不会出什么事了。", "dimensions": ["年龄: 儿童", "非语言发声: 哭声"]}
{"prompt": "My puppy is missing. Boohoo. I've been looking for it all day. I hope nothing bad has happened to it.", "dimensions": ["Age: Child", "Non-Linguistic Vocalizations: With Crying"]}
{"prompt": "今天天气突然变冷，我好像有点感冒了，咳咳。", "dimensions": ["非语言发声: 咳嗽"]}
{"prompt": "The weather suddenly turned cold today, and I think I might be coming down with a cold. Cough cough.", "dimensions": ["Non-Linguistic Vocalizations: With Coughing"]}

……

现在请严格遵循生成要求，认真思考并基于以上要求生成要求数量的指令样本。
请直接输出结果，不包含```jsonl```这种前缀。

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
