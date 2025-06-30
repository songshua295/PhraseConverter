import os
import struct
import time
import io
from typing import List, NamedTuple

# 定义 Entry 类型
class Entry(NamedTuple):
    word: str
    code: str
    order: int  # 序号字段

# 定义 Table 类型
Table = List[Entry]

# ---- dat 转 txt ----
def ReadUint32(file):
    return struct.unpack('<I', file.read(4))[0]

def ReadUint16(file):
    return struct.unpack('<H', file.read(2))[0]

def Decode(data: bytes, encoding: str) -> str:
    return data.decode(encoding)

def Parse(filename: str) -> Table:
    with open(filename, 'rb') as f:
        data = f.read()
    r = io.BytesIO(data)
    ret = []

    # 词库偏移量
    r.seek(0x10)
    offset_start = ReadUint32(r)  # 偏移表开始
    entry_start = ReadUint32(r)  # 词条开始
    entry_end = ReadUint32(r)    # 词条结束
    entry_count = ReadUint32(r)  # 词条数
    export_time = ReadUint32(r)  # 导出的时间
    t = time.gmtime(export_time)
    print(time.strftime("%Y-%m-%d %H:%M:%S", t), entry_end)

    # 第一个偏移量
    offset = 0
    for i in range(entry_count):
        if i == entry_count - 1:
            length = entry_end - entry_start - offset
        else:
            r.seek(offset_start + 4 * (i + 1))
            next_offset = ReadUint32(r)
            length = next_offset - offset

        r.seek(offset + entry_start)
        offset = next_offset
        ReadUint32(r)  # 0x10001000
        code_len = ReadUint16(r)  # 编码字节长 + 0x12
        order = r.read(1)[0]  # 顺序
        r.read(1)  # 0x06 不明
        ReadUint32(r)  # 4 个空字节
        ReadUint32(r)  # 时间戳
        tmp = r.read(code_len - 0x12)
        code = Decode(tmp, 'utf-16-le')
        r.read(2)  # 两个空字节
        tmp = r.read(length - code_len - 2)
        word = Decode(tmp, 'utf-16-le')
        print(code, word, order)
        ret.append(Entry(word, code, order))

    return ret

def SaveToTxt(entries: Table, output_file: str):
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(f"{entry.code},{entry.order}={entry.word}\n")  # 使用新格式：编码,序号=字词
    print(f"解析结果已保存到 {output_file}")

# ---- txt 转 dat ----
def GetUint32(value: int) -> bytes:
    return struct.pack('<I', value)

def GetUint16(value: int) -> bytes:
    return struct.pack('<H', value)

def Encode(text: str, encoding: str) -> bytes:
    return text.encode(encoding)

def Gen(table: Table) -> bytes:
    buf = io.BytesIO()
    stamp = int(time.time())
    buf.write(b"mschxudp\x02\x00`\x00\x01\x00\x00\x00")
    buf.write(GetUint32(0x40))
    buf.write(GetUint32(0x40 + 4 * len(table)))
    buf.write(b"\x00\x00\x00\x00")  # 文件总长度（稍后填充）
    buf.write(GetUint32(len(table)))
    buf.write(GetUint32(stamp))
    buf.write(b"\x00" * 28)
    buf.write(b"\x00" * 4)

    words = []
    codes = []
    sum_ = 0
    for i, entry in enumerate(table):
        word = Encode(entry.word, "utf-16-le")
        code = Encode(entry.code, "utf-16-le")
        words.append(word)
        codes.append(code)
        if i != len(table) - 1:
            sum_ += len(word) + len(code) + 20
            buf.write(GetUint32(sum_))

    for i, entry in enumerate(table):
        buf.write(b"\x10\x00\x10\x00")
        buf.write(GetUint16(len(codes[i]) + 18))
        buf.write(entry.order.to_bytes(1, byteorder='little'))
        buf.write(b"\x06")
        buf.write(b"\x00" * 4)
        buf.write(GetUint32(stamp))
        buf.write(codes[i])
        buf.write(b"\x00\x00")
        buf.write(words[i])
        buf.write(b"\x00\x00")

    # 填充文件总长度
    data = buf.getvalue()
    buf.seek(0x18)
    buf.write(GetUint32(len(data)))
    return buf.getvalue()

def SaveToDat(table: Table, output_file: str):
    data = Gen(table)
    with open(output_file, 'wb') as f:
        f.write(data)
    print(f"生成的 .dat 文件已保存到 {output_file}")

# ---- 主程序 ----
def main():
    print("欢迎使用微软自定义短语转换工具\n====！！！！！请注意输入输出时的txt均为utf8编码，请注意转换！！！！=====")
    print("1. dat 转 txt")
    print("2. txt 转 dat")
    choice = input("请选择操作 (1 或 2): ")

    if choice == "1":
        input_file = input("请输入 .dat 文件路径 (默认为 微软.dat): ").strip() or "微软.dat"
        output_file = input("请输入输出的 .txt 文件路径 (默认为 手心.txt): ").strip() or "手心.txt"
        if not os.path.exists(input_file):
            print(f"错误：文件 {input_file} 不存在！")
            return
        entries = Parse(input_file)
        SaveToTxt(entries, output_file)
    elif choice == "2":
        input_file = input("请输入 .txt 文件路径 (默认为 手心.txt): ").strip() or "手心.txt"
        output_file = input("请输入输出的 .dat 文件路径 (默认为 微软.dat): ").strip() or "微软.dat"
        if not os.path.exists(input_file):
            print(f"错误：文件 {input_file} 不存在！")
            return
        table = []
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # 解析新格式：编码,序号=字词
                parts = line.split(",", 1)
                if len(parts) != 2:
                    print(f"格式错误：{line}")
                    continue
                code_part, word_part = parts
                code = code_part.strip()
                word_part = word_part.strip()
                if "=" not in word_part:
                    print(f"格式错误：{word_part}")
                    continue
                order_str, word = word_part.split("=", 1)
                try:
                    order = int(order_str)
                except ValueError:
                    print(f"序号不是数字：{order_str}")
                    continue
                table.append(Entry(word, code, order))
        SaveToDat(table, output_file)
    else:
        print("无效的选择，请重新运行程序并选择 1 或 2。")

if __name__ == "__main__":
    main()