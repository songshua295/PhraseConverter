import os

def create_nomedia_in_media_folders(path):
    """
    遍历指定路径下的文件夹，如果包含图片或视频文件，则创建.nomedia文件
    :param path: 输入的文件夹路径
    :return: None
    """
    # 定义常见的图片和视频文件扩展名
    media_extensions = (
        # 图片格式
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
        # 视频格式
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'
    )
    
    # 遍历路径下的所有文件夹和文件
    for root, dirs, files in os.walk(path):
        # 检查当前文件夹中的文件是否包含图片或视频
        for file in files:
            if file.lower().endswith(media_extensions):
                # 如果包含媒体文件，创建.nomedia文件
                nomedia_path = os.path.join(root, '.nomedia')
                if not os.path.exists(nomedia_path):
                    with open(nomedia_path, 'w') as f:
                        f.write('')  # 创建空文件
                    print(f"Created .nomedia in: {root}")
                break  # 找到一个媒体文件后即可跳出循环，无需继续检查

if __name__ == "__main__":
    # 获取用户输入的路径
    input_path = input("请输入文件夹路径: ")
    
    # 检查路径是否存在
    if os.path.exists(input_path) and os.path.isdir(input_path):
        create_nomedia_in_media_folders(input_path)
        print("处理完成！")
    else:
        print("路径不存在或不是文件夹，请检查输入！")