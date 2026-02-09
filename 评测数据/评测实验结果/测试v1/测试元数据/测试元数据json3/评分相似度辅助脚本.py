import os
import json
from collections import defaultdict

# ================== 配置区（你只需要改这里） ==================

JSON_DIR = "评测数据/测试v1/测试元数据json3"        # 存放 json 文件的目录
OUTPUT_DIR = "评测数据/测试v1/模型每局得分"  # 输出目录
CANDIDATE_NAME = "gemini"                  # 要统计的 candidate

# ===============================================================


def judge_sample(sample: dict, target_candidate: str):
    """
    返回 result:
        1  -> 胜利
        0  -> 平局
       -1  -> 失败 / 错误
    """

    if sample.get("candidate_name") != target_candidate:
        return None

    winner_position = sample.get("winner_position")
    candidate_position = sample.get("candidate_position")
    status = sample.get("status")

    # 错误
    if status != "Success" or winner_position == -1:
        return -1

    # 平局
    if winner_position == 0:
        return 0

    # 胜负
    if candidate_position == winner_position:
        return 1
    else:
        return -1


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 用 sample_index 做排序用
    results = {}

    for filename in os.listdir(JSON_DIR):
        if not filename.endswith(".json"):
            continue

        file_path = os.path.join(JSON_DIR, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                sample = json.load(f)
        except Exception:
            continue

        if sample.get("candidate_name") != CANDIDATE_NAME:
            continue

        sample_idx = sample.get("sample_index")
        result = judge_sample(sample, CANDIDATE_NAME)

        if sample_idx is not None:
            results[sample_idx] = result

    # 输出文件（只写胜负）
    output_file = os.path.join(
        OUTPUT_DIR, f"{CANDIDATE_NAME}_result3.txt"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        for idx in sorted(results):
            f.write(f"{results[idx]}\n")


if __name__ == "__main__":
    main()

