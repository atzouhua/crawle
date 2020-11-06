class Config:
    _config_data = {}

    @classmethod
    def set(cls, key: str, value: str):
        cls._config_data[key] = value

    @classmethod
    def get(cls, key: str, default=None):
        v = cls._config_data.get(key)
        if v:
            return v
        return default

    @classmethod
    def batch_set(cls, **kwargs):
        for k, v in kwargs.items():
            cls.set(k, v)
