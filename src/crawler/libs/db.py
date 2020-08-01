import logging

import psycopg2
from psycopg2.extras import RealDictCursor

from crawler.libs.common import PG_PASSWORD


class DB:

    def __init__(self):
        self.conn = psycopg2.connect(host='satao.db.elephantsql.com', user='hyzyvxsn',
                                     password=PG_PASSWORD,
                                     database='hyzyvxsn')
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    @classmethod
    def one(cls, sql, params=None):
        return cls.query_internal(sql, params, 'fetchone')

    @classmethod
    def all(cls, sql):
        return cls.query_internal(sql, None, 'fetchall')

    @classmethod
    def insert(cls, table, data: dict):
        sql = cls._format_insert(table, data)
        return cls.query_internal(sql, tuple(data.values()), 'lastrowid')

    @classmethod
    def update(cls, table, data: dict, where: str):
        sql = cls._format_update(table, data, where)
        return cls.query_internal(sql, tuple(data.values()), 'rowcount')

    @classmethod
    def insert_all(cls, table, data: list):
        sql = cls._format_insert(table, data[0], 'REPLACE')
        params = []
        for i in data:
            params.append(tuple(i.values()))

        del data
        result = None
        with DB() as db:
            try:
                db.executemany(sql, params)
                result = db.rowcount
            except Exception as e:
                logging.getLogger(__name__).exception(e)
        return result

    @classmethod
    def query_internal(cls, sql, params=None, method=None):
        data = None
        with DB() as db:
            try:
                db.execute(sql, params)
                if method:
                    invert_op = getattr(db, method)
                    if callable(invert_op):
                        data = invert_op()
                    else:
                        data = invert_op
            except Exception as e:
                logging.exception(e)
            return data

    @classmethod
    def _format_insert(cls, table, data: dict, t='INSERT'):
        fields = list(data.keys())
        _value = '%s,' * len(fields)
        fields = ','.join(fields)
        return '{} INTO {} ({}) VALUES ({})'.format(t, table, fields, _value.strip(','))

    @classmethod
    def _format_update(cls, table, data: dict, where):
        fields = []
        for k, v in data.items():
            fields.append("{} = %s".format(k))
        fields = ','.join(fields)
        return 'UPDATE {} SET {} WHERE {}'.format(table, fields, where)


# res = DB.insert("insert into ii_mgstage (title, url) values ('test', 'test')")

# res = DB.all('select * from ii_mgstage')
# print(res)
if __name__ == '__main__':
    print(DB.query_internal("select * from pg_class where relname = 'crawle_tasks' limit 1", None, 'fetchone'))
