# 合并处理两个UTF-16LE编码的TXT文件
def read_file(file_path, encoding='utf-16le'):
    """读取UTF-16LE编码的文件，返回内容列表"""
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return [line.strip() for line in file if line.strip()]  # 去除空行和换行符
    except Exception as e:
        print(f"读取文件 {file_path} 出错：{e}")
        return []

def extract_code(line):
    """从行中提取编码=序号部分（例如从 '编码=123,测试' 提取 '编码=123'）"""
    if '=' in line and ',' in line:
        code_part = line[:line.find(',')]  # 提取 "编码=123" 部分
        return code_part
    return None

def merge_files(a_path, b_path, output_path, encoding='utf-16le'):
    """合并a和b文件，根据规则生成c文件"""
    # 读取a文件内容
    a_lines = read_file(a_path, encoding)
    # 提取a文件中所有编码=序号
    a_codes = {extract_code(line) for line in a_lines if extract_code(line)}  # 去重

    # 读取b文件内容，并筛选
    b_lines = read_file(b_path, encoding)
    merged_lines = a_lines.copy()  # 复制a文件内容作为基础

    # 检查b文件内容，添加不重复的行
    for b_line in b_lines:
        b_code = extract_code(b_line)
        if b_code and b_code not in a_codes:
            merged_lines.append(b_line)
            a_codes.add(b_code)  # 更新已有的编码集

    # 写入c文件
    try:
        with open(output_path, 'w', encoding=encoding) as output_file:
            for line in merged_lines:
                output_file.write(line + '\n')
        print(f"合并完成，结果已保存到 {output_path}")
    except Exception as e:
        print(f"写入文件 {output_path} 出错：{e}")

def main():
    # 获取文件路径
    a_path = input("请输入a文件的路径（例如：C:/path/to/a.txt）：")
    b_path = input("请输入b文件的路径（例如：C:/path/to/b.txt）：")
    output_path = "c.txt"  # 输出文件默认名为c.txt，可根据需要修改

    # 执行合并
    merge_files(a_path, b_path, output_path)

if __name__ == "__main__":
    main()