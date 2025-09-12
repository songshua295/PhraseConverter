#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dd2sg.py
把“多多格式”（字词<TAB>编码）转换成“搜狗格式”（编码,出现次数=字词）
出现次数从 1 开始，按该编码在文件中出现的顺序递增。
用法：
    1) 带参数：python dd2sg.py 输入文件-多多格式.txt
    2) 无参数：运行后提示“请输入文件路径:”
"""

import os
import sys
from collections import defaultdict

def process_file(path):
    """
    返回行列表：['编码,次数=字词', ...]
    """
    out_lines = []
    counter = defaultdict(int)          # 用来记录每个编码已出现的次数
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n\r')
            if not line or '\t' not in line:
                continue
            word, code = line.split('\t', 1)
            word = word.strip()
            code = code.strip()
            if not code:
                continue
            counter[code] += 1
            out_lines.append(f"{code},{counter[code]}={word}")
    return out_lines

def main():
    # 读取路径
    if len(sys.argv) >= 2:
        in_path = sys.argv[1]
    else:
        in_path = input("请输入文件路径: ").strip('"')

    if not os.path.isfile(in_path):
        print(f"文件不存在：{in_path}")
        sys.exit(1)

    base, ext = os.path.splitext(in_path)
    out_path = f"{base}-搜狗格式{ext if ext else '.txt'}"

    converted = process_file(in_path)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(converted))

    print(f"转换完成，共 {len(converted)} 条记录，已保存到：{out_path}")

if __name__ == '__main__':
    main()