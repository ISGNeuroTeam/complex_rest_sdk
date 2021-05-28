from .locmem import LocMemCache


def cache_page(timeout):
    def _decorator(f):
        def _wrap():
            return f()
        return _wrap
    return _decorator


caches = {
    'RedisCache': {},
    'FileCache': {},
    'LocMemCache': {},
    'DatabaseCache': {}
}


def get_cache(base_cache, namespace=None, timeout=None, max_entries=None):
    """
    Create or return existing cache instance
    :param base_cache: one of the configured caches: 'RedisCaches', 'FileCache', 'LocMemCache', 'DatabaseCache'
    :param namespace: string, only letters, case insensitive,
     namespace for the cache, each key will have prefix with that namespace
    :param timeout: default timeout for cache instance
    :param max_entries: max_entries option for cache instance
    :return:
    cache instance
    """
    global caches

    if base_cache not in caches:
        raise ValueError(f'Cache with name {base_cache} not found in CACHES settings')

    if namespace not in caches[base_cache]:
        caches[base_cache][namespace] = LocMemCache(namespace, params={'timeout': timeout, 'max_entries': max_entries})
    return caches[base_cache][namespace]





