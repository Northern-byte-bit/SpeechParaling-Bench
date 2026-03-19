import os
import json
from collections import defaultdict

# ===== Batch Input & Output Root Directories =====
INPUT_ROOT = "judge_data/result_v5/result_v5_para_con/metadata"
OUTPUT_ROOT = "judge_data/result_v5/result_v5_para_con/judge_result"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

for folder_name in sorted(os.listdir(INPUT_ROOT)):
    JSON_DIR = os.path.join(INPUT_ROOT, folder_name)
    if not os.path.isdir(JSON_DIR):
        continue

    suffix = folder_name.replace("metadata_", "", 1)
    OUTPUT_TXT = os.path.join(OUTPUT_ROOT, f"result_{suffix}.txt")

    print(f"\nStart processing: {JSON_DIR}")

    # Store final scores (Candidate raw scores, Baseline weighted scores)
    scores = defaultdict(lambda: defaultdict(float))
    # Store Baseline vs Candidate raw win/draw counts per dimension
    raw_scores_map = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float)))
    # Store Candidate raw scores (as weight base)
    candidate_dim_scores = defaultdict(lambda: defaultdict(float))

    skipped_samples = []

    # ================= 1. Read and aggregate raw distribution =================
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

        # Process sub-dimension scores
        for idx, dim in enumerate(dims, start=1):
            winner_key = f"winner_position_{idx}"
            winner_pos = data.get(winner_key)

            if winner_pos is None or winner_pos == -1:
                skipped_samples.append(f"{sample_index}:{dim}")
                continue

            # Statistical logic: Update both sub-dimension and virtual "Overall" dimension
            # Note: The weight of Overall here is the average contribution of each dimension's win/loss
            if winner_pos == 0:  # Draw
                # Sub-dimensions
                candidate_dim_scores[candidate][dim] += 0.5
                raw_scores_map[baseline][dim][candidate] += 0.5
                # Overall dimension contribution
                candidate_dim_scores[candidate]["Overall"] += 0.5
                raw_scores_map[baseline]["Overall"][candidate] += 0.5
            elif winner_pos == candidate_pos:  # Candidate wins
                candidate_dim_scores[candidate][dim] += 1.0
                candidate_dim_scores[candidate]["Overall"] += 1.0
            else:  # Baseline wins
                raw_scores_map[baseline][dim][candidate] += 1.0
                raw_scores_map[baseline]["Overall"][candidate] += 1.0

    # ================= 2. Core logic: Weighted score calculation (incl. Overall) =================

    # Get all dimensions including Overall
    all_target_dims = set()
    for cand in candidate_dim_scores:
        for dim in candidate_dim_scores[cand]:
            all_target_dims.add(dim)

    # A. Candidate uses raw scores directly
    for cand, dim_dict in candidate_dim_scores.items():
        for dim, val in dim_dict.items():
            scores[cand][dim] = val

    # B. Baseline uses weighted scores based on candidate performance
    for b_name, dim_dict in raw_scores_map.items():
        for dim, cand_val_map in dim_dict.items():
            compare_candidates = list(cand_val_map.keys())

            # Calculate total raw score for this dimension (or Overall dimension) as weight denominator
            dim_weight_base = sum(candidate_dim_scores[c][dim]
                                  for c in compare_candidates)

            if dim_weight_base == 0:
                avg_weight = 1.0 / len(
                    compare_candidates) if compare_candidates else 0
                for c_name, raw_val in cand_val_map.items():
                    scores[b_name][dim] += raw_val * avg_weight
            else:
                for c_name, raw_val in cand_val_map.items():
                    # Weight = (Candidate's raw performance in this dimension) / (Total performance of all candidates in this dimension)
                    weight = candidate_dim_scores[c_name][dim] / dim_weight_base
                    scores[b_name][dim] += raw_val * weight

    # ================= 3. Sorting and output =================
    # Sort by Overall dimension
    sorted_models = sorted(scores.keys(),
                           key=lambda m: scores[m].get("Overall", 0),
                           reverse=True)

    with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
        out.write("======= Final Scores for Each Model (weighted logic for dimensions and total) =======\n\n")

        for model in sorted_models:
            out.write(f"=== {model} ===\n")
            # This Overall is the weighted total evaluation score
            out.write(f"  Overall: {scores[model].get('Overall', 0):.2f}\n")
            for dim in sorted(all_target_dims):
                if dim != "Overall":
                    out.write(f"  {dim}: {scores[model].get(dim, 0):.2f}\n")
            out.write("\n")

        out.write("\n======= Dimension Ranking Details =======\n\n")
        for dim in sorted(all_target_dims):
            ranking = sorted([(m, scores[m].get(dim, 0)) for m in scores],
                             key=lambda x: x[1],
                             reverse=True)
            out.write(f"【Dimension: {dim}】\n")
            for model, sc in ranking:
                out.write(f"  {model}: {sc:.2f}\n")
            out.write("\n")

        out.write("\n======= Skipped Samples =======\n")
        out.write(
            ", ".join(map(str, skipped_samples)) if skipped_samples else "None")

        # ================= Baseline vs Candidate Overall Raw Scores =================
        out.write(
            "\n\n======= Baseline vs Candidate 【Overall Raw Scores】 =======\n\n")

        for baseline in sorted(raw_scores_map.keys()):
            out.write(f"### Baseline: {baseline} ###\n")
            overall_map = raw_scores_map[baseline].get("Overall", {})

            for candidate in sorted(overall_map.keys()):
                raw_overall = overall_map.get(candidate, 0.0)
                out.write(f"  vs {candidate}: {raw_overall:.2f}\n")

            out.write("\n")

    print(f"Statistics completed: {OUTPUT_TXT}")
