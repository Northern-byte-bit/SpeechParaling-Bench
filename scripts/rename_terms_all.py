#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

def main():
    root = Path.cwd()
    mapping = [
        ("控制_抽象", "con_abs"),
        ("控制_短单", "con_short_sin"),
        ("控制_长单", "con_long_sin"),
        ("控制_短多", "con_short_mul"),
        ("控制_长多", "con_long_mul"),
        ("适应_单维度", "sit_sin"),
        ("适应_多维度", "sit_mul"),
        ("能力", "_ability"),
        ("抽象风格控制", "con_abs"),
        ("短文本", "short"),
        ("长文本", "long"),
        ("单维度", "sin"),
        ("多维度", "mul"),
        ("集合", "_set"),
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
