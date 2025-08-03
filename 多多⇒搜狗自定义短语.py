#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将「词语\t编码」格式文件转换成「编码,候选位数=词语」格式。
候选位数从 1 开始，按相同编码出现的顺序递增。
输出文件：原文件名_搜狗自定义短语.txt
"""

import sys
import os
from collections import defaultdict

def transform(source_path: str) -> str:
    """
    读取源文件，生成新内容并写入目标文件。
    返回：目标文件完整路径
    """
    # 生成目标文件路径
    base, ext = os.path.splitext(source_path)
    target_path = f"{base}_搜狗自定义短语.txt"

    # 用于记录每个编码已经出现的次数
    counter = defaultdict(int)

    with open(source_path, 'r', encoding='utf-8') as fin, \
         open(target_path, 'w', encoding='utf-8') as fout:
        for line_num, line in enumerate(fin, 1):
            line = line.rstrip('\n\r')
            if not line:
                continue
            try:
                word, code = line.rsplit('\t', 1)   # 允许词语里出现 tab
            except ValueError:
                # 如果某行格式异常，打印提示并跳过
                print(f"[警告] 第 {line_num} 行格式错误，已跳过：{line!r}", file=sys.stderr)
                continue

            counter[code] += 1
            new_line = f"{code},{counter[code]}={word}"
            fout.write(new_line + '\n')

    return target_path


def main():
    # 1. 获取文件路径
    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
    else:
        file_path = input("请输入待处理的文件路径：").strip()

    if not os.path.isfile(file_path):
        print("文件不存在：", file_path)
        sys.exit(1)

    # 2. 转换并输出结果
    target = transform(file_path)
    print("处理完成，已生成：", target)


if __name__ == '__main__':
    main()