#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert2utf8.py
自动检测文件编码并转存为 UTF-8
"""

import os
import sys
import shutil
import chardet

def detect_encoding(file_path: str, sample_size: int = 1_000_000) -> str:
    """读取文件头 N 字节，返回检测到的编码"""
    with open(file_path, 'rb') as f:
        raw = f.read(sample_size)
    result = chardet.detect(raw)
    return result.get('encoding') or 'utf-8'      # 若检测失败，保守按 utf-8 处理

def convert_to_utf8(src_path: str, dst_path: str, src_encoding: str) -> None:
    """以 src_encoding 读取 src_path，并以 utf-8 写入 dst_path"""
    with open(src_path, 'r', encoding=src_encoding, errors='replace') as fin:
        content = fin.read()
    with open(dst_path, 'w', encoding='utf-8', newline='') as fout:
        fout.write(content)

def build_dst_path(src_path: str) -> str:
    """根据原路径生成目标文件名：原文件名-utf8.扩展名"""
    base, ext = os.path.splitext(src_path)
    return f"{base}-utf8{ext}"

def main():
    # 1. 获取文件路径
    if len(sys.argv) >= 2:
        src = sys.argv[1]
    else:
        src = input("请输入待转换文件路径: ").strip()

    if not os.path.isfile(src):
        print(f"错误：文件不存在 —— {src}")
        sys.exit(1)

    src = os.path.abspath(src)
    dst = build_dst_path(src)

    if os.path.exists(dst):
        ans = input(f"目标文件已存在：{dst} \n是否覆盖？(y/N) ").strip().lower()
        if ans != 'y':
            print("已取消")
            sys.exit(0)

    # 2. 检测编码
    detected = detect_encoding(src)
    print(f"检测到的编码: {detected}")

    # 3. 转换并保存
    try:
        convert_to_utf8(src, dst, detected)
        print("转换完成，已保存为:")
        print(dst)
    except Exception as e:
        print("转换失败：", e)
        sys.exit(1)

if __name__ == '__main__':
    main()