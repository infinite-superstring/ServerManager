from django.core.cache import cache
from util.logger import Log
import threading


class CacheUtil:
    __cache = None
    __logger = Log
    __lock = threading.Lock()

    def __init__(self):
        self.__cache = cache

    def set(self, key, value, timeout=None):
        with self.__lock:
            try:
                self.__cache.set(key, value, timeout)
            except Exception as e:
                self.__logger.error(f"Error setting cache for Key='{key}': {e}")

    def get(self, key):
        with self.__lock:
            try:
                return self.__cache.get(key)
            except Exception as e:
                self.__logger.error(f"Error getting cache for Key='{key}': {e}")
                return None

    def delete(self, key):
        with self.__lock:
            try:
                result = self.__cache.delete(key)
                if result == 0:
                    self.__logger.warning(f"Cache delete: Key='{key}' not found")
                return result
            except Exception as e:
                self.__logger.error(f"Error deleting cache for Key='{key}': {e}")
                return False

    def set_many(self, mapping, timeout=None):
        with self.__lock:
            try:
                self.__cache.set_many(mapping, timeout)
            except Exception as e:
                self.__logger.error(f"Error setting multiple caches: {e}")

    def get_many(self, keys):
        with self.__lock:
            try:
                return self.__cache.get_many(keys)
            except Exception as e:
                self.__logger.error(f"Error getting multiple caches: {e}")
                return {}

    def add(self, key, value, timeout=None):
        with self.__lock:
            try:
                self.__cache.add(key, value, timeout)
            except Exception as e:
                self.__logger.error(f"Error adding cache for Key='{key}': {e}")

    def clear(self):
        with self.__lock:
            try:
                self.__cache.clear()
            except Exception as e:
                self.__logger.error(f"Error clearing cache: {e}")
