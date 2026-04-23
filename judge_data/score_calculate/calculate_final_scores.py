import os
import re
import pandas as pd
import numpy as np

# Configure paths
base_dir = "judge_data/result_v5"
output_dir = "judge_data/score_calculate/final_results"
os.makedirs(output_dir, exist_ok=True)

# Module settings: define file suffixes and constants per module
modules_config = {
    "para_con": {
        "files":
        ["abstract", "long_multi", "long_sin", "short_multi", "short_sin"],
        "constant": 911
    },
    "sit_ada": {
        "files": ["multi", "sin"],
        "constant": 280
    },
    "dyn_var": {
        "files": ["dyn"],
        "constant": 120
    }
}

# Normalization factors
divisors = np.array([100 / 911, 100 / 280, 100 / 120, 100 / 1311])


def extract_overall_score(file_path):
    """Extract each model's Overall score from a TXT file."""
    scores = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Use regex to match model blocks and Overall scores.
    # Pattern: capture the full "=== model_name ===" line,
    # followed by an "Overall: score" line.
    model_blocks = re.findall(r'^===\s*(.*?)\s*===\s*\n\s+Overall:\s*([\d.]+)',
                              content, re.MULTILINE)
    for model, score in model_blocks:
        scores[model.lower()] = float(score)
    return scores


def process_language(lang):
    """Process data for a specific language (ch or en)."""
    all_models = set()
    data = {}

    # 1. Extract raw scores
    for module, config in modules_config.items():
        module_sum = {}
        for file_name_part in config["files"]:
            file_path = os.path.join(base_dir, f"result_v5_{module}",
                                     "judge_result",
                                     f"result_v5_{file_name_part}_{lang}.txt")
            if os.path.exists(file_path):
                scores = extract_overall_score(file_path)
                for model, score in scores.items():
                    all_models.add(model)
                    module_sum[model] = module_sum.get(model, 0) + score
        data[module] = module_sum

    # 2. Build DataFrame
    df = pd.DataFrame(index=list(all_models))
    for module in modules_config.keys():
        df[module] = pd.Series(data[module])

    # Fill missing values
    df = df.fillna(0)

    # 3. Apply the special baseline formula
    # Determine baseline model by language
    baseline = "doubao" if lang == "ch" else "gemini"

    def apply_special_formula(col, constant):
        col_vals = col.copy()
        candidates = col_vals.drop(baseline, errors='ignore')

        # Formula: Constant - (Sum(Candidate^2) / Sum(Candidate))
        sum_sq = (candidates**2).sum()
        sum_val = candidates.sum()
        if sum_val != 0:
            col_vals[baseline] = constant - (sum_sq / sum_val)
        return col_vals

    # Apply formula to the three modules
    for module, config in modules_config.items():
        df[module] = apply_special_formula(df[module], config["constant"])

    # 4. Calculate total score (Overall)
    # Explicitly sum only the target module columns
    df["Overall"] = df[list(modules_config.keys())].sum(axis=1)
    df["Overall"] = apply_special_formula(df["Overall"], 1311)

    # 5. Normalize scores
    # Order: Para, Sit, Dyn, Overall
    cols_to_norm = ["para_con", "sit_ada", "dyn_var", "Overall"]
    df[cols_to_norm] = df[cols_to_norm].values * divisors

    # 6. Rename columns and reorder
    df = df.rename(
        columns={
            "para_con": "Paralanguage Control",
            "sit_ada": "Situational Adaptation",
            "dyn_var": "Dynamic Variation"
        })

    # Final column order:
    # Overall, Paralanguage Control, Dynamic Variation, Situational Adaptation
    df = df[[
        "Overall", "Paralanguage Control", "Dynamic Variation",
        "Situational Adaptation"
    ]]

    # Sort descending by Overall
    df = df.sort_values(by="Overall", ascending=False)

    return df


# Run calculation and save results
for lang in ["ch", "en"]:
    result_df = process_language(lang)
    output_path = os.path.join(output_dir, f"final_scores_{lang}.csv")
    result_df.round(2).to_csv(output_path)
    print(f"--- {lang.upper()} Models Final Scores ---")
    print(result_df.round(2))
    print(f"Saved to {output_path}\n")
