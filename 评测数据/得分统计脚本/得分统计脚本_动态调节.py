import os
import json
from collections import defaultdict

# ===== 批量输入 & 输出根目录 =====
INPUT_ROOT = "评测数据/评测实验结果/测试v5-最终全实验/测试v5_动态调节/测试元数据"
OUTPUT_ROOT = "评测数据/评测实验结果/测试v5-最终全实验/测试v5_动态调节/模型得分结果"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

def process_one_folder(JSON_DIR, OUTPUT_TXT):
    # scores[model][dim] 存储最终结果 (Candidate 存原始分，Baseline 存加权分)
    scores = defaultdict(lambda: defaultdict(float))
    
    # baseline_raw_scores[baseline][candidate][dim] 存储 baseline 赢了 candidate 的原始次数
    baseline_raw_scores = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float))
    )
    
    skipped_samples = []
    all_dims = set()

    # ================= 1. 读取并统计原始得分 =================
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
        # 将原始维度和“总分”维度合并处理
        dims = data["dimensions"] + ["Overall_Total"] 
        candidate_pos = data["candidate_position"]
        
        for d in dims:
            all_dims.add(d)

        # ==== 核心计分逻辑 ====
        if winner_pos == 0:  # 平局
            for dim in dims:
                scores[candidate][dim] += 0.5
                baseline_raw_scores[baseline][candidate][dim] += 0.5

        elif winner_pos == candidate_pos:  # Candidate 赢
            for dim in dims:
                scores[candidate][dim] += 1

        else:  # Baseline 赢
            for dim in dims:
                baseline_raw_scores[baseline][candidate][dim] += 1

    # ================= 2. 计算 Baseline 在各维度（含总分）上的加权得分 =================
    for baseline, cand_dict in baseline_raw_scores.items():
        for dim in all_dims:
            # 计算该维度下，与该 baseline 比较过的所有 candidate 的原始得分总和
            dim_total_weight = 0.0
            for cand in cand_dict:
                dim_total_weight += scores[cand].get(dim, 0.0)

            if dim_total_weight == 0:
                continue

            # 加权计算 baseline 的得分
            for cand, dim_results in cand_dict.items():
                raw_win_score = dim_results.get(dim, 0.0)
                if raw_win_score > 0:
                    # 权重 = (该 Candidate 在该维度的表现) / (所有 Candidate 在该维度的表现总和)
                    weight = scores[cand].get(dim, 0.0) / dim_total_weight
                    scores[baseline][dim] += raw_win_score * weight

    # ================= 3. 排序逻辑 =================
    # 按 "Overall_Total" 维度进行总排名
    model_ranking = sorted(
        scores.keys(),
        key=lambda m: scores[m].get("Overall_Total", 0),
        reverse=True
    )

    # ================= 写 TXT =================
    with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
        out.write("======= 各模型最终得分 (含加权总分维度) =======\n\n")

        for model in model_ranking:
            total_score = scores[model].get("Overall_Total", 0)
            out.write(f"=== {model} ===\n")
            out.write(f"  Overall: {total_score:.2f}\n")
            
            # 打印其他子维度
            sub_dims = [d for d in all_dims if d != "Overall_Total"]
            for dim in sorted(sub_dims):
                out.write(f"  {dim}: {scores[model].get(dim, 0):.2f}\n")
            out.write("\n")

        out.write("\n======= 各维度详细排名 =======\n\n")
        # 按照维度名称排序打印排名
        for dim in sorted(all_dims):
            ranking = sorted(
                ((model, scores[model].get(dim, 0)) for model in scores),
                key=lambda x: x[1],
                reverse=True
            )
            out.write(f"【维度：{dim}】\n")
            for model, sc in ranking:
                out.write(f"  {model}: {sc:.2f}\n")
            out.write("\n")

        out.write("\n======= Baseline 与各 Candidate 比较的【Overall 原始得分】 =======\n\n")

        for baseline in sorted(baseline_raw_scores.keys()):
            out.write(f"### Baseline: {baseline} ###\n")

            for candidate in sorted(baseline_raw_scores[baseline].keys()):
                overall_raw = baseline_raw_scores[baseline][candidate].get(
                    "Overall_Total", 0.0
                )
                out.write(f"  vs {candidate}: {overall_raw:.2f}\n")

            out.write("\n")


        out.write("\n======= 跳过的样本编号（winner_position = -1）=======\n")
        out.write(", ".join(map(str, skipped_samples)) if skipped_samples else "无")

# 批量执行
for folder_name in sorted(os.listdir(INPUT_ROOT)):
    json_dir = os.path.join(INPUT_ROOT, folder_name)
    if not os.path.isdir(json_dir):
        continue

    suffix = folder_name.replace("测试元数据_", "", 1)
    output_txt = os.path.join(OUTPUT_ROOT, f"模型得分统计结果_{suffix}.txt")

    print(f"开始处理：{folder_name}")
    process_one_folder(json_dir, output_txt)
    print(f"完成 → {output_txt}\n")