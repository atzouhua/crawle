from cloudant import Cloudant


class CloudAntDB:

    def __init__(self, account_name, api_key, database='crawler'):
        self.client = Cloudant.iam(account_name, api_key, connect=True)
        self.db = self.client.create_database(database)

    def save(self, data: dict):
        _id = data.get('_id')
        if not _id or _id not in self.db:
            return self.db.create_document(data)

        document = self._get_document(_id)
        for k, v in data.items():
            document[k] = v
        document.save()
        return document

    def delete(self, data, _id=None):
        if _id is None:
            _id = data['_id']
        document = self._get_document(_id)
        document.delete()
        return True

    def count(self):
        return self.db.all_docs()['total_rows']

    def _get_document(self, _id):
        return self.db[_id]

    def close(self):
        self.client.disconnect()
