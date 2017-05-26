_cache = {}


def get(user_id, default=None):
    return _cache.get(user_id, default)


def contains(user_id):
    return _cache.has_key(user_id)


def set(user_id, data=None):
    if data:
        _cache[user_id] = data
    else:
        _cache.pop(user_id, None)


