import os
import csv

def load_variable_mapping(csv_path):
    """
    从CSV文件加载动态变量的映射关系
    """
    mapping = {}
    try:
        with open(csv_path, mode='r', encoding='utf-16-le', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sogou_var = row.get("搜狗", "").strip()
                handxin_var = row.get("手心", "").strip()
                if sogou_var and handxin_var:
                    mapping[sogou_var] = handxin_var
                    mapping[handxin_var] = sogou_var
    except FileNotFoundError:
        print(f"警告：变量映射文件 {csv_path} 未找到！")
    except Exception as e:
        print(f"加载变量映射文件时出错：{e}")
    return mapping

def convert_handxin_to_sogou(input_path, output_path):
    """
    将手心输入法自定义短语格式转换为搜狗输入法自定义短语格式
    手心格式：字母编码=序号,字词
    搜狗格式：字母编码,序号=字词
    """
    try:
        with open(input_path, 'r', encoding='utf-16-le') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        print(f"错误：文件 {input_path} 未找到！")
        return
    except Exception as e:
        print(f"读取文件时出错：{e}")
        return

    output_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "=" in line and "," in line:
            encoding_part, phrase_part = line.split("=", 1)
            encoding_part = encoding_part.strip()
            order, phrase = phrase_part.split(",", 1)
            order = order.strip()
            phrase = phrase.strip()

            sogou_line = f"{encoding_part},{order}={phrase}\n"
            output_lines.append(sogou_line)
        else:
            print(f"警告：格式错误，跳过行：{line}")

    with open(output_path, 'w', encoding='utf-16-le') as outfile:
        outfile.writelines(output_lines)

    print(f"正向转换完成！输出文件已保存到：{output_path}")


def convert_sogou_to_handxin(input_path, output_path):
    """
    将搜狗输入法自定义短语格式转换为手心输入法自定义短语格式
    搜狗格式：字母编码,序号=字词
    手心格式：字母编码=序号,字词
    """
    try:
        with open(input_path, 'r', encoding='utf-16-le') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        print(f"错误：文件 {input_path} 未找到！")
        return
    except Exception as e:
        print(f"读取文件时出错：{e}")
        return

    output_lines = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "," in line and "=" in line:
            encoding_part, phrase = line.split("=", 1)
            encoding_part = encoding_part.strip()
            encoding, order = encoding_part.rsplit(",", 1)
            encoding = encoding.strip()
            order = order.strip()
            phrase = phrase.strip()

            handxin_line = f"{encoding}={order},{phrase}\n"
            output_lines.append(handxin_line)
        else:
            print(f"警告：格式错误，跳过行：{line}")

    with open(output_path, 'w', encoding='utf-16-le') as outfile:
        outfile.writelines(output_lines)

    print(f"逆向转换完成！输出文件已保存到：{output_path}")


def main():
    print("请选择转换方向：")
    print("1. 手心格式 -> 搜狗格式")
    print("2. 搜狗格式 -> 手心格式")
    choice = input("请输入序号（1 或 2）：")

    input_path = input("请输入输入文件的路径：")

    if not os.path.exists(input_path):
        print("错误：输入文件路径无效！")
        return

    base_name, extension = os.path.splitext(input_path)
    if choice == "1":
        output_path = f"{base_name}_搜狗格式{extension}"
        convert_handxin_to_sogou(input_path, output_path)
    elif choice == "2":
        output_path = f"{base_name}_手心格式{extension}"
        convert_sogou_to_handxin(input_path, output_path)
    else:
        print("错误：无效的选项！")


if __name__ == "__main__":
    main()