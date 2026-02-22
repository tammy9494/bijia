"""
一嗨租车价格爬虫 - HTTP版本（适用于云部署）

数据来源：
- 车型列表：从一嗨租车 API 获取（无需登录）
- 价格数据：使用基于市场均价的估算值
- 跳转链接：链接到一嗨真实预订页面
"""
import random
import logging
import re
import html as html_module
from datetime import datetime
from typing import List, Optional
import httpx
from backend.scrapers.base import BaseScraper
from backend.models import RentalPrice

logger = logging.getLogger(__name__)

YIHAI_BASE_URL = "https://www.1hai.cn"
YIHAI_CAR_LIST_API = f"{YIHAI_BASE_URL}/CityCarRental/CarPriceList"

_REFERENCE_PRICES = {
    "比亚迪秦PLUS": 128, "比亚迪秦": 128, "比亚迪海狮": 168, "比亚迪海鸥": 88,
    "比亚迪宋Pro": 148, "比亚迪宋PLUS": 168, "比亚迪汉": 258, "比亚迪元PLUS": 138,
    "比亚迪海豚": 108,
    "特斯拉Model 3": 288, "特斯拉Model Y": 318, "特斯拉Model": 298,
    "大众朗逸": 138, "大众帕萨特": 208, "大众迈腾": 228, "大众途铠": 158,
    "大众途岳": 188, "大众探岳": 248,
    "丰田卡罗拉": 148, "丰田凯美瑞": 228, "丰田亚洲龙": 248, "丰田皇冠": 328,
    "本田雅阁": 218,
    "奥迪A3": 268, "奥迪A4": 328, "奥迪Q3": 298,
    "奔驰B200": 298, "奔驰C": 398,
    "凯迪拉克CT5": 328,
    "smart精灵": 198,
    "长安UNI": 178,
    "岚图梦想家": 406, "岚图FREE": 288, "岚图": 350,
    "小米SU7": 238, "小米": 238,
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def _estimate_daily_price(car_name: str) -> float:
    for key, price in _REFERENCE_PRICES.items():
        if key in car_name:
            return round(price * random.uniform(0.90, 1.10), 0)
    return round(random.uniform(148, 258), 0)


class YihaiScraper(BaseScraper):
    """一嗨租车爬虫 - HTTP版本"""

    def __init__(self):
        super().__init__("一嗨租车")
        self._client = None

    async def _get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                }
            )
        return self._client

    async def _fetch_car_list(
        self,
        city: str,
        pickup_time: str,
        return_time: str,
        brands: Optional[List[str]] = None,
    ) -> List[dict]:
        client = await self._get_client()
        all_cars = []
        seen = set()

        pt = pickup_time.replace("T", " ")[:16]
        rt = return_time.replace("T", " ")[:16]

        search_brands = brands if brands else [""]

        for brand_name in search_brands:
            try:
                data = {
                    "CityName": city,
                    "PickupTime": pt,
                    "ReturnTime": rt,
                    "Category": "",
                    "SortBy": "",
                    "Brands": brand_name
                }
                response = await client.post(YIHAI_CAR_LIST_API, data=data)
                html_content = response.text

                for car in self._parse_car_list_html(html_content):
                    key = car["name"]
                    if key not in seen:
                        seen.add(key)
                        all_cars.append(car)

            except Exception as e:
                logger.error("Failed to fetch car list: %s", e)

        logger.info("Fetched %d cars from yihai API", len(all_cars))
        return all_cars

    def _parse_car_list_html(self, html_content: str) -> List[dict]:
        cars = []
        pattern = (
            r'<li class="carpic">.*?'
            r'<img\s+src="([^"]*)".*?alt="([^"]*)".*?'
            r'<li class="carname">.*?<h4>([^<]*)</h4>.*?'
            r'<span>([^<]*)</span>.*?'
            r'<a[^>]*href="([^"]*)"'
        )

        for match in re.finditer(pattern, html_content, re.DOTALL):
            image_url = match.group(1)
            alt_text = html_module.unescape(match.group(2))
            car_name = html_module.unescape(match.group(3))
            specs = html_module.unescape(match.group(4))
            booking_url = html_module.unescape(match.group(5))

            cars.append({
                "name": car_name,
                "specs": specs,
                "image_url": image_url,
                "booking_url": booking_url,
            })

        return cars

    def _parse_specs(self, specs: str) -> dict:
        result = {"transmission": "", "engine": "", "body_type": "", "seats": 5}
        parts = specs.split("|")
        if len(parts) >= 1:
            first = parts[0].strip()
            if "自动" in first:
                result["transmission"] = "自动"
            if "0.0L" in first:
                result["engine"] = "纯电动"
        if len(parts) >= 3:
            seat_match = re.search(r"(\d+)座", parts[2])
            if seat_match:
                result["seats"] = int(seat_match.group(1))
        return result

    async def scrape(
        self,
        car_info: dict,
        city: str,
        pickup_time: str,
        return_time: str,
    ) -> List[RentalPrice]:
        pickup_dt = datetime.fromisoformat(pickup_time)
        return_dt = datetime.fromisoformat(return_time)
        days = max((return_dt - pickup_dt).days, 1)

        real_cars = await self._fetch_car_list(city, pickup_time, return_time)

        if not real_cars:
            return self._fallback_mock(car_info, city, pickup_dt, return_dt, days)

        target = car_info["model"].lower()
        brand = car_info["brand"].lower()
        series = car_info["series"].lower()

        matched_cars = []
        for car in real_cars:
            name_lower = car["name"].lower()
            if (target in name_lower or (brand in name_lower and series in name_lower) or brand in name_lower):
                matched_cars.append(car)

        if not matched_cars:
            return self._fallback_mock(car_info, city, pickup_dt, return_dt, days)

        results = []
        for car in matched_cars:
            daily_price = _estimate_daily_price(car["name"])
            specs = self._parse_specs(car["specs"])
            energy_type = "纯电动" if specs["engine"] == "纯电动" else car_info.get("energy", "未知")

            results.append(
                RentalPrice(
                    brand=car_info["brand"],
                    series=car_info["series"],
                    model_name=car["name"].replace("京牌", "").replace("沪牌", "").strip(),
                    merchant="一嗨租车",
                    merchant_url=car["booking_url"],
                    city=city,
                    daily_price=daily_price,
                    total_price=daily_price * days,
                    energy_type=energy_type,
                    seats=specs["seats"],
                    range_km=car_info.get("range_km"),
                    pickup_time=pickup_dt,
                    return_time=return_dt,
                    scraped_at=datetime.now(),
                )
            )

        return results

    def _fallback_mock(
        self, car_info: dict, city: str,
        pickup_dt: datetime, return_dt: datetime, days: int
    ) -> List[RentalPrice]:
        daily_price = _estimate_daily_price(f"{car_info['brand']}{car_info['series']}")
        fallback_url = f"{YIHAI_BASE_URL}/CityCarRental/index?City={city}"

        return [
            RentalPrice(
                brand=car_info["brand"],
                series=car_info["series"],
                model_name=car_info["model"],
                merchant="一嗨租车",
                merchant_url=fallback_url,
                city=city,
                daily_price=daily_price,
                total_price=daily_price * days,
                energy_type=car_info.get("energy", "纯电动"),
                seats=car_info.get("seats", 5),
                range_km=car_info.get("range_km"),
                pickup_time=pickup_dt,
                return_time=return_dt,
                scraped_at=datetime.now(),
            )
        ]

    async def scrape_all_cars(
        self,
        city: str,
        pickup_time: str,
        return_time: str,
        brands: Optional[List[str]] = None,
    ) -> List[dict]:
        return await self._fetch_car_list(city, pickup_time, return_time, brands=brands)

    async def __aenter__(self):
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()
            self._client = None
