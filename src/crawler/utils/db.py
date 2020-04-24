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
        return cls._query_internal(sql, None, 'fetchone')

    @classmethod
    def all(cls, sql):
        return cls._query_internal(sql, None, 'fetchall')

    @classmethod
    def insert(cls, table, data: dict):
        sql = cls._format_insert(table, data)
        return cls._query_internal(sql, tuple(data.values()), 'lastrowid')

    @classmethod
    def insert_all(cls, table, data: list):
        sql = cls._format_insert(table, data[0])
        params = []
        for i in data:
            params.append(tuple(i.values()))

        del data
        with DB() as db:
            db.executemany(sql, params)
            data = db.rowcount

        return data

    @classmethod
    def query_internal(cls, sql, params, method):
        with DB() as db:
            db.execute(sql, params)
            invert_op = getattr(db, method)
            if callable(invert_op):
                data = invert_op()
            else:
                data = invert_op
        return data

    @classmethod
    def _format_insert(cls, table, data: dict):
        fields = list(data.keys())
        _value = '%s,' * len(fields)
        fields = ','.join(fields)
        return 'INSERT INTO {} ({}) VALUES ({})'.format(table, fields, _value.strip(','))


# res = DB.insert("insert into ii_mgstage (title, url) values ('test', 'test')")

# res = DB.all('select * from ii_mgstage')
# print(res)
# print(DB.insert_all('ii_mgstage', [{'title': 99}, {'title': 10}]))
