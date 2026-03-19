import os
import json
from collections import defaultdict

# ===== Batch Input & Output Root Directories =====
INPUT_ROOT = "judge_data/result_v5/result_v5_sit_ada/metadata"
OUTPUT_ROOT = "judge_data/result_v5/result_v5_sit_ada/judge_result"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# ================= Main Loop: Statistical analysis per dataset =================
for folder_name in sorted(os.listdir(INPUT_ROOT)):

    JSON_DIR = os.path.join(INPUT_ROOT, folder_name)
    if not os.path.isdir(JSON_DIR):
        continue

    suffix = folder_name.replace("metadata_", "", 1)
    OUTPUT_TXT = os.path.join(OUTPUT_ROOT, f"result_{suffix}.txt")

    print(f"\nStart processing: {JSON_DIR}")

    # scores[model][dim] stores final calculated scores (Candidate raw, Baseline weighted)
    scores = defaultdict(lambda: defaultdict(float))

    # raw_scores_map[baseline][dim][candidate] stores raw win/loss counts for baseline vs different candidates
    raw_scores_map = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float)))

    # candidate_dim_scores[candidate][dim] stores candidate raw scores (as weight base)
    candidate_dim_scores = defaultdict(lambda: defaultdict(float))

    skipped_samples = []
    sub_dims_set = set()  # Record all sub-dimensions

    # ================= 1. Read data and aggregate raw distribution =================
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

            # --- Statistical logic: Update both sub-dimension and "Overall" dimension ---
            target_dims = [dim, "Overall"]

            if winner_pos == 0:  # Draw
                for d in target_dims:
                    candidate_dim_scores[candidate][d] += 0.5
                    raw_scores_map[baseline][d][candidate] += 0.5
            elif winner_pos == candidate_pos:  # Candidate wins
                for d in target_dims:
                    candidate_dim_scores[candidate][d] += 1.0
            else:  # Baseline wins
                for d in target_dims:
                    raw_scores_map[baseline][d][candidate] += 1.0

    # ================= 2. Core logic: Weighted score calculation (incl. Overall) =================

    # Define all dimensions participating in calculation (sub-dimensions + Overall)
    all_dims = sorted(list(sub_dims_set)) + ["Overall"]

    # A. Candidate uses raw scores directly
    for cand, dim_dict in candidate_dim_scores.items():
        for dim, val in dim_dict.items():
            scores[cand][dim] = val

    # B. Baseline uses weighted scores based on its opponent's performance
    for b_name, dim_dict in raw_scores_map.items():
        for dim, cand_val_map in dim_dict.items():
            compare_candidates = list(cand_val_map.keys())

            # Calculate total raw score for this dimension as weight base
            dim_weight_base = sum(candidate_dim_scores[c][dim]
                                  for c in compare_candidates)

            if dim_weight_base == 0:
                avg_weight = 1.0 / len(
                    compare_candidates) if compare_candidates else 0
                for c_name, raw_val in cand_val_map.items():
                    scores[b_name][dim] += raw_val * avg_weight
            else:
                for c_name, raw_val in cand_val_map.items():
                    # Weight = (Candidate's performance in this dimension) / (Total performance of all relevant candidates in this dimension)
                    weight = candidate_dim_scores[c_name][dim] / dim_weight_base
                    scores[b_name][dim] += raw_val * weight

    # ================= 3. Sorting logic =================
    # Sort by weighted "Overall" dimension score
    model_ranking = sorted(scores.keys(),
                           key=lambda m: scores[m].get("Overall", 0),
                           reverse=True)

    # ================= 4. Write file =================
    os.makedirs(os.path.dirname(OUTPUT_TXT), exist_ok=True)
    with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
        out.write("======= Final Scores for Each Model (incl. independently weighted Overall dimension) =======\n\n")

        for model in model_ranking:
            overall_sc = scores[model].get("Overall", 0)
            out.write(f"=== {model} ===\n")
            out.write(f"  Overall: {overall_sc:.2f}\n")
            # Print sub-dimensions
            for dim in sorted(list(sub_dims_set)):
                out.write(f"  {dim}: {scores[model].get(dim, 0):.2f}\n")
            out.write("\n")

        out.write("\n======= Dimension Ranking (incl. Overall) =======\n\n")
        for dim in all_dims:
            dim_ranking = sorted([(m, scores[m].get(dim, 0)) for m in scores],
                                 key=lambda x: x[1],
                                 reverse=True)
            out.write(f"【Dimension: {dim}】\n")
            for model, sc in dim_ranking:
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
