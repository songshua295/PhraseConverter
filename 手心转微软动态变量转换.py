import os
import csv
from datetime import datetime

def read_mapping(file_path):
    """读取变量映射文件"""
    mapping = {}
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            handin = row.get('手心')
            microsoft = row.get('微软')
            if handin and microsoft:
                mapping[handin] = microsoft
    return mapping

def replace_content(input_file, output_file, mapping):
    """替换内容并写入新文件"""
    with open(input_file, mode='r', encoding='utf-8') as infile:
        content = infile.read()
    
    # 替换内容
    for handin, microsoft in mapping.items():
        content = content.replace(handin, microsoft)
    
    # 写入新文件
    with open(output_file, mode='w', encoding='utf-8') as outfile:
        outfile.write(content)

def main():
    # 提示用户输入文件路径
    input_path = input("输入手心自定义短语的路径：").strip()
    if not os.path.exists(input_path):
        print("文件不存在，请检查路径！")
        return
    
    # 读取变量映射文件
    mapping_path = os.path.join("var", "variable_mapping.csv")
    if not os.path.exists(mapping_path):
        print("变量映射文件不存在，请检查路径！")
        return
    
    mapping = read_mapping(mapping_path)
    
    # 生成输出文件名
    output_path = f"{os.path.splitext(input_path)[0]}_微软动态变量.txt"
    
    # 替换内容并写入新文件
    replace_content(input_path, output_path, mapping)
    print(f"替换完成，结果已保存到：{output_path}")

if __name__ == "__main__":
    main()