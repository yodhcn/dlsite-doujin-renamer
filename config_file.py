import json
import os
import re
from typing import Annotated, Optional, Union, Literal
from pydantic import Field
from jsonschema import Draft202012Validator
from typing_extensions import TypedDict
from pydantic import TypeAdapter, ConfigDict
from scraper import Locale

FilenameStr = Annotated[str, Field(pattern=r'^[^\/:*?"<>|]*$', description="""不能含有系统保留字[^\/:*?`<>|]*""")]
RjcodeStr = Annotated[str, Field(pattern=re.compile(r".*rjcode.*"), description='template 应是一个包含 "rjcode" 的字符串')]

class Config(TypedDict):
    __pydantic_config__ = ConfigDict()

    # scaner
    scaner_max_depth: int
    # scraper
    scraper_locale: Locale
    scraper_connect_timeout: int
    scraper_read_timeout: int
    scraper_sleep_interval: int
    scraper_http_proxy: Optional[str]
    # renamer
    renamer_template: RjcodeStr
    renamer_release_date_format: str # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    renamer_exclude_square_brackets_in_work_name_flag: bool
    renamer_illegal_character_to_full_width_flag: bool
    renamer_make_folder_icon: bool
    renamer_remove_jpg_file: bool
    renamer_delimiter: FilenameStr  # 分隔符
    renamer_cv_list_left: FilenameStr
    renamer_cv_list_right: FilenameStr
    renamer_tags_max_number: int  # 标签个数上限
    renamer_tags_ordered_list: list[Union[str, list[str]]]
    renamer_age_cat_map_gen: str
    renamer_age_cat_map_r15: str
    renamer_age_cat_map_r18: str
    renamer_age_cat_left: FilenameStr
    renamer_age_cat_right: FilenameStr
    renamer_age_cat_ignore_r18: bool
    renamer_mode: Literal["RENAME", "MOVE", "LINK"]
    renamer_move_root: str
    renamer_move_template: RjcodeStr


ta = TypeAdapter(Config)


DEFAULT_CONFIG: Config = {
    # scaner
    'scaner_max_depth': 5,
    # scraper
    'scraper_locale': 'ja_jp',
    'scraper_connect_timeout': 10,
    'scraper_read_timeout': 10,
    'scraper_sleep_interval': 3,
    'scraper_http_proxy': None,
    # renamer
    'renamer_template': 'age_cat[maker_name][rjcode] work_name cv_list_str',
    'renamer_release_date_format': '%y%m%d',
    'renamer_exclude_square_brackets_in_work_name_flag': True,
    'renamer_illegal_character_to_full_width_flag': False,
    'renamer_make_folder_icon': True,
    'renamer_remove_jpg_file': True,
    'renamer_delimiter': " ",
    'renamer_cv_list_left': "(CV ",
    'renamer_cv_list_right': ")",
    'renamer_tags_max_number': 5,
    'renamer_tags_ordered_list': ["标签1", ["标签2", "替换2"], "标签3"],  # 标签顺序列表，每一项可为字符串或[原标签,替换名]
    'renamer_age_cat_map_gen': "全年龄",
    'renamer_age_cat_map_r15': "R15",
    'renamer_age_cat_map_r18': "R18",
    'renamer_age_cat_left': "(",
    'renamer_age_cat_right': ")",
    'renamer_age_cat_ignore_r18': True,
    'renamer_mode': 'RENAME',
    'renamer_move_root': 'RENAMER_MOVE_ROOT',
    'renamer_move_template': 'maker_name/age_cat[rjcode] work_name cv_list_str'
}


class ConfigFile(object):
    def __init__(self, file_path: str):
        self.__config: Config = None
        self.__config_dict = None
        self.__file_path = file_path
        if not os.path.isfile(file_path):
            self.save_config(DEFAULT_CONFIG)

    def load_config_dict(self):
        """
        从配置文件中读取配置
        """
        with open(self.__file_path, encoding='UTF-8') as file:
            config_dict = json.load(file)
            self.__config_dict = config_dict

    def save_config(self, config: Config):
        """
        保存配置到文件
        """
        with open(self.__file_path, 'w', encoding='UTF-8') as file:
            json.dump(config, file, indent=2, ensure_ascii=False)

    @property
    def file_path(self):
        return self.__file_path

    @property
    def config(self):
        return self.__config

    def verify_config(self) -> list[str]:
        """
        验证配置是否合理
        """
        schema = ta.json_schema()
        validator = Draft202012Validator(schema)
        strerror_list: list[str] = []

        for i, error in enumerate(validator.iter_errors(self.__config_dict), 1):
            description = error.schema.get('description', None)
            if description:
                strerror_list.append(
                    "\n".join(["- 错误: " + error.message,
                               "  校验器: " + error.validator,
                               "  描述:" + description]))
            else:
                strerror_list.append(
                    "\n".join(["- 错误: " + error.message,
                               "  校验器: " + error.validator]))
        if len(strerror_list) == 0:
            self.__config = Config(**self.__config_dict)

        return strerror_list
