import logging
import os
import re

from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout

from scaner import Scaner
from scraper import WorkMetadata, Scraper

# Windows 系统的保留字符
# https://docs.microsoft.com/zh-cn/windows/win32/fileio/naming-a-file
# <（小于）
# >（大于）
# ： (冒号)
# "（双引号）
# /（正斜杠）
# \ (反反)
# | (竖线或竖线)
# ? （问号）
# * (星号)
WINDOWS_RESERVED_CHARACTER_PATTERN = re.compile(r'[\\/*?:"<>|]')
WINDOWS_RESERVED_CHARACTER_PATTERN_str = r'\/:*?"<>|'  # 半角字符，原
WINDOWS_RESERVED_CHARACTER_PATTERN_replace_str = '＼／：＊？＂＜＞｜'  # 全角字符，替


def _get_logger():
    # create logger
    logger = logging.getLogger('Renamer')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


class Renamer(object):
    logger = _get_logger()

    def __init__(
            self,
            scaner: Scaner,
            scraper: Scraper,
            template: str = '[maker_name][rjcode] work_name cv_list_str',  # 模板
            delimiter: str = ' ',  # 列表转字符串的分隔符
            exclude_square_brackets_in_work_name_flag: bool = False,  # 设为 True 时，移除 work_name 中【】及其间的内容
            renamer_illegal_character_to_full_width_flag: bool = False,  # 设为 True 时，新文件名将非法字符转为全角；为 False 时直接移除.
            tags_option: dict = None,  # 标签相关设置
    ):
        if 'rjcode' not in template:
            raise ValueError  # 重命名不能丢失 rjcode
        self.__scaner = scaner
        self.__scraper = scraper
        self.__template = template
        self.__delimiter = delimiter
        self.__exclude_square_brackets_in_work_name_flag = exclude_square_brackets_in_work_name_flag
        self.__renamer_illegal_character_to_full_width_flag = renamer_illegal_character_to_full_width_flag
        self.__tags_option = tags_option

    def __compile_new_name(self, metadata: WorkMetadata):
        """
        根据作品的元数据编写出新的文件名
        """
        work_name = re.sub(r'【.*?】', '', metadata['work_name']).strip() \
            if self.__exclude_square_brackets_in_work_name_flag \
            else metadata['work_name']

        template = self.__template
        new_name = template.replace('rjcode', metadata['rjcode'])
        new_name = new_name.replace('work_name', work_name)
        new_name = new_name.replace('maker_id', metadata['maker_id'])
        new_name = new_name.replace('maker_name', metadata['maker_name'])
        new_name = new_name.replace('release_date', metadata['release_date'])

        cv_list = metadata['cvs']  # cv列表
        cv_list_str = '(' + self.__delimiter.join(cv_list) + ')' if len(cv_list) > 0 else ''
        new_name = new_name.replace('cv_list_str', cv_list_str)

        if "tags_list_str" in self.__template:  # 标签列表
            tags_list = []
            tags_list_flag = []
            for i in self.__tags_option['ordered_list']:  # ordered_list中存在的标签
                if isinstance(i, str) and i in metadata['tags']:
                    tags_list.append(i)
                    tags_list_flag.append(i)
                elif isinstance(i, list) and i[0] in metadata['tags']:
                    tags_list.append(i[1])  # 替换新标签
                    tags_list_flag.append(i[0])
            for i in metadata['tags']:  # 剩余的标签
                if not i in tags_list_flag:
                    tags_list.append(i)
            tags_list = tags_list[: self.__tags_option['max_number']]  # 数量限制
            tags_list_str = self.__delimiter.join(tags_list)  # 转字符串，加分隔符
            new_name = new_name.replace('tags_list_str', tags_list_str)

        # 文件名中不能包含 Windows 系统的保留字符
        if self.__renamer_illegal_character_to_full_width_flag:  # 半角转全角
            new_name = new_name.translate(new_name.maketrans(
                WINDOWS_RESERVED_CHARACTER_PATTERN_str, WINDOWS_RESERVED_CHARACTER_PATTERN_replace_str))
        else:  # 直接移除
            new_name = WINDOWS_RESERVED_CHARACTER_PATTERN.sub('', new_name)

        return new_name.strip()

    def rename(self, root_path: str):
        work_folders = self.__scaner.scan(root_path)
        for rjcode, folder_path in work_folders:
            Renamer.logger.info(f'[{rjcode}] -> 发现 RJ 文件夹："{os.path.normpath(folder_path)}"')
            dirname, basename = os.path.split(folder_path)
            try:
                metadata = self.__scraper.scrape_metadata(rjcode)
            except Timeout:
                # 请求超时
                Renamer.logger.warning(f'[{rjcode}] -> 重命名失败：dlsite.com 请求超时！\n')
                continue
            except ConnectionError as err:
                # 遇到其它网络问题（如：DNS 查询失败、拒绝连接等）
                Renamer.logger.warning(f'[{rjcode}] -> 重命名失败：{str(err)}\n')
                continue
            except HTTPError as err:
                # HTTP 请求返回了不成功的状态码
                Renamer.logger.warning(f'[{rjcode}] -> 重命名失败：{err.response.status_code} {err.response.reason}\n')
                continue
            except RequestException as err:
                # requests 引发的其它异常
                Renamer.logger.error(f'[{rjcode}] -> 重命名失败：{str(err)}\n')
                continue

            new_basename = self.__compile_new_name(metadata)
            new_folder_path = os.path.join(dirname, new_basename)
            try:
                os.rename(folder_path, new_folder_path)
                Renamer.logger.info(f'[{rjcode}] -> 重命名成功："{os.path.normpath(new_folder_path)}"\n')
            except FileExistsError as err:
                filename = os.path.normpath(err.filename)
                filename2 = os.path.normpath(err.filename2)
                Renamer.logger.warning(f'[{rjcode}] -> 重命名失败：{err.strerror}："{filename}" -> "{filename2}"\n')
            except OSError as err:
                Renamer.logger.error(f'[{rjcode}] -> 重命名失败：{str(err)}\n')
