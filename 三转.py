#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 需要安装的包：pip install chardet
# 删除微软自定义短语可用一下cmd命令
# del "%APPDATA%\Microsoft\InputMethod\Chs\ChsPinyinEUDPv1.lex"
"""
一键三输出 · 自动编码检测版
手心/搜狗/微软 六向互转
所有 txt 文件统一以 UTF-8 落盘
"""
import os
import sys
import struct
import time
import io
from typing import List, NamedTuple

try:
    import chardet
except ImportError:
    print('需安装 chardet：pip install chardet')
    sys.exit(1)

# -------------------- 基础数据结构 --------------------
class Entry(NamedTuple):
    word: str
    code: str
    order: int

Table = List[Entry]

# -------------------- 自动编码转换 ---------------------
def detect_encoding(path: str) -> str:
    raw = open(path, 'rb').read(100_000)  # 取前 100 KB 足够
    res = chardet.detect(raw)
    return res['encoding'] or 'utf-8'

def auto_read(path: str) -> List[str]:
    enc = detect_encoding(path)
    try:
        with open(path, 'r', encoding=enc) as f:
            lines = [ln.rstrip('\n') for ln in f]
        if enc and enc.lower() not in {'utf-8', 'ascii'}:
            print(f'[提示] 检测到文件编码：{enc.upper()} → 已自动转 UTF-8 缓存')
        return lines
    except Exception as e:
        print(f'警告：{e}，尝试 UTF-8 带忽略模式')
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [ln.rstrip('\n') for ln in f]

def write_lines(path: str, lines: List[str], encoding: str = 'utf-8'):
    with open(path, 'w', encoding=encoding) as f:
        f.writelines(f'{ln}\n' for ln in lines)
    print(f'已保存 → {path}')

# -------------------- 1. 手心 ↔ 搜狗 -----------------
def load_handxin(path: str) -> Table:
    return [Entry(word=word, code=code, order=int(order))
            for ln in auto_read(path)
            for code, order_word in [ln.strip().split('=', 1)]
            for order, word in [order_word.split(',', 1)]]

def save_handxin(path: str, table: Table):
    write_lines(path, [f'{e.code}={e.order},{e.word}' for e in table])

def load_sogou(path: str) -> Table:
    tbl = []
    for ln in auto_read(path):
        if not ln or ln.startswith('#'):
            continue
        enc_order, word = ln.split('=', 1)
        enc, order = enc_order.rsplit(',', 1)
        tbl.append(Entry(word.strip(), enc.strip(), int(order.strip())))
    return tbl

def save_sogou(path: str, table: Table):
    write_lines(path, [f'{e.code},{e.order}={e.word}' for e in table])

# -------------------- 2. 微软 dat 解析/生成 ----------
def load_ms(path: str) -> Table:
    r = io.BytesIO(open(path, 'rb').read())
    r.seek(0x10)
    off_base, entry_base, entry_end, count = struct.unpack('<4I', r.read(16))
    tbl = []
    for i in range(count):
        r.seek(off_base + 4 * i)
        off = struct.unpack('<I', r.read(4))[0]
        r.seek(entry_base + off)
        r.read(4)  # magic
        code_len = struct.unpack('<H', r.read(2))[0]
        order = r.read(1)[0]
        r.seek(r.tell() + 1 + 8)
        code = r.read(code_len - 0x12).decode('utf-16-le')
        r.seek(r.tell() + 2)
        word = r.read(entry_end - r.tell()).split(b'\x00\x00')[0].decode('utf-16-le')
        tbl.append(Entry(word, code, order))
    return tbl

def save_ms(path: str, table: Table):
    buf = io.BytesIO()
    stamp = int(time.time())
    buf.write(b"mschxudp\x02\x00`\x00\x01\x00\x00\x00")
    buf.write(struct.pack('<I', 0x40))
    buf.write(struct.pack('<I', 0x40 + 4 * len(table)))
    buf.write(b'\x00' * 4)  # total len
    buf.write(struct.pack('<I', len(table)))
    buf.write(struct.pack('<I', stamp))
    buf.write(b'\x00' * 32)

    sum_ = 0
    for i, e in enumerate(table):
        if i != len(table) - 1:
            sum_ += len(e.word.encode('utf-16-le')) + len(e.code.encode('utf-16-le')) + 20
            buf.write(struct.pack('<I', sum_))

    for e in table:
        buf.write(b'\x10\x00\x10\x00')
        buf.write(struct.pack('<H', len(e.code.encode('utf-16-le')) + 18))
        buf.write(e.order.to_bytes(1, 'little'))
        buf.write(b'\x06\x00\x00\x00\x00')
        buf.write(struct.pack('<I', stamp))
        buf.write(e.code.encode('utf-16-le'))
        buf.write(b'\x00\x00')
        buf.write(e.word.encode('utf-16-le'))
        buf.write(b'\x00\x00')

    data = buf.getvalue()
    data = data[:0x18] + struct.pack('<I', len(data)) + data[0x1C:]
    with open(path, 'wb') as f:
        f.write(data)
    print(f'已保存 → {path}')

# -------------------- 3. 一键三输出逻辑 --------------
def main():
    print('============ 一键三输出互转工具（自动编码检测） ============')
    print('1. 手心 → 搜狗 + 微软')
    print('2. 搜狗 → 手心 + 微软')
    print('3. 微软 → 手心 + 搜狗')
    print('============================================================')
    try:
        src = int(input('请选择你的源格式序号：').strip())
        if src not in (1, 2, 3):
            raise ValueError
    except ValueError:
        print('请输入 1/2/3 ！')
        return

    src_path = input('请输入源文件路径：').strip(' "')
    if not os.path.isfile(src_path):
        print('文件不存在！')
        return

    base = os.path.splitext(src_path)[0]
    # 加载
    if src == 1:
        table = load_handxin(src_path)
        save_sogou(f'{base}_搜狗.txt', table)
        save_ms(f'{base}_微软.dat', table)
    elif src == 2:
        table = load_sogou(src_path)
        save_handxin(f'{base}_手心.txt', table)
        save_ms(f'{base}_微软.dat', table)
    else:
        table = load_ms(src_path)
        save_handxin(f'{base}_手心.txt', table)
        save_sogou(f'{base}_搜狗.txt', table)

    print('全部转换完成！')

if __name__ == '__main__':
    main()