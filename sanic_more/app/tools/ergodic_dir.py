# Author: Q
# Date:   2023-6-28
# Desc:   遍历文件夹函数


import os
from typing import List


def traverse_folders(directory: str) -> List[str]:
    """获取指定目录下的文件夹列表(不包含双下划线开头的文件夹)"""
    dirs_list = []
    # 获取指定目录下文件夹列表(不包含双下划线开头的文件夹)
    items = os.listdir(directory)
    for item in items:
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and not item.startswith("_"):
            dirs_list.append(item)
    return dirs_list
