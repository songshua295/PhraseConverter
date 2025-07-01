import csv

def process_csv_file_with_deduplication(csv_filepath, txt_filepath, output_filepath):
    """
    处理CSV文件，根据指定条件删除行，并在第三列值重复时删除后续行，
    将结果保存到新文件。

    Args:
        csv_filepath (str): 输入CSV文件的路径，例如 "C:\\Users\\t295\\Downloads\\csv文件.csv"。
        txt_filepath (str): 包含要匹配的值的文本文件路径，例如 "C:\\Users\\t295\\Downloads\\8105.txt"。
        output_filepath (str): 结果CSV文件的输出路径，例如 "结果.csv"。
    """
    rows_to_keep = []
    
    # 存储已经出现过的第三列的值，用于去重
    seen_third_column_values = set()

    # 读取txt文件中的内容，将其存储在一个集合中以便快速查找
    try:
        with open(txt_filepath, 'r', encoding='utf-8') as f:
            allowed_values = {line.strip() for line in f}
    except FileNotFoundError:
        print(f"错误：未找到文件 '{txt_filepath}'。请检查路径是否正确。")
        return
    except Exception as e:
        print(f"读取文本文件时发生错误：{e}")
        return

    # 读取CSV文件
    try:
        with open(csv_filepath, 'r', encoding='utf-8', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader)  # 读取标题行
            rows_to_keep.append(header)  # 保留标题行

            for row_num, row in enumerate(reader, start=2): # row_num 从2开始，因为第一行是标题
                if len(row) > 2:  # 确保有第三列 (索引为2)
                    third_column_value = row[2]
                    
                    # 检查第三列的值是否包含在允许的值中 并且 之前没有出现过
                    if third_column_value in allowed_values and third_column_value not in seen_third_column_values:
                        rows_to_keep.append(row)
                        seen_third_column_values.add(third_column_value) # 将该值添加到已出现集合中
                    elif third_column_value in seen_third_column_values:
                        # 仅为调试或用户反馈，表示该行因重复而被删除
                        # print(f"第 {row_num} 行因第三列值 '{third_column_value}' 重复而被删除。")
                        pass 
                    else:
                        # 仅为调试或用户反馈，表示该行因不符合txt文件条件而被删除
                        # print(f"第 {row_num} 行因第三列值 '{third_column_value}' 不在允许列表中而被删除。")
                        pass
                else:
                    # 如果行没有足够的列，可以选择保留或删除。这里选择保留。
                    rows_to_keep.append(row)

    except FileNotFoundError:
        print(f"错误：未找到CSV文件 '{csv_filepath}'。请检查路径是否正确。")
        return
    except Exception as e:
        print(f"读取CSV文件时发生错误：{e}")
        return

    # 将结果写入新的CSV文件
    try:
        with open(output_filepath, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(rows_to_keep)
        print(f"处理完成！结果已保存到 '{output_filepath}'。")
    except Exception as e:
        print(f"写入结果文件时发生错误：{e}")

# --- 使用示例 ---
csv_file = r"C:\Users\t295\Downloads\csv文件.csv"
txt_file = r"C:\Users\t295\Downloads\8105.txt"
output_file = "结果.csv"

process_csv_file_with_deduplication(csv_file, txt_file, output_file)