import os
import json
from collections import defaultdict

# ===== 批量输入 & 输出根目录 =====
INPUT_ROOT = "judge_data/result_v5/result_v5_sit_ada/metadata"
OUTPUT_ROOT = "judge_data/result_v5/result_v5_sit_ada/judge_result"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# ================= 主循环：逐个数据集统计 =================
for folder_name in sorted(os.listdir(INPUT_ROOT)):

    JSON_DIR = os.path.join(INPUT_ROOT, folder_name)
    if not os.path.isdir(JSON_DIR):
        continue

    suffix = folder_name.replace("metadata_", "", 1)
    OUTPUT_TXT = os.path.join(OUTPUT_ROOT, f"result_{suffix}.txt")

    print(f"\n开始统计：{JSON_DIR}")

    # scores[model][dim] 存储最终计算出的得分 (Candidate为原始，Baseline为加权)
    scores = defaultdict(lambda: defaultdict(float))

    # raw_scores_map[baseline][dim][candidate] 存储 baseline 面对不同 candidate 的原始胜负分
    raw_scores_map = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float)))

    # candidate_dim_scores[candidate][dim] 存储 candidate 原始得分（作为权重基数）
    candidate_dim_scores = defaultdict(lambda: defaultdict(float))

    skipped_samples = []
    sub_dims_set = set()  # 记录所有子维度

    # ================= 1. 读取数据并统计原始分布 =================
    for filename in os.listdir(JSON_DIR):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(JSON_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        sample_index = data.get("sample_index", filename)
        if data.get("status") != "Success":
            skipped_samples.append(sample_index)
            continue

        candidate = data["candidate_name"]
        baseline = data["baseline_name"]

        raw_dims = data["dimensions"]
        dims = [d.split(":", 1)[0].strip() for d in raw_dims]
        candidate_pos = data["candidate_position"]

        for idx, dim in enumerate(dims, start=1):
            sub_dims_set.add(dim)
            winner_key = f"winner_position_{idx}"
            winner_pos = data.get(winner_key)

            if winner_pos is None or winner_pos == -1:
                skipped_samples.append(f"{sample_index}:{dim}")
                continue

            # --- 统计逻辑：同时作用于子维度和 "Overall" 维度 ---
            target_dims = [dim, "Overall"]

            if winner_pos == 0:  # 平局
                for d in target_dims:
                    candidate_dim_scores[candidate][d] += 0.5
                    raw_scores_map[baseline][d][candidate] += 0.5
            elif winner_pos == candidate_pos:  # Candidate 赢
                for d in target_dims:
                    candidate_dim_scores[candidate][d] += 1.0
            else:  # Baseline 赢
                for d in target_dims:
                    raw_scores_map[baseline][d][candidate] += 1.0

    # ================= 2. 核心逻辑：加权计算得分 (含 Overall) =================

    # 定义所有参与计算的维度（子维度 + Overall）
    all_dims = sorted(list(sub_dims_set)) + ["Overall"]

    # A. Candidate 直接使用原始分
    for cand, dim_dict in candidate_dim_scores.items():
        for dim, val in dim_dict.items():
            scores[cand][dim] = val

    # B. Baseline 使用基于其对手表现的加权分
    for b_name, dim_dict in raw_scores_map.items():
        for dim, cand_val_map in dim_dict.items():
            compare_candidates = list(cand_val_map.keys())

            # 计算该维度下，该 baseline 面对的所有 candidate 的原始总分作为权重基数
            dim_weight_base = sum(candidate_dim_scores[c][dim]
                                  for c in compare_candidates)

            if dim_weight_base == 0:
                avg_weight = 1.0 / len(
                    compare_candidates) if compare_candidates else 0
                for c_name, raw_val in cand_val_map.items():
                    scores[b_name][dim] += raw_val * avg_weight
            else:
                for c_name, raw_val in cand_val_map.items():
                    # 权重 = (该 Candidate 在该维度的表现) / (所有相关 Candidate 在该维度的总表现)
                    weight = candidate_dim_scores[c_name][dim] / dim_weight_base
                    scores[b_name][dim] += raw_val * weight

    # ================= 3. 排序逻辑 =================
    # 按照加权后的 "Overall" 维度得分进行排序
    model_ranking = sorted(scores.keys(),
                           key=lambda m: scores[m].get("Overall", 0),
                           reverse=True)

    # ================= 4. 写文件 =================
    os.makedirs(os.path.dirname(OUTPUT_TXT), exist_ok=True)
    with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
        out.write("======= 各模型最终得分 (含独立加权的 Overall 维度) =======\n\n")

        for model in model_ranking:
            overall_sc = scores[model].get("Overall", 0)
            out.write(f"=== {model} ===\n")
            out.write(f"  Overall: {overall_sc:.2f}\n")
            # 打印子维度
            for dim in sorted(list(sub_dims_set)):
                out.write(f"  {dim}: {scores[model].get(dim, 0):.2f}\n")
            out.write("\n")

        out.write("\n======= 各维度排名 (含 Overall) =======\n\n")
        for dim in all_dims:
            dim_ranking = sorted([(m, scores[m].get(dim, 0)) for m in scores],
                                 key=lambda x: x[1],
                                 reverse=True)
            out.write(f"【维度：{dim}】\n")
            for model, sc in dim_ranking:
                out.write(f"  {model}: {sc:.2f}\n")
            out.write("\n")

        out.write("\n======= 跳过的样本 =======\n")
        out.write(
            ", ".join(map(str, skipped_samples)) if skipped_samples else "无")

        # ================= Baseline vs Candidate 的 Overall 原始分 =================
        out.write(
            "\n\n======= Baseline 与各 Candidate 比较的【Overall 原始得分】 =======\n\n")

        for baseline in sorted(raw_scores_map.keys()):
            out.write(f"### Baseline: {baseline} ###\n")
            overall_map = raw_scores_map[baseline].get("Overall", {})

            for candidate in sorted(overall_map.keys()):
                raw_overall = overall_map.get(candidate, 0.0)
                out.write(f"  vs {candidate}: {raw_overall:.2f}\n")

            out.write("\n")

    print(f"完成统计: {OUTPUT_TXT}")
