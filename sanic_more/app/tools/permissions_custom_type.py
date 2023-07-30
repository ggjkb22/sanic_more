# Author: Q
# Date:   2023-5-17
# Desc:   权限自定义数据类型


class LevelPermissionDict(dict):
    """带等级的权限汇总字典"""
    def __missing__(self, key):
        return None

    def __setitem__(self, key, value):
        if self[key] is None:
            super().__setitem__(key, value)
        else:
            if self[key] < value:
                super().__setitem__(key, value)