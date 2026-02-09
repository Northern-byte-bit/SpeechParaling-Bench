import os
import json
from collections import defaultdict

# ==== 用户配置 ====
JSON_DIR = "评测数据/测试元数据json3"
OUTPUT_TXT = "评测数据/测试元数据json3/模型得分统计结果3.txt"

# 模型 → 维度 → 分数
scores = defaultdict(lambda: defaultdict(float))

# baseline -> 参与比较的 candidate 模型集合
baseline_compare_candidates = defaultdict(set)

# 被跳过的编号
skipped_samples = []


for filename in os.listdir(JSON_DIR):
    if not filename.endswith(".json"):
        continue
    
    path = os.path.join(JSON_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sample_index = data.get("sample_index", filename)

    winner_pos = data.get("winner_position", None)
    if winner_pos == -1:
        skipped_samples.append(sample_index)
        continue

    candidate = data["candidate_name"]
    baseline = data["baseline_name"]
    dims = data["dimensions"]
    candidate_pos = data["candidate_position"]

    # baseline 记录对比过的 candidate
    baseline_compare_candidates[baseline].add(candidate)

    # ==== scoring logic ====
    if winner_pos == 0:
        # 平局：两个模型 +0.5 分
        for dim in dims:
            scores[candidate][dim] += 0.5
            scores[baseline][dim] += 0.5

    elif winner_pos == candidate_pos:
        # candidate 胜
        for dim in dims:
            scores[candidate][dim] += 1

    else:
        # baseline 胜
        for dim in dims:
            scores[baseline][dim] += 1


# ==== baseline 得分除以比较数量 ====
for baseline, cand_set in baseline_compare_candidates.items():
    n = len(cand_set)
    if n > 0:
        for dim in scores[baseline]:
            scores[baseline][dim] /= n


# ==== 写入 TXT 输出 ====

with open(OUTPUT_TXT, "w", encoding="utf-8") as out:

    out.write("======= 各模型最终得分 =======\n\n")

    for model, dim_scores in scores.items():
        out.write(f"=== {model} ===\n")
        total_score = sum(dim_scores.values())
        out.write(f"总分：{total_score:.2f}\n")
        for dim, value in dim_scores.items():
            out.write(f"  {dim}: {value:.2f}\n")
        out.write("\n")

    # ==== 维度排名 ====
    out.write("\n======= 各维度排名 =======\n\n")

    # 收集所有维度
    all_dims = set()
    for model in scores:
        for dim in scores[model]:
            all_dims.add(dim)

    for dim in all_dims:
        ranking = []
        for model in scores:
            ranking.append((model, scores[model].get(dim, 0)))
        ranking.sort(key=lambda x: x[1], reverse=True)

        out.write(f"【维度：{dim}】\n")
        for model, sc in ranking:
            out.write(f"  {model}: {sc:.2f}\n")
        out.write("\n")

    # ==== 被跳过的编号 ====
    out.write("\n======= 跳过的样本编号（winner_position = -1）=======\n")
    if skipped_samples:
        out.write(", ".join(map(str, skipped_samples)) + "\n")
    else:
        out.write("无\n")

print(f"统计完成！结果已写入：{OUTPUT_TXT}")
