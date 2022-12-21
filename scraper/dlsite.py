import re
from typing import Final
from urllib.parse import unquote

from scraper.locale import Locale
from scraper.langs import EN_US, JA_JP, KO_KR, ZH_CN, ZH_TW
from scraper.translation import Translation


# 读取翻译文件
def _load_translations():
    translations: dict[Locale, Translation] = {
        Locale.en_us: EN_US,
        Locale.ja_jp: JA_JP,
        Locale.ko_kr: KO_KR,
        Locale.zh_cn: ZH_CN,
        Locale.zh_tw: ZH_TW,
    }
    return translations


class Dlsite(object):
    TRANSLATIONS: Final = _load_translations()
    RJCODE_PATTERN: Final = re.compile(r'RJ(\d{6}|\d{8})(?!\d+)')
    RGCODE_PATTERN: Final = re.compile(r'RG(\d{5})(?!\d+)')
    SRICODE_PATTERN: Final = re.compile(r'SRI(\d{10})(?!\d+)')

    # 提取字符串中的 rjcode
    @staticmethod
    def parse_rjcode(string: str):
        match = Dlsite.RJCODE_PATTERN.search(string.upper())
        if match:
            return match.group()
        else:
            return None

    # 根据 rjcode 拼接出同人作品页面的 url
    @staticmethod
    def compile_work_page_url(rjcode: str):
        return f'https://www.dlsite.com/maniax/work/=/product_id/{rjcode}.html'

    # 解析 scraper 链接中携带的参数 (dlsite.com 服务端使用 mod_rewrite 优化 SEO)
    @staticmethod
    def parse_url_params(url: str):
        url = unquote(url)
        split_url = url.split(r'/=/', 1)
        params_str = split_url[1] if len(split_url) == 2 else ''
        params_str_1 = re.sub(r'\?.*$', '', params_str, count=1)
        params_str_2 = re.sub(r'(\.html)?/?$', '', params_str_1)  # 去除 url 的 .html/ 后缀
        params_list = params_str_2.split('/')
        params = {}
        for i in range(0, len(params_list), 2):
            params[params_list[i]] = params_list[i + 1] if i + 1 < len(params_list) else ''
        return params
