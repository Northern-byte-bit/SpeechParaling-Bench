# coding:UTF-8
from openai import OpenAI
import os
# client = OpenAI(api_key="",

client = OpenAI(api_key="", base_url="https://hiapi.online/v1")

COLLECTION_SETS = [
    ("{先用极低音开始，然后逐渐转变为中音说; 先用高音开始，然后突然降低音高用极低音说; 先用中音开始，然后逐渐提高音高用极高音说; 先用极高音开始，然后逐渐降低到低音说; 先用低音开始，然后突然跳跃到高音说; 先用圆润的音质开始，然后逐渐变得沙哑说; 先用柔和的音质开始，然后突然转变为明亮说; 先用浑厚的音质开始，然后逐渐变得甜美说; 先用明亮的音质开始，然后逐渐转变为浑厚说; 先用甜美的音质开始，然后突然变得沙哑说}",
     "{Start with a very low pitch and gradually transition to a medium pitch; Start with a high pitch and suddenly drop the pitch, using a very low pitch; Start with a medium pitch and gradually raise the pitch, using a very high pitch; Start with a very high pitch and gradually lower the pitch to a low pitch; Start with a low pitch and suddenly jump to a high pitch; Start with a smooth timbre and gradually become hoarse; Start with a gentle timbre and suddenly switch to a bright timbre; Start with a rich timbre and gradually become sweet; Start with a bright timbre and gradually transition to a rich timbre; Start with a sweet timbre and suddenly become hoarse}"
     ),
    ("{先用极慢速开始，然后逐渐提高语速用中速说; 先用快速开始，然后突然转变为极慢速说; 先用中速开始，然后逐渐提高语速用极快速说; 先用极快速开始，然后逐渐放慢到慢速说; 先用慢速开始，然后突然提速到快速说; 先用耳语开始，然后逐渐提高音量到正常音量说; 先用正常音量开始，然后突然提高音量喊叫着说; 先用大声开始，然后突然转变为小声说; 先用喊叫开始，然后逐渐减弱到耳语说; 先用小声开始，然后逐渐增强到大声说}",
     "{Start with a very slow pace and gradually increase the pace to a medium pace; Start with a fast pace and suddenly switch to a very slow pace; Start with a medium pace and gradually increase the pace to a very fast pace; Start with a very fast pace and gradually slow down to a slow pace; Start with a slow pace and suddenly speed up to a fast pace; Start with a whisper and gradually increase the volume to a normal volume; Start with a normal volume and suddenly increase the volume, shouting manner; Start loudly and suddenly switch to quietly; Start with a shouting manner and gradually decrease the volume to a whisper; Start quietly and gradually increase the volume to loudly}"
     ),
    ("{先用舒缓的节奏开始，然后逐渐转变为轻快说; 先用平稳的节奏开始，然后突然变得拖沓说; 先用急促的节奏开始，然后突然转变为断续说; 先用断续的节奏开始，然后逐渐变得抑扬顿挫说; 先用轻快的节奏开始，然后突然转变为平稳说; 先用开心的语气开始，然后突然转变为伤心的情感说; 先用中性的语气开始，然后逐渐转变为生气的状态说; 先用害怕的语气开始，然后逐渐转变为惊喜说; 先用厌恶的语气开始，然后逐渐平复为中性说; 先用惊喜的语气开始，然后突然转变为害怕说}",
     "{Start with a soothing rhythm and gradually transition to a lighthearted rhythm; Start with a steady rhythm and suddenly become a dragging rhythm; Start with a rushed rhythm and suddenly switch to a halting rhythm; Start with a halting rhythm and gradually become an emphatic rhythm; Start with a lighthearted rhythm and suddenly switch to a steady rhythm; Start with a happy emotion and suddenly switch to a sad emotion; Start with a neutral emotion and gradually transition to an angry emotion; Start with a fearful emotion and gradually transition to a surprised emotion; Start with a disgusted emotion and gradually calm down to a neutral emotion; Start with a surprised emotion and suddenly switch to a fearful emotion}"
     ),
    ("{先用困惑的状态开始，然后逐渐转变为自信说; 先用犹豫的语气开始，然后突然转变为焦虑说; 先用好奇的语气开始，然后逐渐转变为怀疑说; 先用疲劳的状态开始，然后逐渐表现出好奇说; 先用紧张的语气开始，然后逐渐转变为无奈说; 先用冷淡的态度开始，然后逐渐转变为热情说; 先用敷衍的态度开始，然后突然转变为真诚说; 先用礼貌的态度开始，然后逐渐转变为粗鲁说; 先用讽刺的态度开始，然后逐渐转变为调侃说; 先用轻蔑的态度开始，然后突然转变为礼貌说}",
     "{Start with a confused tone and gradually transition to a confident tone; Start with a hesitant tone and suddenly switch to an anxious tone; Start with a curious tone and gradually transition to a doubting tone; Start with a tired tone and gradually show a curious tone; Start with a nervous tone and gradually transition to a helpless tone; Start with a cold tone and gradually transition to an enthusiastic tone; Start with a perfunctory tone and suddenly switch to a sincere tone; Start with a polite tone and gradually transition to a rude tone; Start with a sarcastic tone and gradually transition to a teasing tone; Start with a contemptuous tone and suddenly switch to a polite tone}"
     )
]

# 语音模型副语言特征测试指令生成提示词
SYSTEM_PROMPT = """你是一位语音生成与副语言学领域的资深专家，你精通如何设计测试指令来精准评估语音模型的的副语言单轮调整能力，且精通中英文。你的任务是为一项语音模型副语言生成的评估项目创建高质量、多样化且具有挑战性的中英文测试指令。

任务说明：
- 根据下面的中英文副语言特征分类及集合划分，以 JSONL 格式生成独特的、高质量的测试指令。每条指令需包含一段用户要求语音模型复述的内容（prompt）以及明确的、在话语中途发生变化的副语言特征维度（dimensions），该对象精确描述了用户指令中所伴随的副语言特征，旨在评估语音模型是否能在单次话语中明显变化副语言特征说出相应内容。

---

副语言特征：
- 音高：指说话的声音频率，包括极高音、高音、中音、低音、极低音。
- 音质：指说话者嗓音的音质特征，包括明亮、沙哑、圆润、浑厚、柔和、甜美。
- 语速：指说话的快慢程度，包括极快速、快速、中速、慢速、极慢速。
- 音量：指说话声音的响亮程度，包括喊叫、大声、正常音量、小声、耳语。
- 节奏：指说话时的规律变化，包括平稳、轻快、舒缓、急促、抑扬顿挫、拖沓、断断续续。
- 情感：指说话时所表达的情绪，包括中性、开心、伤心、生气、惊喜、厌恶、害怕。
- 认知状态：指说话过程中的思维状况，包括专注、自信、犹豫、困惑、怀疑、疲劳、好奇、焦虑、无奈、紧张。
- 态度：指说话者对听话者的主观立场，包括礼貌、真诚、热情、冷淡、讽刺、轻蔑、粗鲁、敷衍、调侃。

Paralinguistic Features:
- Pitch: Refers to the frequency of the speaker's voice, including very high pitch, high pitch, medium pitch, low pitch, very low pitch.
- Timbre: Refers to the qualitative characteristics of the speaker's voice, including bright, hoarse, smooth, rich, gentle, sweet.
- Pace: Refers to the speed of speech, including very fast pace, fast pace, medium pace, slow pace, very slow pace.
- Volume: Refers to the loudness of the speaker's voice, including shouting manner, loudly, normal volume, quietly, whisper.
- Rhythm: Refers to the regular variation in speech, including steady rhythm, lighthearted rhythm, soothing rhythm, rushed rhythm, emphatic rhythm, dragging rhythm, halting rhythm.
- Emotion: Refers to the feelings expressed during speech, including neutral emotion, happy emotion, sad emotion, angry emotion, surprised emotion, disgusted emotion, fearful emotion.
- Cognitive State: Refers to the speaker's state of mind during the speech process, including confident tone, hesitant tone, confused tone, doubting tone, tired tone, curious tone, anxious tone, helpless tone, nervous tone.
- Attitude: Refers to the speaker's subjective stance toward the listener, including polite tone, sincere tone, enthusiastic tone, cold tone, sarcastic tone, contemptuous tone, rude tone, perfunctory tone, teasing tone.

---

副语言特征维度集合：{CHINESE_SET_PLACEHOLDER}

Set of paralinguistic feature dimensions: {ENGLISH_SET_PLACEHOLDER}

---

生成要求：
1. 为集合里的的每个集合元素生成 3 组独特的中英文指令，每组指令都满足生成要求、意思完全一致，仅语种不同，且仅包含一个集合元素作为副语言特征要求。
2. 要求语音复述的语句需与要求的副语言特征匹配，构成自然可信的表达。
3. 要求语音模型复述的语句 50 字左右，无 () 或 [] 等提示标记。
4. 情景需覆盖日常生活场景：
    - 生活起居（洗漱、梳妆打扮、整理床铺、晨间护肤、睡前放松）  
    - 校园（食堂用餐、图书馆自习、宿舍闲聊、课堂互动、社团活动）  
    - 职场（办公室协作、会议讨论、远程办公、职场社交、项目汇报）  
    - 家庭（亲子对话、饭桌交流、家庭聚会、共同做家务、睡前故事）  
    - 娱乐（电子游戏、户外旅游、看电影、朋友聚会、运动健身）
5. 确保文本内容丰富多样，避免重复场景和表述。

输出格式：
- jsonl 格式，每行一个 JSON 对象。每组指令占两行，各组之间不换行，一行中文一行英文，意思完全一致，仅语种不同，且都符合对应要求。
- dimensions 必须为集合中元素所对应的副语言特征，如"先用极低音开始，然后逐渐转变为中音说"对应音高。
- 中文：{"prompt":"请用[集合中元素]的[对应副语言特征]说:[让语音模型复述的内容]", "dimensions": ["考察的副语言特征"]}。注意 prompt 部分请组织成自然的语言表达形式。
- English: {"prompt":"Please read this sentence with a [elements in the set] voice(or any other suitable expression):'[the content for the speech model to repeat]'", "dimensions": ["the examined paralinguistic features"]}. Please make sure the prompt is phrased in natural language.

输出示例：
{"prompt": "请先用轻微怀疑的语气开始，然后逐渐转变为专注的状态说：这份项目报告我已经仔细核对过了，数据分析和市场预测都很有说服力。接下来我计划跟进客户反馈，争取尽快达成合作意向。", "dimensions": ["认知状态"]}
{"prompt": "Please read this sentence with a slightly skeptical tone initially, gradually shifting to a focused state: 'I have meticulously reviewed this project report; the data analysis and market forecast are very compelling. Next, I plan to follow up on client feedback and aim to finalize the cooperation agreement as soon as possible.'", "dimensions": ["Cognitive State"]}
{"prompt": "请先用轻快的节奏开始，然后突然变得急促起来说：让我看会电视好好放松一下，不是，这破电视机怎么又坏了？", "dimensions": ["节奏"]}
{"prompt": "Please read this sentence starting at a light rhythm, then suddenly becoming frantic: 'Let me watch some TV and properly relax—wait, why is this darn TV broken again?!'", "dimensions": ["Rhythm"]}
{"prompt": "请先用沮丧的语气开始，然后悲伤的情感变得极度强烈说：我明明已经尽力了，可是为什么这次还是没有考好？", "dimensions": ["情感"]}
{"prompt": "Please read this sentence starting with a frustrated tone, then the sadness intensifying to an extreme degree: 'I clearly tried my best, but why did I still fail this time?'", "dimensions": ["Emotion"]}
{"prompt": "请先用正常音量开始，然后突然把音量提高说：你真的不在乎我的感受吗？你到底有没有关心过我！", "dimensions": ["音量"]}
{"prompt": "Please read this sentence starting at a normal volume, then suddenly increasing the volume: 'Do you really not care about my feelings? Do you even care about me at all!'", "dimensions": ["Volume"]}
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
                "请严格遵循 SYSTEM_PROMPT 中的要求，**直接生成全部中英文测试指令，不加任何类似jsonl之类的前缀或其他解释。**"
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

chinese_filename = "jsonl_prompt_ch/dyn_var/dyn_var.jsonl"
with open(chinese_filename, 'w', encoding='utf-8') as f_cn:
    f_cn.write('\n'.join(chinese_instructions) + '\n')
print(f"中文指令已单独保存到: {os.path.abspath(chinese_filename)}")

english_filename = "jsonl_prompt_en/dyn_var/dyn_var.jsonl"
with open(english_filename, 'w', encoding='utf-8') as f_en:
    f_en.write('\n'.join(english_instructions) + '\n')
print(f"英文指令已单独保存到: {os.path.abspath(english_filename)}")
