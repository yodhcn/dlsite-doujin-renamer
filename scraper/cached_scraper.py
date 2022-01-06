import json

from scraper.db import db, WorkMetadataCache
from scraper.locale import Locale
from scraper.scraper import Scraper
from scraper.work_metadata import WorkMetadata


class CachedScraper(Scraper):
    def __init__(self, locale: Locale, proxies=None, connect_timeout: int = 10, read_timeout: int = 10, sleep_interval=3):
        super().__init__(locale, proxies, connect_timeout, read_timeout, sleep_interval)
        db.connect()
        db.create_tables([WorkMetadataCache])

    def __del__(self):
        db.close()

    def scrape_metadata(self, rjcode: str):
        # 在数据库中查找
        metadata_cache = WorkMetadataCache.get_or_none(WorkMetadataCache.rjcode == rjcode)
        if metadata_cache:
            # 已缓存，返回数据库中缓存的 metadata
            metadata: WorkMetadata = json.loads(metadata_cache.metadata)
            return metadata
        else:
            # 未缓存，从 scraper 抓取 metadata 并缓存到数据库
            metadata = super().scrape_metadata(rjcode)
            WorkMetadataCache.create(rjcode=rjcode, metadata=json.dumps(metadata, indent=2, ensure_ascii=False))
            return metadata
