import os

from scraper import Dlsite


class Scaner(object):
    def __init__(self, max_depth=5):
        self.__max_depth = max_depth

    def scan(self, root_path: str, _depth=0):
        """
        生成器。深层遍历所有含 rjcode 的文件夹
        """
        if os.path.isdir(root_path):  # 检查是否是文件夹
            folder = os.path.basename(root_path)
            rjcode = Dlsite.parse_rjcode(folder)
            if rjcode:  # 检查文件夹名称中是否含RJ号
                yield rjcode, root_path
            elif _depth < self.__max_depth:
                dir_list = os.listdir(root_path)
                for folder in dir_list:
                    folder_path = os.path.join(root_path, folder)
                    yield from self.scan(folder_path, _depth + 1)
