import os
import re
import pandas as pd
import numpy as np

# 配置路径
base_dir = "judge_data/result_v5"
output_dir = "judge_data/score_calculate/final_results"
os.makedirs(output_dir, exist_ok=True)

# 模块配置：定义每个模块对应的前缀和文件个数
modules_config = {
    "Para_con": {
        "files":
        ["abstract", "long_multi", "long_sin", "short_multi", "short_sin"],
        "constant": 911
    },
    "Sit_ada": {
        "files": ["multi", "sin"],
        "constant": 280
    },
    "Dyn_var": {
        "files": ["dyn"],
        "constant": 120
    }
}

# 归一化因子
divisors = np.array([100 / 911, 100 / 280, 100 / 120, 100 / 1311])


def extract_overall_score(file_path):
    """从TXT文件中提取每个模型的Overall得分"""
    scores = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用正则匹配模型块和Overall得分
    # 模式: === model_name ===\n\s+Overall: score
    model_blocks = re.findall(
        r'===\s*(\w+[\w-]*)\s*===\n\s+Overall:\s*([\d.]+)', content)
    for model, score in model_blocks:
        scores[model.lower()] = float(score)
    return scores


def process_language(lang):
    """处理特定语言 (ch 或 en) 的数据"""
    all_models = set()
    data = {}

    # 1. 提取原始数据
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

    # 2. 构建 DataFrame
    df = pd.DataFrame(index=list(all_models))
    for module in modules_config.keys():
        df[module] = pd.Series(data[module])

    # 填充缺失值
    df = df.fillna(0)

    # 3. Baseline 特殊公式计算
    # 确定 Baseline
    baseline = "doubao" if lang == "ch" else "gemini"

    def apply_special_formula(col, constant):
        col_vals = col.copy()
        candidates = col_vals.drop(baseline, errors='ignore')

        # 公式: Constant - (Sum(Candidate^2) / Sum(Candidate))
        sum_sq = (candidates**2).sum()
        sum_val = candidates.sum()
        if sum_val != 0:
            col_vals[baseline] = constant - (sum_sq / sum_val)
        return col_vals

    # 应用到三个模块
    for module, config in modules_config.items():
        df[module] = apply_special_formula(df[module], config["constant"])

    # 4. 计算总分 (Overall_A)
    # 必须明确相加的列名
    df["Overall"] = df[list(modules_config.keys())].sum(axis=1)
    df["Overall"] = apply_special_formula(df["Overall"], 1311)

    # 5. 归一化
    # 顺序：Para, Sit, Dyn, Overall
    cols_to_norm = ["Para_con", "Sit_ada", "Dyn_var", "Overall"]
    df[cols_to_norm] = df[cols_to_norm].values * divisors

    # 6. 重命名和调整顺序
    df = df.rename(
        columns={
            "Para_con": "Paralanguage Control",
            "Sit_ada": "Situational Adaptation",
            "Dyn_var": "Dynamic Variation"
        })

    # 顺序：Overall, Paralanguage Control, Dynamic Variation, Situational Adaptation
    df = df[[
        "Overall", "Paralanguage Control", "Dynamic Variation",
        "Situational Adaptation"
    ]]

    # 降序排列
    df = df.sort_values(by="Overall", ascending=False)

    return df


# 执行计算并保存
for lang in ["ch", "en"]:
    result_df = process_language(lang)
    output_path = os.path.join(output_dir, f"final_scores_{lang}.csv")
    result_df.round(2).to_csv(output_path)
    print(f"--- {lang.upper()} Models Final Scores ---")
    print(result_df.round(2))
    print(f"Saved to {output_path}\n")
