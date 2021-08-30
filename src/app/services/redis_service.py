from redis import Redis


class __RedisClient:

    def __init__(self):
        self.client = Redis(host='localhost', port=6379, db=0)

    def add_dict(self, key, val: dict, expire=None):
        self.client.hmset(key, val)
        if expire is not None:
            self.client.expire(key, expire)

    def remove(self, keys: list):
        self.client.delete(*keys)

    def count(self, keys: list):
        return self.client.exists(*keys)

    def exists(self, key):
        return self.client.exists(key) > 0

    def get_dict(self, key):
        return self.client.hgetall(key)

    def get_dict_val(self, dict_key, val_key):
        return self.client.hget(dict_key, val_key)

    def add_val(self, key, val, expire=None):
        self.client.set(key, val)
        if expire is not None:
            self.client.expire(key, expire)

    def get_val(self, key):
        return self.client.get(key).encode('utf-8')

    def add_to_set(self, key, val):
        self.client.sadd(key, val)

    def get_set(self, key):
        self.client.smembers(key)

    def remove_from_set(self, key, val):
        self.client.srem(key, val)


redis_client = __RedisClient()
