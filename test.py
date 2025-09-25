#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键三输出 · 全 UTF-16 LE 版
百度/搜狗/微软 六向互转
所有 txt 文件统一以 UTF-16 LE 落盘
"""
import os
import sys
import struct
import time
import io
from typing import List, NamedTuple

# -------------------- 基础数据结构 --------------------
class Entry(NamedTuple):
    word: str
    code: str
    order: int

Table = List[Entry]

# -------------------- UTF-16 LE 专用读写 --------------------
def read_utf16le_lines(path: str) -> List[str]:
    try:
        with open(path, 'r', encoding='utf-16-le') as f:
            return [ln.rstrip('\n') for ln in f]
    except Exception as e:
        print(f'警告：{e}，尝试忽略错误继续读取')
        with open(path, 'r', encoding='utf-16-le', errors='ignore') as f:
            return [ln.rstrip('\n') for ln in f]

def write_utf16le_lines(path: str, lines: List[str]):
    with open(path, 'w', encoding='utf-16-le') as f:
        f.writelines(f'{ln}\n' for ln in lines)
    print(f'已保存 → {path}')

# -------------------- 1. 百度 ↔ 搜狗 -----------------
def load_baidu(path: str) -> Table:
    return [Entry(word=word, code=code, order=int(order))
            for ln in read_utf16le_lines(path)
            for code, order_word in [ln.strip().split('=', 1)]
            for order, word in [order_word.split(',', 1)]]

def save_baidu(path: str, table: Table):
    write_utf16le_lines(path, [f'{e.code}={e.order},{e.word}' for e in table])

def load_sogou(path: str) -> Table:
    tbl = []
    for ln in read_utf16le_lines(path):
        ln = ln.strip()
        if not ln or ln.startswith('#') or ln.startswith(';'):
            continue
        if '=' not in ln:
            print(f'[警告] 跳过无效行（无等号）: {ln[:30]}...')
            continue
        enc_order, word = ln.split('=', 1)
        if ',' not in enc_order:
            print(f'[警告] 跳过无效行（无逗号）: {ln[:30]}...')
            continue
        enc, order = enc_order.rsplit(',', 1)
        tbl.append(Entry(word.strip(), enc.strip(), int(order.strip())))
    return tbl

def save_sogou(path: str, table: Table):
    write_utf16le_lines(path, [f'{e.code},{e.order}={e.word}' for e in table])

# --- 新增函数：保存为 Rime 格式（UTF-8），增加权重转换 ---
def save_rime(path: str, table: Table):
    """保存词库为 Rime 短语格式，UTF-8编码，并转换权重"""
    # Rime格式：word<tab>code<tab>weight
    lines = []
    for e in table:
        # 权重计算：将搜狗的 order 转换为 Rime 权重
        # order 越小，权重越大，排序越靠前
        # 更正公式为 (20 - order)，提供更大的通用性
        weight = (20 - e.order)
        # 确保权重值不为负数
        if weight < 0:
            weight = 0
        lines.append(f'{e.word}\t{e.code}\t{weight}')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(f'{ln}\n' for ln in lines)
    print(f'已保存 → {path}')
# ----------------------------------------------


# -------------------- 微软 dat 解析/生成（防 truncated） ----------
def load_ms(path: str) -> Table:
    with open(path, 'rb') as f:
        data = f.read()
    r = io.BytesIO(data)

    r.seek(0x10)
    off_base, entry_base, entry_end, count = struct.unpack('<4I', r.read(16))
    tbl = []

    # 预读所有偏移量
    r.seek(off_base)
    offsets = [struct.unpack('<I', r.read(4))[0] for _ in range(count)]
    offsets.append(entry_end - entry_base)
    for i in range(count):
        start = entry_base + offsets[i]
        end = entry_base + offsets[i + 1]
        r.seek(start)

        r.read(4)
        code_len = struct.unpack('<H', r.read(2))[0]
        order = r.read(1)[0]
        r.read(1 + 8)
        code_bytes = r.read(code_len - 0x12)
        r.read(2)
        word_bytes = r.read(end - r.tell())
        code = code_bytes.decode('utf-16-le', errors='ignore')
        word = word_bytes.split(b'\x00\x00')[0].decode('utf-16-le', errors='ignore')
        tbl.append(Entry(word, code, order))
    return tbl


def save_ms(path: str, table: Table):
    buf = io.BytesIO()
    stamp = int(time.time())

    # ---- 头部固定字段 ----
    buf.write(b"mschxudp\x02\x00`\x00\x01\x00\x00\x00")
    buf.write(struct.pack('<I', 0x40))
    entry_table_offset = 0x40 + 4 * len(table)
    buf.write(struct.pack('<I', entry_table_offset))
    buf.write(b'\x00' * 4)
    buf.write(struct.pack('<I', len(table)))
    buf.write(struct.pack('<I', stamp))
    buf.write(b'\x00' * 32)
    entries_blob = []
    offset = 0
    for e in table:
        code_bytes = e.code.encode('utf-16-le')
        word_bytes = e.word.encode('utf-16-le')
        entry_head = (
            b'\x10\x00\x10\x00' +
            struct.pack('<H', len(code_bytes) + 18) +
            e.order.to_bytes(1, 'little') +
            b'\x06' +
            b'\x00\x00\x00\x00' +
            struct.pack('<I', stamp)
        )
        entry_blob = entry_head + code_bytes + b'\x00\x00' + word_bytes + b'\x00\x00'
        entries_blob.append(entry_blob)
        if len(entries_blob) < len(table):
            offset += len(entry_blob)
            buf.write(struct.pack('<I', offset))
    for blob in entries_blob:
        buf.write(blob)
    final = buf.getvalue()
    final = final[:0x18] + struct.pack('<I', len(final)) + final[0x1C:]
    with open(path, 'wb') as f:
        f.write(final)
    print(f'已保存 → {path}')

# -------------------- 3. 一键三输出逻辑 --------------
def main():
    print('============ 一键三输出互转工具（全 UTF-16 LE） ============')
    print('1. 百度(.ini) → 搜狗(.txt) + 微软(.dat)')
    print('2. 搜狗(.txt) → 百度(.ini) + 微软(.dat)')
    print('3. 微软(.dat) → 百度(.ini) + 搜狗(.txt)')
    print('4. 搜狗(.txt) → Rime 短语词库（.txt）')
    print('============================================================')
    try:
        src = int(input('请选择你的源格式序号：').strip())
        if src not in (1, 2, 3, 4):
            raise ValueError
    except ValueError:
        print('请输入 1/2/3/4 ！')
        return

    src_path = input('请输入源文件路径：').strip(' "')
    if not os.path.isfile(src_path):
        print('文件不存在！')
        return

    base = os.path.splitext(src_path)[0]
    if src == 1:
        table = load_baidu(src_path)
        save_sogou(f'{base}_搜狗.txt', table)
        save_ms(f'{base}_微软.dat', table)
    elif src == 2:
        table = load_sogou(src_path)
        save_baidu(f'{base}_百度.ini', table)
        save_ms(f'{base}_微软.dat', table)
    elif src == 3:
        table = load_ms(src_path)
        save_baidu(f'{base}_百度.ini', table)
        save_sogou(f'{base}_搜狗.txt', table)
    elif src == 4:
        table = load_sogou(src_path)
        save_rime(f'{base}_Rime.txt', table)

    print('全部转换完成！')

if __name__ == '__main__':
    main()