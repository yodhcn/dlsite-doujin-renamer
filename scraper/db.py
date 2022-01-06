from peewee import *

db = SqliteDatabase('cache.db')


class WorkMetadataCache(Model):
    rjcode = CharField(primary_key=True)
    metadata = TextField()

    class Meta:
        database = db  # This model uses the "work_metadata_cache.db" database.
