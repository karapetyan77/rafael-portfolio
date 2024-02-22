from collections import OrderedDict


class MRUCache:
    def __init__(self, capacity: int = 5):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return None

        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            del self.cache[key]

        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)

        self.cache[key] = value
        self.cache.move_to_end(key)
