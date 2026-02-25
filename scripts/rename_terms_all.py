#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path


def main():
    root = Path.cwd()
    mapping = [
        # ("con_abs", "con_abs"),
        # ("con_short_sin", "con_short_sin"),
        # ("con_long_sin", "con_long_sin"),
        # ("con_short_multi", "con_short_mul"),
        # ("con_long_multi", "con_long_mul"),
        # ("sit_ada_sin", "sit_sin"),
        # ("sit_ada_multi", "sit_mul"),
        # ("能力", "_ability"),
        # ("抽象风格控制", "con_abs"),
        # ("短文本", "short"),
        # ("长文本", "long"),
        # ("单维度", "sin"),
        # ("多维度", "mul"),
        # ("集合", "_set"),
        # ("测试得分", "judge_json"),
        # ("测试元数据", "metadata"),
        # ("模型得分结果", "judge_result"),
        ("可控生成", "para_con"),
        ("情景适应", "sit_ada"),
        ("动态调节", "dyn_var"),
    ]

    def replace_in_name(name: str) -> str:
        out = name
        for old, new in mapping:
            if old in out:
                out = out.replace(old, new)
        return out

    def compute_dst(p: Path) -> Path:
        if not p.exists():
            return p
        new_name = replace_in_name(p.name)
        if new_name == p.name:
            return p
        dst = p.parent / new_name
        if dst.exists():
            base, ext = os.path.splitext(new_name)
            i = 1
            while True:
                candidate = f"{base}_{i}{ext}"
                cand_path = p.parent / candidate
                if not cand_path.exists():
                    dst = cand_path
                    break
                i += 1
        return dst

    # Step 1: rename directories bottom-up
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        for d in list(dirnames):
            src = Path(dirpath) / d
            dst = compute_dst(src)
            if dst != src:
                src.rename(dst)
                print(f"Renamed dir: {src} -> {dst}")

    # Step 2: rename files (top-down)
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        for fname in list(filenames):
            src = Path(dirpath) / fname
            dst = compute_dst(src)
            if dst != src:
                if dst.exists():
                    base, ext = os.path.splitext(dst.name)
                    i = 1
                    while True:
                        candidate = dst.parent / f"{base}_{i}{ext}"
                        if not candidate.exists():
                            dst = candidate
                            break
                        i += 1
                src.rename(dst)
                print(f"Renamed file: {src} -> {dst}")

    print("Renaming completed.")


if __name__ == "__main__":
    main()
