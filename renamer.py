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
            exclude_square_brackets_in_work_name_flag: bool = False,  # 设为 True 时，移除 work_name 中【】及其间的内容
    ):
        if 'rjcode' not in template:
            raise ValueError  # 重命名不能丢失 rjcode
        self.__scaner = scaner
        self.__scraper = scraper
        self.__template = template
        self.__exclude_square_brackets_in_work_name_flag = exclude_square_brackets_in_work_name_flag

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

        cv_list = metadata['cvs']
        cv_list_str = '(' + ' '.join(cv_list) + ')' if len(cv_list) > 0 else ''
        new_name = new_name.replace('cv_list_str', cv_list_str)

        # 文件名中不能包含 Windows 系统的保留字符
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
