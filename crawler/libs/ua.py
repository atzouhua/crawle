import random


class FakerUa:
    os_type = [
        '(Windows NT 6.1; WOW64)',
        '(Windows NT 10.0; WOW64)',
        '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)',
        '(Macintosh; Intel Mac OS X 10_13)',
    ]

    @classmethod
    def get_chrome(cls):
        a = random.randint(55, 69)
        b = random.randint(0, 3200)
        c = random.randint(0, 140)
        chrome_version = 'Chrome/{}.0.{}.{}'.format(a, b, c)
        return ' '.join(
            ['Mozilla/5.0', random.choice(cls.os_type),
             'AppleWebKit/537.36',
             '(KHTML, like Gecko)',
             chrome_version, 'Safari/537.36'])

    @classmethod
    def get_firefox(cls):
        version_num = random.randint(55, 62)
        firefox_version = 'Gecko/20100101 Firefox/{}.0'.format(version_num)
        return ' '.join(
            ['Mozilla/5.0', random.choice(cls.os_type), firefox_version])

    @classmethod
    def get_ua(cls):
        if random.randint(1, 2) == 1:
            return cls.get_chrome()
        return cls.get_firefox()
