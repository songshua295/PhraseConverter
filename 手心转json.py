import json

# 定义输入文件路径
input_file = input("请输入手心自定义短语文件路径:")
# input_file = "手心自定义短语.txt"

# 定义输出文件路径
output_file = "手心自定义短语.json"

# 初始化一个列表来存储所有JSON对象
json_data = []

# 打开并读取文件
with open(input_file, "r", encoding="utf-16-le") as file:
    for line in file:
        # 去掉每行的首尾空白字符
        line = line.strip()
        if not line:
            continue  # 跳过空行
        
        # 按照格式解析每行
        try:
            # 分割每行数据
            parts = line.split("=")[1].split(",")
            py = line.split("=")[0]  # zym 对应 py
            rank = int(parts[0])  # 第二个部分对应 rank
            str_value = parts[1]  # 第三个部分对应 str
            
            # 添加到JSON对象列表
            json_data.append({
                "py": py,
                "rank": rank,
                "str": str_value
            })
        except Exception as e:
            print(f"解析错误: {line} - {e}")

# 将JSON对象列表转换为JSON格式字符串
json_output = json.dumps(json_data, ensure_ascii=False, indent=4)

# 将结果写入到指定的输出文件
with open(output_file, "w", encoding="utf-16-le") as outfile:
    outfile.write(json_output)

print(f"JSON数据已成功写入到文件 {output_file}")