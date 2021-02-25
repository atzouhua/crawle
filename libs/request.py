class Request:

    def __init__(self, url, callback, data=dict):
        self.url = url
        self.callback = callback
        self.data = data
        self.doc = None
        self.index = 0
        self.total = 0
