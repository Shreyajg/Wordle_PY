import mongomock


class _Cursor:
    def __init__(self, docs):
        self._docs = list(docs)

    async def to_list(self, length=None):
        return self._docs if length is None else self._docs[:length]


class _Collection:
    def __init__(self, collection):
        self._c = collection

    async def find_one(self, *args, **kwargs):
        return self._c.find_one(*args, **kwargs)

    def find(self, *args, **kwargs):
        return _Cursor(self._c.find(*args, **kwargs))

    async def insert_one(self, *args, **kwargs):
        return self._c.insert_one(*args, **kwargs)

    async def replace_one(self, *args, **kwargs):
        return self._c.replace_one(*args, **kwargs)

    async def count_documents(self, *args, **kwargs):
        return self._c.count_documents(*args, **kwargs)

    async def aggregate(self, pipeline):
        return _Cursor(self._c.aggregate(pipeline))


class FakeDatabase:
    def __init__(self):
        self.raw = mongomock.MongoClient(tz_aware=False)["test"]

    def __getitem__(self, name):
        return _Collection(self.raw[name])
