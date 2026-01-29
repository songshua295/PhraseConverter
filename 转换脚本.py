#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜狗、百度（同手心）、微软、rime自定义短语格式转换脚本
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
    lines = []
    try:
        with open(path, 'r', encoding='utf-16-le') as f:
            lines = [ln.rstrip('\n') for ln in f]
    except Exception as e:
        print(f'警告：{e}，尝试忽略错误继续读取')
        with open(path, 'r', encoding='utf-16-le', errors='ignore') as f:
            lines = [ln.rstrip('\n') for ln in f]
    
    # 去除可能的 BOM (\ufeff)
    if lines and lines[0].startswith('\ufeff'):
        lines[0] = lines[0].lstrip('\ufeff')
    return lines

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

# --- Rime 格式读写 ---
def load_rime(path: str) -> Table:
    """从 Rime 短语词库文件（UTF-8）加载词条"""
    tbl = []
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            for ln in f:
                ln = ln.strip()
                # 忽略注释和空行
                if not ln or ln.startswith('#'):
                    continue
                parts = ln.split('\t')
                if len(parts) < 2:
                    print(f'[警告] 跳过无效 Rime 行: {ln[:30]}...')
                    continue
                word = parts[0]
                code = parts[1]
                weight = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 20
                order = 20 - weight
                if order < 1:
                    order = 1
                tbl.append(Entry(word, code, order))
    except Exception as e:
        print(f"读取 Rime 文件时出错: {e}")
        return []
    return tbl

def save_rime(path: str, table: Table):
    """保存词库为 Rime 短语格式，UTF-8编码，并转换权重"""
    lines = []
    for e in table:
        weight = 20 - e.order
        if weight < 0:
            weight = 0
        lines.append(f'{e.word}\t{e.code}\t{weight}')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(f'{ln}\n' for ln in lines)
    print(f'已保存 → {path}')

# -------------------- 多多 格式读写 --------------------
def load_duoduo(path: str) -> Table:
    tbl = []
    for ln in read_utf16le_lines(path):
        ln = ln.strip()
        if not ln or ln.startswith('#') or ln.startswith(';'):
            continue
        parts = ln.split('\t')
        if len(parts) < 2:
            continue
        word = parts[0].strip()
        code = parts[1].strip()
        tbl.append(Entry(word, code, 1))
    return tbl

def save_duoduo(path: str, table: Table):
    write_utf16le_lines(path, [f'{e.word}\t{e.code}' for e in table])

# -------------------- 微软 dat 解析/生成（防 truncated） ----------
def load_ms(path: str) -> Table:
    with open(path, 'rb') as f:
        data = f.read()
    r = io.BytesIO(data)

    r.seek(0x10)
    off_base, entry_base, entry_end, count = struct.unpack('<4I', r.read(16))
    tbl = []

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

# -------------------- 3. 一键四输出逻辑 --------------
def main():
    print('============ 一键四输出互转工具（全 UTF-16 LE） ============')
    print('1. 百度(.ini) → 搜狗 + 微软 + Rime + 多多')
    print('2. 搜狗(.txt) → 百度 + 微软 + Rime + 多多')
    print('3. 微软(.dat) → 百度 + 搜狗 + Rime + 多多')
    print('4. Rime(.txt) → 百度 + 搜狗 + 微软 + 多多')
    print('5. 多多(.txt) → 百度 + 搜狗 + 微软 + Rime')
    print('============================================================')
    
    # 提示默认选择 1
    src_input = input('请选择你的源格式序号 (默认 1): ').strip()
    if not src_input:
        src = 1
    else:
        try:
            src = int(src_input)
            if src not in (1, 2, 3, 4, 5):
                raise ValueError
        except ValueError:
            print('请输入 1-5 之间的数字！')
            return

    # 根据选择设置默认文件名并给出提示
    default_filename = None
    if src == 2:
        default_filename = 'PhraseEdit.txt'
    elif src == 4:
        default_filename = 'custom_phrase_double.txt'
    elif src == 5:
        default_filename = '多多自定义短语.txt'
    
    prompt_text = '请输入源文件路径'
    if default_filename:
        prompt_text += f' (默认 {default_filename})'
    
    src_path_input = input(f'{prompt_text}: ').strip(' "')

    # 使用默认文件名
    if not src_path_input and default_filename:
        src_path = default_filename
    elif src_path_input:
        src_path = src_path_input
    else:
        print('警告：未指定文件路径！')
        return

    if not os.path.isfile(src_path):
        print(f'文件不存在！({src_path})')
        return

    base = os.path.splitext(src_path)[0]
    
    print(f'正在转换文件: {src_path}')

    # 采用固定的名字的格式，这样更迭更方便
    if src == 1:
        table = load_baidu(src_path)
        save_sogou(f'PhraseEdit.txt', table)
        save_ms(f'微软.dat', table)
        save_rime(f'Rime自定义短语.txt', table)
        save_duoduo(f'多多自定义短语.txt', table)
    elif src == 2:
        table = load_sogou(src_path)
        save_baidu(f'百度.ini.txt', table)
        save_ms(f'微软.dat', table)
        save_rime(f'Rime自定义短语.txt', table)
        save_duoduo(f'多多自定义短语.txt', table)
    elif src == 3:
        table = load_ms(src_path)
        save_baidu(f'百度.ini.txt', table)
        save_sogou(f'PhraseEdit.txt', table)
        save_rime(f'Rime自定义短语.txt', table)
        save_duoduo(f'多多自定义短语.txt', table)
    elif src == 4:
        table = load_rime(src_path)
        save_baidu(f'百度.ini.txt', table)
        save_sogou(f'PhraseEdit.txt', table)
        save_ms(f'微软.dat', table)
        save_duoduo(f'多多自定义短语.txt', table)
    elif src == 5:
        table = load_duoduo(src_path)
        save_baidu(f'百度.ini.txt', table)
        save_sogou(f'PhraseEdit.txt', table)
        save_ms(f'微软.dat', table)
        save_rime(f'Rime自定义短语.txt', table)

    print('全部转换完成！')

if __name__ == '__main__':
    main()
