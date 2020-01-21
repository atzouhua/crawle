class RuleException(Exception):

    def __init__(self, error):
        Exception.__init__(self)
        self.error = error

    def __str__(self):
        return self.error


class HttpException(Exception):

    def __init__(self, error, url):
        Exception.__init__(self)
        self.error = error
        self.url = url

    def __str__(self):
        return '[%s] %s' % (self.url, self.error)


class UserException(Exception):

    def __init__(self, error):
        Exception.__init__(self)
        self.error = error

    def __str__(self):
        return self.error
