"""
内存缓存模块（15分钟过期）
"""
from datetime import datetime, timedelta
from typing import Any, Optional
import hashlib
import json


class Cache:
    """简单的内存缓存实现"""

    def __init__(self, ttl_minutes: int = 15):
        """
        初始化缓存
        :param ttl_minutes: 缓存过期时间（分钟）
        """
        self._store: dict[str, tuple[Any, datetime]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def _generate_key(self, query: str, city: str, pickup_time: datetime, return_time: datetime) -> str:
        """生成缓存键"""
        key_data = {
            "query": query,
            "city": city,
            "pickup_time": pickup_time.isoformat(),
            "return_time": return_time.isoformat(),
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, query: str, city: str, pickup_time: datetime, return_time: datetime) -> Optional[Any]:
        """
        从缓存获取数据
        :return: 缓存的数据；不存在或已过期返回 None
        """
        key = self._generate_key(query, city, pickup_time, return_time)
        if key not in self._store:
            return None

        cached_data, cached_time = self._store[key]
        if datetime.now() - cached_time > self.ttl:
            del self._store[key]
            return None

        return cached_data

    def set(self, query: str, city: str, pickup_time: datetime, return_time: datetime, data: Any):
        """设置缓存数据"""
        key = self._generate_key(query, city, pickup_time, return_time)
        self._store[key] = (data, datetime.now())

    def clear(self):
        """清空所有缓存"""
        self._store.clear()


# 全局缓存实例
cache = Cache(ttl_minutes=15)
