import logging

from pymysql.cursors import DictCursor
from pymysql import connect


class DB:

    def __init__(self):
        self.conn = connect("database.cbh9dwaszqbf.ap-southeast-1.rds.amazonaws.com", "root", "hack3321",
                            'crawle', 12306, charset='utf8mb4')
        self.cur = self.conn.cursor(cursor=DictCursor)

    def __enter__(self):
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    @classmethod
    def one(cls, sql):
        return cls.query_internal(sql, None, 'fetchone')

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
                Logging.get(__name__).exception(e)
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
    print(DB.update('ii_mgstage', [{'alias': 99}, {'t': 11}], '1=1'))
