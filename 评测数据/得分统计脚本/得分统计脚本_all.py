import os
import json
from collections import defaultdict

# ================= 用户配置 =================
JSON_DIR = "评测数据/评测实验结果/测试v5-最终全实验/测试v5_可控生成_all/测试元数据/测试元数据_v5_all_short_sin_ch"
OUTPUT_TXT = "评测数据/评测实验结果/测试v5-最终全实验/测试v5_可控生成_all/模型得分结果/模型得分统计结果_v5_all_short_sin_ch.txt"

# model -> dim -> score
scores = defaultdict(lambda: defaultdict(float))

# 跳过的样本
skipped_samples = []

# ================= 读取并统计 =================
for filename in os.listdir(JSON_DIR):
    if not filename.endswith(".json"):
        continue

    path = os.path.join(JSON_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sample_index = data.get("sample_index", filename)

    winner_pos = data.get("winner_position_1", -1)
    if winner_pos == -1:
        skipped_samples.append(sample_index)
        continue

    model_a = data["model_a"]
    model_b = data["model_b"]
    dims = data["dimensions"]

    pos_a = data["model_a_position"]
    pos_b = data["model_b_position"]

    # ================= 得分规则（保持不变） =================
    if winner_pos == 0:
        # tie
        for dim in dims:
            scores[model_a][dim] += 0.5
            scores[model_b][dim] += 0.5

    elif winner_pos == pos_a:
        # model_a wins
        for dim in dims:
            scores[model_a][dim] += 1.0

    elif winner_pos == pos_b:
        # model_b wins
        for dim in dims:
            scores[model_b][dim] += 1.0

# ================= 全局维度列表 =================
all_dims = set()
for model in scores:
    all_dims.update(scores[model].keys())

all_dims_sorted = sorted(all_dims)

# ================= 模型按总分排序 =================
model_total_scores = []
for model, dim_scores in scores.items():
    total = sum(dim_scores.values())
    model_total_scores.append((model, total))

model_total_scores.sort(key=lambda x: x[1], reverse=True)

# ================= 写入 TXT =================
with open(OUTPUT_TXT, "w", encoding="utf-8") as out:

    out.write("======= 各模型最终得分（全模型两两比较）=======\n\n")

    for model, total_score in model_total_scores:
        out.write(f"=== {model} ===\n")
        out.write(f"总分：{total_score:.2f}\n")

        for dim in all_dims_sorted:
            value = scores[model].get(dim, 0.0)
            out.write(f"  {dim}: {value:.2f}\n")

        out.write("\n")

    out.write("\n======= 各维度排名 =======\n\n")

    for dim in all_dims_sorted:
        ranking = []
        for model, _ in model_total_scores:
            ranking.append((model, scores[model].get(dim, 0.0)))

        ranking.sort(key=lambda x: x[1], reverse=True)

        out.write(f"【维度：{dim}】\n")
        for model, sc in ranking:
            out.write(f"  {model}: {sc:.2f}\n")
        out.write("\n")

    out.write("\n======= 跳过的样本编号（winner_position_1 = -1）=======\n")
    if skipped_samples:
        out.write(", ".join(map(str, skipped_samples)) + "\n")
    else:
        out.write("无\n")

print(f"统计完成！结果已写入：{OUTPUT_TXT}")
