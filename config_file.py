import json
import os
import re
from typing import TypedDict, Final, Optional

from scraper import Locale


class Config(TypedDict):
    scaner_max_depth: int
    scraper_locale: str
    scraper_connect_timeout: int
    scraper_read_timeout: int
    scraper_sleep_interval: int
    scraper_http_proxy: Optional[str]
    renamer_template: str
    renamer_exclude_square_brackets_in_work_name_flag: bool


class ConfigFile(object):
    DEFAULT_CONFIG: Final[Config] = {
        'scaner_max_depth': 5,
        'scraper_locale': 'zh_cn',
        'scraper_connect_timeout': 10,
        'scraper_read_timeout': 10,
        'scraper_sleep_interval': 3,
        'scraper_http_proxy': None,
        'renamer_template': '[maker_name][rjcode] work_name cv_list_str',
        'renamer_exclude_square_brackets_in_work_name_flag': False,
    }

    def __init__(self, file_path: str):
        self.__file_path = file_path
        if not os.path.isfile(file_path):
            self.save_config(ConfigFile.DEFAULT_CONFIG)

    def load_config(self):
        """
        从配置文件中读取配置
        """
        with open(self.__file_path, encoding='UTF-8') as file:
            config_dict: Config = json.load(file)
            return config_dict

    def save_config(self, config_dict: Config):
        """
        保存配置到文件
        """
        with open(self.__file_path, 'w', encoding='UTF-8') as file:
            json.dump(config_dict, file, indent=2, ensure_ascii=False)

    @property
    def file_path(self):
        return self.__file_path

    @staticmethod
    def verify_config(config_dict: Config):
        """
        验证配置是否合理
        """
        scaner_max_depth = config_dict.get('scaner_max_depth', None)
        scraper_locale = config_dict.get('scraper_locale', None)
        scraper_connect_timeout = config_dict.get('scraper_connect_timeout', None)
        scraper_read_timeout = config_dict.get('scraper_read_timeout', None)
        scraper_http_proxy = config_dict.get('scraper_http_proxy', None)
        scraper_sleep_interval = config_dict.get('scraper_sleep_interval', None)
        renamer_template = config_dict.get('renamer_template', None)
        renamer_exclude_square_brackets_in_work_name_flag = \
            config_dict.get('renamer_exclude_square_brackets_in_work_name_flag', None)

        strerror_list = []

        # 检查 scaner_max_depth
        if not isinstance(scaner_max_depth, int) or scaner_max_depth < 0:
            strerror_list.append('scaner_max_depth 应是一个大于等于 0 的整数')

        # 检查 scraper_locale
        locale_name_list: list[str] = []
        for locale in Locale:
            locale_name_list.append(locale.name)
        if scraper_locale not in locale_name_list:
            strerror_list.append(f'scraper_locale 应是 {locale_name_list} 中的一个')

        # 检查 scraper_connect_timeout
        if not isinstance(scraper_connect_timeout, int) or scraper_connect_timeout <= 0:
            strerror_list.append('scraper_connect_timeout 应是一个大于 0 的整数')

        # 检查 scraper_read_timeout
        if not isinstance(scraper_read_timeout, int) or scraper_read_timeout <= 0:
            strerror_list.append('scraper_read_timeout 应是一个大于 0 的整数')

        # 检查 scraper_sleep_interval
        if not isinstance(scraper_sleep_interval, int) or scraper_sleep_interval < 0:
            strerror_list.append('scraper_sleep_interval 应是一个大于等于 0 的整数')

        # 检查 scraper_http_proxy
        http_proxy_pattern = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:(\d+)")
        str_error_http_proxy = f'scraper_http_proxy 应是形如 "http://127.0.0.1:7890" 的 http 代理；或设为 null，这将使用系统代理'
        if isinstance(scraper_http_proxy, str):
            if not http_proxy_pattern.fullmatch(scraper_http_proxy):
                # 是字符串但不匹配正则规则
                strerror_list.append(str_error_http_proxy)
        elif scraper_http_proxy is not None:
            # 既不是字符串也不是 None
            strerror_list.append(str_error_http_proxy)

        # 检查 renamer_template
        if not isinstance(renamer_template, str) or 'rjcode' not in renamer_template:
            strerror_list.append('renamer_template 应是一个包含 "rjcode" 的字符串')

        # 检查 renamer_exclude_square_brackets_in_work_name_flag
        if not isinstance(renamer_exclude_square_brackets_in_work_name_flag, bool):
            strerror_list.append('renamer_exclude_square_brackets_in_work_name_flag 应是一个布尔值')

        return strerror_list
