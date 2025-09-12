#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert2dd.py
将“编码,数字=字词”格式转换成“字词<TAB>编码”格式（多多输入法格式）
用法：
    1) 带参数：python convert2dd.py 输入文件.txt
    2) 无参数：运行后会提示“请输入文件路径:”
"""

import re
import os
import sys

def convert_line(line: str):
    line = line.rstrip('\n\r')
    m = re.fullmatch(r'\s*([^,=]+),\s*(\d+)\s*=\s*(.+?)\s*$', line)
    if not m:
        return None
    code, _, word = m.groups()
    if not word:
        return None
    return word, code

def process_file(path):
    out = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            res = convert_line(line)
            if res:
                word, code = res
                out.append(f"{word}\t{code}")
    return out

def main():
    # 若命令行无参数，则用 input() 读路径
    if len(sys.argv) >= 2:
        in_path = sys.argv[1]
    else:
        in_path = input("请输入文件路径: ").strip('"')

    if not os.path.isfile(in_path):
        print(f"文件不存在：{in_path}")
        sys.exit(1)

    base, ext = os.path.splitext(in_path)
    out_path = f"{base}-多多格式{ext if ext else '.txt'}"

    converted = process_file(in_path)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(converted))

    print(f"转换完成，共 {len(converted)} 条记录，已保存到：{out_path}")

if __name__ == '__main__':
    main()