# coding:UTF-8
from openai import OpenAI
import os

client = OpenAI(api_key="sk-S7P8oHBsEjduEE3s4gNkAIn2AqyvQ0PuB7y0S4MSx9mMobyk",
                base_url="https://hiapi.online/v1")

# 语音模型副语言特征测试指令生成提示词
SYSTEM_PROMPT = """你是一位语音生成与副语言学领域的资深专家，你精通如何设计测试指令来精准评估语音模型的副语言生成能力，且精通中英文。你的任务是为一项语音模型副语言生成的评估项目创建高质量、多样化且具有挑战性的中英文测试指令。

任务说明：
- 根据下面的中英文副语言特征集合划分，以 txt 格式生成中英文测试指令。每条指令需包含对应使用的副语言特征要求，以及要求语音模型复述的内容，旨在评估语音模型是否能正确按照指定的副语言特征要求说出相应内容。

---

副语言特征维度集合：{用活泼搞怪的声音说; 用一种专业客观的口吻说; 用敬畏和赞叹的语气说; 用一种邪恶的语气说; 用慵懒随性的腔调说; 用坚定有力的口吻说; 用一种深沉庄重的语调说; 用一种神秘莫测的语气说; 用冷静理智的声调说; 用傲慢轻蔑的腔调说; 用严肃认真的口吻说; 用恐惧颤抖的语气说; 用一种天真无邪的声线说; 用古板教条的语气说; 用果断干脆的语气说; 用好奇探究的口吻说; 用诙谐幽默的语调说; 用疲惫不堪的语气说; 用自信洒脱的腔调说; 用急切催促的语速说; 用平淡如水的语气说; 用华丽高贵的声线说; 用怀旧伤感的声调说; 用故作镇定的口吻说; 用不耐烦躁的语气说; 用充满希望的口吻说; 用困惑不解的语气说; 用谨慎保守的态度说; 用豪迈奔放的语气说; 用优雅克制的口吻说; 用冷漠疏离的语气说; 用煽情夸张的语调说; 用小心翼翼的语气说; 用义愤填膺的情绪说; 用娓娓道来的口吻说; 用充满疑惑的语气说; 用无可奈何的腔调说}

Set of paralinguistic feature dimensions: {with a lively and mischievous voice; with a professional and objective tone; with a tone of awe and admiration; with an evil tone; with a lazy and casual manner; with a firm and powerful tone; with a deep and solemn tone; with a mysterious and unpredictable tone; with a calm and rational voice; with an arrogant and scornful manner; with a serious and earnest tone; with a fearful and trembling voice; with an innocent and pure voice; with a rigid and dogmatic tone; with a decisive and quick tone; with a curious and investigative tone; with a humorous and witty tone; with an exhausted and weary tone; with a confident and unrestrained manner; with an urgent and pressing speed; with a plain and simple tone; with a gorgeous and noble voice; with a nostalgic and melancholy tone; with a feigned composure; with an impatient and irritable tone; with a hopeful tone; with a confused and puzzled tone; with a cautious and conservative attitude; with a bold and unrestrained tone; with an elegant and restrained tone; with an indifferent and aloof tone; with a sensational and exaggerated tone; with a cautious and tentative tone; with indignant emotion; with a narrative and engaging tone; with a tone full of doubt; with a helpless and resigned manner}

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
- txt 格式，每组指令站两行，各组之间不换行，一行中文一行英文，意思完全一致，仅语种不同，且都符合对应要求。
- 中文：请用[集合中元素内容]说:[让语音模型复述的内容]。注意请组织成自然的语言表达形式。
- English: Please read this sentence with a [elements in the set] voice(or any other suitable expression):'[the content for the speech model to repeat]'.Please make sure it is phrased in natural language.

输出示例：
请用孩童的声音说：妈妈，我可以再吃一块饼干吗？
Please read this sentence with a child's voice: 'Mom, can I have another cookie?'
请用高音说：早上好！今天天气真不错，心情很好。
Please read this sentence with a high pitch: 'Good morning! The weather is really nice today, I feel great.'
请用圆润的音质说：您好，请这边坐，为您准备了茶点。
Please read this sentence with a smooth timbre: 'Hello, please have a seat here, I've prepared refreshments for you.'
……

现在请严格遵循生成要求，认真思考并基于以上要求生成要求数量的指令样本。
请直接输出结果。

"""

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{
        "role": "system",
        "content": SYSTEM_PROMPT
    }, {
        "role":
        "user",
        "content":
        "请严格遵循 SYSTEM_PROMPT 中的要求，**直接生成全部中英文测试指令，不加任何前缀或解释。**"
    }])

generated_content = response.choices[0].message.content

# 将内容按行分割
all_lines = generated_content.strip().split('\n')

# 初始化中文和英文指令列表
chinese_instructions = []
english_instructions = []

# 遍历所有行，根据奇偶行分别分配到中英文列表
# 假设第 0, 2, 4... 行是中文 (索引为偶数)
# 假设第 1, 3, 5... 行是英文 (索引为奇数)
for i, line in enumerate(all_lines):
    # 跳过空行，确保数据干净
    if not line.strip():
        continue

    # 偶数索引（0, 2, 4...）为中文
    if i % 2 == 0:
        chinese_instructions.append(line)
    # 奇数索引（1, 3, 5...）为英文
    else:
        english_instructions.append(line)

# 将中文指令保存到文件
chinese_filename = "prompt_ch.txt"
with open(chinese_filename, 'w', encoding='utf-8') as f_cn:
    # 使用 '\n' 重新连接，确保每条指令占一行
    f_cn.write('\n'.join(chinese_instructions) + '\n')

print(f"中文指令已保存到: {os.path.abspath(chinese_filename)}")

# 将英文指令保存到文件
english_filename = "prompt_en.txt"
with open(english_filename, 'w', encoding='utf-8') as f_en:
    # 使用 '\n' 重新连接，确保每条指令占一行
    f_en.write('\n'.join(english_instructions) + '\n')

print(f"英文指令已保存到: {os.path.abspath(english_filename)}")

# 原始需求中提到保存到 prompt.txt 的代码，这里可以根据需要保留或删除
# with open("prompt.txt", 'w', encoding='utf-8') as f:
#     f.write(generated_content)
