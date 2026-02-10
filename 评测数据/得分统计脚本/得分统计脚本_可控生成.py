import os
import json
from collections import defaultdict

# ===== 批量输入 & 输出根目录 =====
INPUT_ROOT = "评测数据/评测实验结果/测试v5-最终全实验/测试v5_para_con/测试元数据"
OUTPUT_ROOT = "评测数据/评测实验结果/测试v5-最终全实验/测试v5_para_con/模型得分结果"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

for folder_name in sorted(os.listdir(INPUT_ROOT)):
    JSON_DIR = os.path.join(INPUT_ROOT, folder_name)
    if not os.path.isdir(JSON_DIR):
        continue

    suffix = folder_name.replace("测试元数据_", "", 1)
    OUTPUT_TXT = os.path.join(OUTPUT_ROOT, f"模型得分统计结果_{suffix}.txt")

    print(f"\n开始统计：{JSON_DIR}")

    # 存储最终得分 (Candidate为原始分，Baseline为加权分)
    scores = defaultdict(lambda: defaultdict(float))
    # 存储 Baseline 面对各 Candidate 在各维度上的原始赢球/平局计数
    raw_scores_map = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    # 存储 Candidate 原始得分（用于计算权重基数）
    candidate_dim_scores = defaultdict(lambda: defaultdict(float))
    
    skipped_samples = []

    # ================= 1. 读取并统计原始分布 =================
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
        dims = data["dimensions"]
        candidate_pos = data["candidate_position"]

        # 处理子维度得分
        for idx, dim in enumerate(dims, start=1):
            winner_key = f"winner_position_{idx}"
            winner_pos = data.get(winner_key)

            if winner_pos is None or winner_pos == -1:
                skipped_samples.append(f"{sample_index}:{dim}")
                continue

            # 统计逻辑：同时更新该维度和虚拟的 "Overall" 维度
            # 注意：这里 Overall 的权重是各维度胜负的平均贡献
            if winner_pos == 0:  # 平局
                # 子维度
                candidate_dim_scores[candidate][dim] += 0.5
                raw_scores_map[baseline][dim][candidate] += 0.5
                # 总分维度贡献
                candidate_dim_scores[candidate]["Overall"] += 0.5
                raw_scores_map[baseline]["Overall"][candidate] += 0.5
            elif winner_pos == candidate_pos: # Candidate 赢
                candidate_dim_scores[candidate][dim] += 1.0
                candidate_dim_scores[candidate]["Overall"] += 1.0
            else: # Baseline 赢
                raw_scores_map[baseline][dim][candidate] += 1.0
                raw_scores_map[baseline]["Overall"][candidate] += 1.0

    # ================= 2. 核心逻辑：加权计算得分 (含 Overall) =================
    
    # 获取包含 Overall 在内的所有维度
    all_target_dims = set()
    for cand in candidate_dim_scores:
        for dim in candidate_dim_scores[cand]:
            all_target_dims.add(dim)

    # A. Candidate 直接使用原始分
    for cand, dim_dict in candidate_dim_scores.items():
        for dim, val in dim_dict.items():
            scores[cand][dim] = val

    # B. Baseline 使用基于 Candidate 表现的加权分
    for b_name, dim_dict in raw_scores_map.items():
        for dim, cand_val_map in dim_dict.items():
            compare_candidates = list(cand_val_map.keys())
            
            # 计算该维度（或 Overall 维度）下，相关 candidate 的原始总分作为权重分母
            dim_weight_base = sum(candidate_dim_scores[c][dim] for c in compare_candidates)
            
            if dim_weight_base == 0:
                avg_weight = 1.0 / len(compare_candidates) if compare_candidates else 0
                for c_name, raw_val in cand_val_map.items():
                    scores[b_name][dim] += raw_val * avg_weight
            else:
                for c_name, raw_val in cand_val_map.items():
                    # 权重 = (该 Candidate 在该维度的原始表现) / (所有 Candidate 在该维度的总表现)
                    weight = candidate_dim_scores[c_name][dim] / dim_weight_base
                    scores[b_name][dim] += raw_val * weight

    # ================= 3. 排序与输出 =================
    # 按 Overall 维度进行排序
    sorted_models = sorted(
        scores.keys(),
        key=lambda m: scores[m].get("Overall", 0),
        reverse=True
    )

    with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
        out.write("======= 各模型最终得分 (各维度及总分均采用加权逻辑) =======\n\n")

        for model in sorted_models:
            out.write(f"=== {model} ===\n")
            # 这里的 Overall 是加权后的总评价分
            out.write(f"  Overall: {scores[model].get('Overall', 0):.2f}\n")
            for dim in sorted(all_target_dims):
                if dim != "Overall":
                    out.write(f"  {dim}: {scores[model].get(dim, 0):.2f}\n")
            out.write("\n")

        out.write("\n======= 维度排名详情 =======\n\n")
        for dim in sorted(all_target_dims):
            ranking = sorted(
                [(m, scores[m].get(dim, 0)) for m in scores],
                key=lambda x: x[1],
                reverse=True
            )
            out.write(f"【维度：{dim}】\n")
            for model, sc in ranking:
                out.write(f"  {model}: {sc:.2f}\n")
            out.write("\n")

        out.write("\n======= 跳过的样本 =======\n")
        out.write(", ".join(map(str, skipped_samples)) if skipped_samples else "无")

        # ================= Baseline vs Candidate 的 Overall 原始分 =================
        out.write("\n\n======= Baseline 与各 Candidate 比较的【Overall 原始得分】 =======\n\n")

        for baseline in sorted(raw_scores_map.keys()):
            out.write(f"### Baseline: {baseline} ###\n")
            overall_map = raw_scores_map[baseline].get("Overall", {})

            for candidate in sorted(overall_map.keys()):
                raw_overall = overall_map.get(candidate, 0.0)
                out.write(f"  vs {candidate}: {raw_overall:.2f}\n")

            out.write("\n")


    print(f"统计完成 → {OUTPUT_TXT}")