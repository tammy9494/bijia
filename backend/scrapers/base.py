"""
爬虫基类，定义统一的接口
"""
from abc import ABC, abstractmethod
from typing import List
from backend.models import RentalPrice


class BaseScraper(ABC):
    """爬虫基类，所有平台的爬虫都应继承此类"""
    
    def __init__(self, platform_name: str):
        """
        初始化爬虫
        :param platform_name: 平台名称
        """
        self.platform_name = platform_name
    
    @abstractmethod
    async def scrape(
        self,
        car_model: str,
        city: str,
        pickup_time: str,
        return_time: str
    ) -> List[RentalPrice]:
        """
        抓取租赁价格信息
        :param car_model: 车型名称
        :param city: 城市名称
        :param pickup_time: 取车时间（ISO 格式字符串）
        :param return_time: 还车时间（ISO 格式字符串）
        :return: 价格信息列表
        """
        pass
