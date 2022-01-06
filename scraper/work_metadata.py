from typing import TypedDict


# 同人作品元数据
class WorkMetadata(TypedDict):
    rjcode: str
    work_name: str
    maker_id: str
    maker_name: str
    release_date: str
    series_id: str
    series_name: str
    age_category: str
    tags: list[str]
    cvs: list[str]
