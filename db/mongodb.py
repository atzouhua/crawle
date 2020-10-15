from typing import Optional

import pymongo
from pymongo.collection import Collection


class MongoDB:

    def __init__(self, dsn=None, collection='root', database='crawler'):
        self._client = pymongo.MongoClient(f"{dsn}?retryWrites=true&w=majority")
        self._db = self._client.get_database(database)
        self._col: Optional[Collection] = self._db.get_collection(collection)

    def set_col(self, name):
        self._col = self._db.get_collection(name)
        return self

    def save(self, data: dict):
        _id = data.get('_id')
        if _id:
            if self._col.find_one(_id):
                return self.update({'_id': _id}, data)
        return self._col.insert_one(data).inserted_id

    def update(self, where, data):
        del data['_id']
        data = {'$set': data}
        return self._col.update_one(where, data).modified_count

    def __getattr__(self, item):
        def call_back(*args, **kwargs):
            func = getattr(self._col, item)
            return func(*args, **kwargs)
        return call_back
