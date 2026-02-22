"""
数据模型定义
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PlatformLink(BaseModel):
    """平台链接模型"""
    name: str                # 平台名称，如 "神州租车"
    url: str                 # 搜索链接
    available: bool = True   # 是否有车（默认未知）


class RentalPrice(BaseModel):
    """租赁价格数据模型"""
    # 允许 model_ 开头的字段名（Pydantic v2 默认会警告）
    model_config = ConfigDict(protected_namespaces=())
    # 车辆信息
    brand: str               # 品牌，如 "比亚迪"
    series: str              # 车系，如 "秦PLUS"
    model_name: str          # 车型，如 "秦PLUS EV 冠军版"
    # 租赁信息
    merchant: str            # 租赁商户名称，如 "一嗨租车"
    merchant_url: str        # 商户该车型的页面链接，支持点击跳转
    city: str                # 城市名称
    daily_price: Optional[float] = None   # 日租金（元/天），None 表示该平台暂无此车
    total_price: Optional[float] = None   # 总价（元）
    available: bool = True                 # 该平台是否有此车源
    # 车辆详情
    energy_type: str         # 能源类型，如 "纯电动" "插电混动"
    seats: int = 5           # 座位数
    range_km: Optional[int] = None   # 续航里程（公里），纯电车型
    # 时间信息
    pickup_time: datetime    # 取车时间
    return_time: datetime    # 还车时间
    scraped_at: datetime     # 抓取时间
    # 其他平台链接
    other_platforms: list[PlatformLink] = []  # 其他平台的搜索链接


class RentalRequest(BaseModel):
    """租赁查询请求模型"""
    query: str               # 搜索关键词（品牌/车系/车型，支持精确和模糊）
    city: str                # 城市名称
    pickup_time: datetime    # 取车时间
    return_time: datetime    # 还车时间


class RentalResponse(BaseModel):
    """租赁查询响应模型"""
    success: bool
    search_type: str         # "exact" 精确搜索 | "fuzzy" 模糊搜索
    data: list[RentalPrice]  # 多个平台的价格数据
    message: Optional[str] = None
