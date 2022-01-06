from enum import Enum


# 枚举类 - scraper 支持的语言
class Locale(Enum):
    en_us = 'en_us'
    ja_jp = 'ja_jp'
    ko_kr = 'ko_kr'
    zh_cn = 'zh_cn'
    zh_tw = 'zh_tw'
