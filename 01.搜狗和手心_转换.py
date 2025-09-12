import os

def convert_handxin_to_sogou(input_path, output_path):
    """手心→搜狗：编码=序号,字词  →  编码,序号=字词"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f'错误：文件 {input_path} 未找到！')
        return
    except Exception as e:
        print(f'读取文件时出错：{e}')
        return

    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        if '=' not in ln or ',' not in ln:
            print(f'警告：格式错误，跳过行：{ln}')
            continue
        enc, tail = ln.split('=', 1)
        enc = enc.strip()
        if ',' not in tail:
            print(f'警告：格式错误，跳过行：{ln}')
            continue
        order, phrase = tail.split(',', 1)
        out.append(f'{enc},{order.strip()}={phrase.strip()}\n')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(out)
    print(f'正向转换完成 → {output_path}')


def convert_sogou_to_handxin(input_path, output_path):
    """搜狗→手心：编码,序号=字词  →  编码=序号,字词"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f'错误：文件 {input_path} 未找到！')
        return
    except Exception as e:
        print(f'读取文件时出错：{e}')
        return

    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        if ',' not in ln or '=' not in ln:
            print(f'警告：格式错误，跳过行：{ln}')
            continue
        enc_part, phrase = ln.split('=', 1)
        enc_part = enc_part.strip()
        if ',' not in enc_part:
            print(f'警告：格式错误，跳过行：{ln}')
            continue
        enc, order = enc_part.rsplit(',', 1)
        out.append(f'{enc.strip()}={order.strip()},{phrase.strip()}\n')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(out)
    print(f'逆向转换完成 → {output_path}')


def _make_out_path(input_path, direction):
    """生成输出文件名，防止重复叠加标记"""
    base, ext = os.path.splitext(input_path)
    for tag in ('_手心格式', '_搜狗格式'):
        if base.endswith(tag):
            base = base[:-len(tag)]
    tag = '_搜狗格式' if direction == 1 else '_手心格式'
    return f'{base}{tag}{ext}'


def main():
    print('请选择转换方向：')
    print('1. 手心格式 -> 搜狗格式')
    print('2. 搜狗格式 -> 手心格式')
    choice = input('请输入序号（1 或 2）：').strip()

    raw_path = input('请输入输入文件的路径：').strip(' "')
    if not os.path.isfile(raw_path):
        print('错误：输入文件路径无效！')
        return

    if choice == '1':
        convert_handxin_to_sogou(raw_path, _make_out_path(raw_path, 1))
    elif choice == '2':
        convert_sogou_to_handxin(raw_path, _make_out_path(raw_path, 2))
    else:
        print('错误：无效的选项！')


if __name__ == '__main__':
    main()