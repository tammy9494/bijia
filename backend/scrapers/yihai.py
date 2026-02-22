"""
一嗨租车价格爬虫

数据来源：
- 车型列表：从一嗨租车 CityCarRental/CarPriceList 接口获取（无需登录）
- 价格数据：一嗨需要登录才能查看，当前使用基于市场均价的估算值
- 跳转链接：链接到一嗨真实预订页面，用户可查看实时价格

反爬处理点：
1. 随机 User-Agent 轮换
2. 随机延迟 1-3 秒
3. 无头浏览器模拟真实访问
4. 通过同一浏览器上下文保持 cookies
"""
import asyncio
import random
import logging
import re
import html as html_module
from datetime import datetime
from typing import List, Optional
from playwright.async_api import async_playwright, Browser
from backend.scrapers.base import BaseScraper
from backend.models import RentalPrice

logger = logging.getLogger(__name__)

# 一嗨租车 CityCarRental 页面的城市名 -> URL 映射
# 页面 URL 格式: https://www.1hai.cn/CityCarRental/index?City=城市名
# CarPriceList API: POST https://www.1hai.cn/CityCarRental/CarPriceList
YIHAI_BASE_URL = "https://www.1hai.cn"
YIHAI_CAR_LIST_API = f"{YIHAI_BASE_URL}/CityCarRental/CarPriceList"

# 基于市场调研的参考日租价（元/天）
# 由于一嗨需要登录才能看到真实价格，这里使用市场均价作为参考
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


def _estimate_daily_price(car_name: str) -> float:
    """
    根据车型名称估算日租价格

    匹配逻辑：遍历价格表，找到车型名称中包含的关键词
    """
    for key, price in _REFERENCE_PRICES.items():
        if key in car_name:
            # 添加 ±10% 的随机波动，模拟不同门店的价差
            return round(price * random.uniform(0.90, 1.10), 0)
    # 默认价格
    return round(random.uniform(148, 258), 0)


class YihaiScraper(BaseScraper):
    """一嗨租车爬虫"""

    # 反爬处理点 1：User-Agent 轮换
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]

    def __init__(self):
        super().__init__("一嗨租车")
        self._playwright = None
        self._browser: Optional[Browser] = None

    async def _random_delay(self, lo: float = 1.0, hi: float = 3.0):
        """反爬处理点 2：随机延迟"""
        await asyncio.sleep(random.uniform(lo, hi))

    async def _init_browser(self):
        """反爬处理点 3：使用无头浏览器"""
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )

    async def _close_browser(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    # ------------------------------------------------------------------
    # 核心：从一嗨获取真实车型列表
    # ------------------------------------------------------------------
    async def _fetch_car_list(
        self,
        city: str,
        pickup_time: str,
        return_time: str,
        brands: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        从一嗨租车获取某城市的真实车型列表

        :param brands: 要筛选的品牌列表。如果传入，会对每个品牌单独发请求，
                       绕过默认 30 条的数量限制。
        :return: 车型列表 [{"name": "...", "specs": "...", "image": "...", "booking_url": "..."}]
        """
        await self._init_browser()
        page = await self._browser.new_page()

        ua = random.choice(self.USER_AGENTS)
        await page.set_extra_http_headers({"User-Agent": ua})

        all_htmls: List[str] = []

        async def on_response(response):
            if "CarPriceList" in response.url:
                try:
                    body = await response.text()
                    all_htmls.append(body)
                except Exception:
                    pass

        page.on("response", on_response)

        try:
            city_url = f"{YIHAI_BASE_URL}/CityCarRental/index?City={city}"
            await page.goto(city_url, wait_until="networkidle", timeout=20000)
            await self._random_delay(1.0, 2.0)

            # 先获取默认列表（前 30 条）
            btn = await page.query_selector("#J_SumitBooking")
            if btn:
                await btn.click()
                await page.wait_for_timeout(4000)

            # 对指定品牌单独发请求，绕过默认 30 条限制
            # 直接用用户传入的时间，不依赖页面 DOM 默认值
            if brands:
                # 将 ISO 格式转为一嗨 API 需要的格式
                pt = pickup_time.replace("T", " ")[:16]  # "2026-02-25 08:00"
                rt = return_time.replace("T", " ")[:16]

                for brand_name in brands:
                    await self._random_delay(0.3, 0.8)
                    js = """() => {
                        return new Promise((resolve) => {
                            $.ajax({
                                type: 'POST',
                                url: '/CityCarRental/CarPriceList',
                                data: {
                                    CityName: '%s',
                                    PickupTime: '%s',
                                    ReturnTime: '%s',
                                    Category: '',
                                    SortBy: '',
                                    Brands: '%s'
                                },
                                dataType: 'html',
                                success: function(data) { resolve(data); },
                                error: function() { resolve(''); }
                            });
                        });
                    }""" % (city, pt, rt, brand_name)
                    result = await page.evaluate(js)
                    if result:
                        all_htmls.append(result)

            # 合并所有响应中的车型，去重
            all_cars = []
            seen = set()
            for html_content in all_htmls:
                for car in self._parse_car_list_html(html_content):
                    key = car["name"]
                    if key not in seen:
                        seen.add(key)
                        all_cars.append(car)

            return all_cars

        except Exception as e:
            logger.error("Failed to fetch car list: %s", e, exc_info=True)
            return []
        finally:
            await page.close()

    def _parse_car_list_html(self, html_content: str) -> List[dict]:
        """
        解析 CarPriceList 返回的 HTML，提取车型信息

        HTML 结构：
        <div class="det-carlist">
          <ul class="clearfix">
            <li class="carpic"><img src="..." alt="车型名" /></li>
            <li class="carname"><h4>车型名</h4><p><span>规格</span></p></li>
            <li class="carstore"><a href="预订链接">选门店</a></li>
          </ul>
        </div>
        """
        cars = []

        # 匹配每个车型块
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

        logger.info("Parsed %d cars from yihai HTML", len(cars))
        return cars

    def _parse_specs(self, specs: str) -> dict:
        """解析规格字符串，如 '自动 1.5L|三厢|5座'"""
        result = {"transmission": "", "engine": "", "body_type": "", "seats": 5}

        parts = specs.split("|")
        if len(parts) >= 1:
            # 第一段包含变速箱和排量
            first = parts[0].strip()
            if "自动" in first:
                result["transmission"] = "自动"
            elif "无级" in first:
                result["transmission"] = "无级变速"
            elif "双离合" in first:
                result["transmission"] = "双离合"
            # 判断是否纯电（0.0L 表示纯电动）
            if "0.0L" in first:
                result["engine"] = "纯电动"
            else:
                engine_match = re.search(r"[\d.]+[TL](?:-[\d.]+[TL])?", first)
                if engine_match:
                    result["engine"] = engine_match.group()

        if len(parts) >= 2:
            result["body_type"] = parts[1].strip()

        if len(parts) >= 3:
            seat_match = re.search(r"(\d+)座", parts[2])
            if seat_match:
                result["seats"] = int(seat_match.group(1))

        return result

    def _is_new_energy(self, car_name: str, specs: str) -> bool:
        """判断是否为新能源车型"""
        ne_keywords = [
            "特斯拉", "Model", "比亚迪", "蔚来", "小鹏", "理想",
            "极氪", "问界", "小米", "零跑", "哪吒", "smart精灵",
            "埃安", "AION", "深蓝", "智己", "岚图", "海狮", "海鸥",
            "海豚", "萤火虫", "firefly",
        ]
        # 0.0L 排量通常表示纯电
        if "0.0L" in specs:
            return True
        return any(kw in car_name for kw in ne_keywords)

    # ------------------------------------------------------------------
    # 对外接口
    # ------------------------------------------------------------------
    async def scrape(
        self,
        car_info: dict,
        city: str,
        pickup_time: str,
        return_time: str,
    ) -> List[RentalPrice]:
        """
        抓取一嗨租车的价格信息

        :param car_info: 车型信息字典（来自 nev_catalog）
        :param city: 城市名称
        :param pickup_time: 取车时间 ISO 格式
        :param return_time: 还车时间 ISO 格式
        """
        pickup_dt = datetime.fromisoformat(pickup_time)
        return_dt = datetime.fromisoformat(return_time)
        days = max((return_dt - pickup_dt).days, 1)

        # 从一嗨获取该城市的真实车型列表
        real_cars = await self._fetch_car_list(city, pickup_time, return_time)

        if not real_cars:
            logger.warning("No cars fetched from yihai, using fallback mock for %s", city)
            return self._fallback_mock(car_info, city, pickup_dt, return_dt, days)

        # 在真实车型列表中匹配用户搜索的车型
        target = car_info["model"].lower()
        brand = car_info["brand"].lower()
        series = car_info["series"].lower()

        matched_cars = []
        for car in real_cars:
            name_lower = car["name"].lower()
            # 尝试匹配：完整车型名、品牌+车系、品牌
            if (target in name_lower
                    or (brand in name_lower and series in name_lower)
                    or (brand in name_lower)):
                matched_cars.append(car)

        if not matched_cars:
            logger.info("No matching car found in yihai for '%s', using fallback", car_info["model"])
            return self._fallback_mock(car_info, city, pickup_dt, return_dt, days)

        # 为匹配到的车型生成价格数据
        results = []
        for car in matched_cars:
            daily_price = _estimate_daily_price(car["name"])
            total_price = daily_price * days
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
                    total_price=total_price,
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
        """当无法从一嗨获取数据时的兜底方案"""
        daily_price = _estimate_daily_price(f"{car_info['brand']}{car_info['series']}")
        total_price = daily_price * days

        # 生成一个指向一嗨搜索页的通用链接
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
                total_price=total_price,
                energy_type=car_info.get("energy", "纯电动"),
                seats=car_info.get("seats", 5),
                range_km=car_info.get("range_km"),
                pickup_time=pickup_dt,
                return_time=return_dt,
                scraped_at=datetime.now(),
            )
        ]

    async def _fetch_brand_catalog(self) -> List[dict]:
        """
        从一嗨 BrandStep1 页面获取全品牌车型目录

        CityCarRental 接口有 30 条硬限制，会漏掉部分车型。
        BrandStep1 页面列出了一嗨平台上的所有品牌和车型（无数量限制），
        作为补充数据源，确保不遗漏车型。

        返回格式与 _fetch_car_list 一致，但 booking_url 指向品牌浏览页。
        """
        await self._init_browser()
        page = await self._browser.new_page()
        ua = random.choice(self.USER_AGENTS)
        await page.set_extra_http_headers({"User-Agent": ua})

        try:
            await page.goto(
                "https://booking.1hai.cn/Order/BrandStep1",
                wait_until="networkidle", timeout=20000,
            )
            await self._random_delay(1.0, 2.0)

            # BrandStep1 页面结构：
            # <li>
            #   <div class="car-list">
            #     <div class="car-img"><img src="..."></div>
            #     <div class="car-desc">
            #       <div class="car-name">岚图梦想家沪牌</div>
            #       <div class="car-intro"></div>
            #     </div>
            #   </div>
            # </li>
            cars = await page.evaluate("""() => {
                const results = [];
                const nameEls = document.querySelectorAll('.car-name');
                for (const el of nameEls) {
                    const name = el.innerText.trim();
                    if (!name || name.length > 40) continue;
                    // 从父级 li 中获取图片
                    const li = el.closest('li');
                    const img = li ? li.querySelector('img') : null;
                    results.push({
                        name: name,
                        specs: '',
                        booking_url: '',
                        image_url: img ? img.src : '',
                    });
                }
                return results;
            }""")

            logger.info("Parsed %d cars from BrandStep1", len(cars))
            return cars

        except Exception as e:
            logger.error("Failed to fetch brand catalog: %s", e, exc_info=True)
            return []
        finally:
            await page.close()

    async def scrape_all_cars(
        self,
        city: str,
        pickup_time: str,
        return_time: str,
        brands: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        获取该城市一嗨所有可租车型（公开数据）

        :param brands: 要重点查询的品牌列表。会对每个品牌单独发请求，
                       绕过默认 30 条限制，确保不遗漏。

        合并两个数据源：
        1. CityCarRental（默认 30 条 + 按品牌定向筛选）
        2. BrandStep1（全品牌目录补充）
        """
        city_cars = await self._fetch_car_list(city, pickup_time, return_time, brands=brands)
        brand_cars = await self._fetch_brand_catalog()

        # 用车型名去重合并（CityCarRental 数据优先，因为链接带城市+日期参数）
        seen_names = set()
        merged = []
        for car in city_cars:
            key = car["name"].replace("京牌", "").replace("沪牌", "").strip().lower()
            seen_names.add(key)
            merged.append(car)

        for car in brand_cars:
            key = car["name"].replace("京牌", "").replace("沪牌", "").strip().lower()
            if key not in seen_names:
                seen_names.add(key)
                # 补充的车型没有城市+日期参数的预订链接，给一个通用链接
                if not car.get("booking_url"):
                    car["booking_url"] = f"{YIHAI_BASE_URL}/CityCarRental/index?City={city}"
                merged.append(car)

        logger.info(
            "Merged car list: %d (city=%d + brand_supplement=%d)",
            len(merged), len(city_cars), len(merged) - len(city_cars),
        )
        return merged

    # ------------------------------------------------------------------
    # 异步上下文管理器
    # ------------------------------------------------------------------
    async def __aenter__(self):
        await self._init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_browser()


# ------------------------------------------------------------------
# 便捷函数
# ------------------------------------------------------------------
async def scrape_yihai(
    car_info: dict,
    city: str,
    pickup_time: str,
    return_time: str,
) -> List[RentalPrice]:
    """抓取一嗨租车价格的便捷函数"""
    async with YihaiScraper() as scraper:
        return await scraper.scrape(car_info, city, pickup_time, return_time)
