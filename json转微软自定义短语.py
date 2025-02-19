import struct
import time
import json
from typing import List, Dict


# 生成 Record
def generate_record(py_text: str, string_text: str, rank: int = 2) -> bytes:
    # Record Head
    record_head = 0x100010

    # 拼音和字符串以 UTF-16LE 编码（wchar_t）
    py_encoded = py_text.encode("utf-16le")
    str_encoded = string_text.encode("utf-16le")

    pinyin_len = 16 + len(py_encoded) + 2

    # 打包 Record 结构
    record_bytes = struct.pack(
        "<I H B B 2I",
        record_head,  # recordHead
        pinyin_len,  # pyLen
        rank,  # rank
        0x06,  # rankPad (填充字节)
        0,
        0,  # unknown[2]
    )
    record_bytes += py_encoded  # 拼音部分
    record_bytes += struct.pack("<H", 0)  # 跳过两个字节
    record_bytes += str_encoded  # 字符串部分
    record_bytes += struct.pack("<H", 0)  # 跳过两个字节

    return record_bytes


# 生成 Header
def generate_header(
    offset_start: int, data_start: int, file_len: int, item_cnt: int, timestamp: int
) -> bytes:
    header = struct.pack(
        "<8s 2I 4I 1Q 3Q",
        b"mschxudp",  # proto
        6291458,
        1,  # version[2]
        offset_start,  # offsetStart
        data_start,  # dataStart
        file_len,  # fileLen
        item_cnt,  # itemCnt
        timestamp,  # time
        0,
        0,
        0,  # empty[3]
    )

    return header


# 生成 Offset 表
def generate_offset(records: List[bytes]) -> bytes:
    offset = 0
    offset_bytes = b""
    for i in range(len(records)):
        offset_bytes += struct.pack("<I", offset)
        offset += len(records[i])

    return offset_bytes


# 生成 DAT 文件
def generate_dat(filename: str, data: List[Dict]) -> None:
    # 生成 Record
    records = []
    cur_offset = 0
    for entry in data:
        record = generate_record(entry["py"], entry["str"], entry["rank"])
        records.append(record)
        cur_offset += len(record)

    # 生成 Offset 表
    offset_bytes = generate_offset(records)

    # 生成 Header
    offset_start = 0x40  # header 固定部分的长度
    data_start = offset_start + len(offset_bytes)
    timestamp = int(time.time())
    header_bytes = generate_header(
        offset_start, data_start, data_start + cur_offset, len(records), timestamp
    )

    # 将 Header 和所有 Record 写入到文件中
    with open(filename, "wb") as f:
        f.write(header_bytes)
        f.write(offset_bytes)
        for record in records:
            f.write(record)

    print(f"{filename} generated.")


if __name__ == "__main__":
    print("请输入输入文件路径（JSON文件）：")
    # input_file = input().strip()
    input_file = "手心自定义短语.json"
    print("请输入输出文件路径（DAT文件，默认为Output.dat）：")
    output_file = input().strip() or "微软自定义短语.dat"

    try:
        with open(input_file, "r", encoding="utf-16-le") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误：文件 {input_file} 未找到。")
    except json.JSONDecodeError:
        print(f"错误：文件 {input_file} 不是有效的JSON格式。")
    else:
        generate_dat(output_file, data)