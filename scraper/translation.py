from typing import TypedDict


# 同人作品页面翻译
class Translation(TypedDict):
    AGE: str  # 年龄指定
    GENRE: str  # 分类
    RELEASE_DATE: str  # 贩卖日
    SERIES_NAME: str  # 系列名
    PRODUCT_FORMAT: str  # 作品类型
    EVENT: str  # 活动
    AUTHOR: str  # 作者
    SCENARIO: str  # 剧情
    ILLUSTRATION: str  # 插画
    MUSIC: str  # 音乐
    VOICE_ACTOR: str  # 声优
