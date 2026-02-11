import re
import os
from collections import Counter


def analyze_file_robust(file_path):
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 '{file_path}'")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='gbk') as f:
            text = f.read()

    # --- 关键改进点 ---
    # 1. 先匹配出所有方括号内的内容: [内容]
    # 2. 然后在内容中查找所有 "维度: 特征" 的模式

    # 匹配方括号内部的所有内容
    bracket_pattern = r"\[(.*?)\]"
    brackets = re.findall(bracket_pattern, text)

    all_dimensions = []
    # 针对每一个方括号内的字符串进行二次解析
    for content in brackets:
        # 匹配 "维度: 特征"，考虑到逗号分隔，提取冒号前的非空格部分
        # 匹配逻辑：找 单词/中文 + 冒号
        dim_pairs = re.findall(r"([^,;]+?):\s*[^,;\]]+", content)
        for d in dim_pairs:
            all_dimensions.append(d.strip())

    # 3. 统计
    dim_counts = Counter(all_dimensions)

    # 4. 输出
    output_lines = ["各副语言特征维度被考察的样本数量："]
    for dim, count in dim_counts.most_common():
        output_lines.append(f"{dim}: {count}")

    final_output = "\n".join(output_lines)
    print(final_output)

    with open("feature_count.txt", "w", encoding="utf-8") as f:
        f.write(final_output)
    print(f"\n--- 统计完成 ---")


if __name__ == "__main__":
    # 请确保路径正确，Windows路径建议使用原始字符串 r''
    analyze_file_robust(r'D:\MLLM\Benchmark\想法2\sit_ada能力\多标签\多标签共情集合.txt')
