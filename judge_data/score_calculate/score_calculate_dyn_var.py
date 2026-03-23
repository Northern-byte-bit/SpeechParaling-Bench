import os
import json
from collections import defaultdict

# ===== Batch Input & Output Root Directories =====
INPUT_ROOT = "judge_data/result_v5/result_v5_para_con/metadata"
OUTPUT_ROOT = "judge_data/result_v5/result_v5_para_con/judge_result"
os.makedirs(OUTPUT_ROOT, exist_ok=True)


def process_one_folder(JSON_DIR, OUTPUT_TXT):
    # scores[model][dim] stores final results (Candidate stores raw scores, Baseline stores weighted scores)
    scores = defaultdict(lambda: defaultdict(float))

    # baseline_raw_scores[baseline][candidate][dim] stores raw counts of baseline winning over candidate
    baseline_raw_scores = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float)))

    skipped_samples = []
    all_dims = set()

    # ================= 1. Read and aggregate raw scores =================
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
        # Merge original dimensions with "Overall_Total" dimension
        dims = data["dimensions"] + ["Overall_Total"]
        candidate_pos = data["candidate_position"]

        for d in dims:
            all_dims.add(d)

        # ==== Core scoring logic ====
        if winner_pos == 0:  # Draw
            for dim in dims:
                scores[candidate][dim] += 0.5
                baseline_raw_scores[baseline][candidate][dim] += 0.5

        elif winner_pos == candidate_pos:  # Candidate wins
            for dim in dims:
                scores[candidate][dim] += 1

        else:  # Baseline wins
            for dim in dims:
                baseline_raw_scores[baseline][candidate][dim] += 1

    # ================= 2. Calculate baseline weighted scores in each dimension (incl. total) =================
    for baseline, cand_dict in baseline_raw_scores.items():
        for dim in all_dims:
            # Calculate total raw score sum for all candidates compared with this baseline in this dimension
            dim_total_weight = 0.0
            for cand in cand_dict:
                dim_total_weight += scores[cand].get(dim, 0.0)

            if dim_total_weight == 0:
                continue

            # Weighted calculation for baseline score
            for cand, dim_results in cand_dict.items():
                raw_win_score = dim_results.get(dim, 0.0)
                if raw_win_score > 0:
                    # Weight = (Candidate's performance in this dimension) / (Sum of all candidates' performance in this dimension)
                    weight = scores[cand].get(dim, 0.0) / dim_total_weight
                    scores[baseline][dim] += raw_win_score * weight

    # ================= 3. Sorting logic =================
    # Ranking by "Overall_Total" dimension
    model_ranking = sorted(scores.keys(),
                           key=lambda m: scores[m].get("Overall_Total", 0),
                           reverse=True)

    # ================= Write TXT =================
    with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
        out.write(
            "======= Final Scores for Each Model (incl. weighted total score dimension) =======\n\n"
        )

        for model in model_ranking:
            total_score = scores[model].get("Overall_Total", 0)
            out.write(f"=== {model} ===\n")
            out.write(f"  Overall: {total_score:.2f}\n")

            # Print other sub-dimensions
            sub_dims = [d for d in all_dims if d != "Overall_Total"]
            for dim in sorted(sub_dims):
                out.write(f"  {dim}: {scores[model].get(dim, 0):.2f}\n")
            out.write("\n")

        out.write("\n======= Detailed Ranking for Each Dimension =======\n\n")
        # Print ranking sorted by dimension name
        for dim in sorted(all_dims):
            ranking = sorted(
                ((model, scores[model].get(dim, 0)) for model in scores),
                key=lambda x: x[1],
                reverse=True)
            out.write(f"【Dimension: {dim}】\n")
            for model, sc in ranking:
                out.write(f"  {model}: {sc:.2f}\n")
            out.write("\n")

        out.write(
            "\n======= Baseline vs Candidate 【Overall Raw Scores】 =======\n\n")

        for baseline in sorted(baseline_raw_scores.keys()):
            out.write(f"### Baseline: {baseline} ###\n")

            for candidate in sorted(baseline_raw_scores[baseline].keys()):
                overall_raw = baseline_raw_scores[baseline][candidate].get(
                    "Overall_Total", 0.0)
                out.write(f"  vs {candidate}: {overall_raw:.2f}\n")

            out.write("\n")

        out.write("\n======= Skipped Samples (winner_position = -1) =======\n")
        out.write(", ".join(map(str, skipped_samples)
                            ) if skipped_samples else "None")


# Batch execution
for folder_name in sorted(os.listdir(INPUT_ROOT)):
    json_dir = os.path.join(INPUT_ROOT, folder_name)
    if not os.path.isdir(json_dir):
        continue

    suffix = folder_name.replace("metadata_", "", 1)
    output_txt = os.path.join(OUTPUT_ROOT, f"result_{suffix}.txt")

    print(f"Start processing: {folder_name}")
    process_one_folder(json_dir, output_txt)
    print(f"Finished → {output_txt}\n")
