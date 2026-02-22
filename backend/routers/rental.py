"""
租赁价格查询路由
"""
import re
import logging
from datetime import datetime
from urllib.parse import urlencode, quote
from fastapi import APIRouter, HTTPException
from backend.models import RentalRequest, RentalResponse, RentalPrice, PlatformLink
from backend.nev_catalog import search_cars, get_all_brands, match_platform_car
from backend.scrapers.yihai import YihaiScraper, _estimate_daily_price
from backend.cache import cache

logger = logging.getLogger(__name__)
router = APIRouter()

# 城市ID映射表
_CITY_IDS = {
    "北京": {"shenzhou": "1", "wkzuche": "110100", "ctrip": "1"},
    "上海": {"shenzhou": "31", "wkzuche": "310100", "ctrip": "2"},
    "广州": {"shenzhou": "3", "wkzuche": "440100", "ctrip": "32"},
    "深圳": {"shenzhou": "4", "wkzuche": "440300", "ctrip": "33"},
    "杭州": {"shenzhou": "5", "wkzuche": "330100", "ctrip": "14"},
    "成都": {"shenzhou": "6", "wkzuche": "510100", "ctrip": "28"},
    "南京": {"shenzhou": "7", "wkzuche": "320100", "ctrip": "17"},
    "武汉": {"shenzhou": "8", "wkzuche": "420100", "ctrip": "19"},
    "西安": {"shenzhou": "9", "wkzuche": "610100", "ctrip": "27"},
    "重庆": {"shenzhou": "10", "wkzuche": "500100", "ctrip": "4"},
    "天津": {"shenzhou": "11", "wkzuche": "120100", "ctrip": "3"},
    "苏州": {"shenzhou": "12", "wkzuche": "320500", "ctrip": "18"},
    "厦门": {"shenzhou": "13", "wkzuche": "350200", "ctrip": "24"},
    "青岛": {"shenzhou": "14", "wkzuche": "370200", "ctrip": "10"},
    "长沙": {"shenzhou": "15", "wkzuche": "430100", "ctrip": "21"},
    "郑州": {"shenzhou": "16", "wkzuche": "410100", "ctrip": "20"},
    "济南": {"shenzhou": "17", "wkzuche": "370100", "ctrip": "9"},
    "福州": {"shenzhou": "18", "wkzuche": "350100", "ctrip": "23"},
    "合肥": {"shenzhou": "19", "wkzuche": "340100", "ctrip": "22"},
    "昆明": {"shenzhou": "20", "wkzuche": "530100", "ctrip": "30"},
}


def _format_time_for_url(dt: datetime) -> str:
    """将时间格式化为一嗨网站需要的格式：YYYY-MM-DD HH:MM"""
    return dt.strftime("%Y-%m-%d %H:%M")


def _add_time_params_to_url(url: str, pickup_dt: datetime, return_dt: datetime) -> str:
    """在 URL 中添加取还车时间参数（URL编码）"""
    pickup_str = _format_time_for_url(pickup_dt)
    return_str = _format_time_for_url(return_dt)
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}PickupTime={quote(pickup_str)}&ReturnTime={quote(return_str)}"


_CITY_IDS = {
    "北京": {"shenzhou": "1", "wkzuche": "110100", "ctrip": "1"},
    "上海": {"shenzhou": "31", "wkzuche": "310100", "ctrip": "2"},
    "广州": {"shenzhou": "3", "wkzuche": "440100", "ctrip": "32"},
    "深圳": {"shenzhou": "4", "wkzuche": "440300", "ctrip": "33"},
    "杭州": {"shenzhou": "5", "wkzuche": "330100", "ctrip": "14"},
    "成都": {"shenzhou": "6", "wkzuche": "510100", "ctrip": "28"},
    "南京": {"shenzhou": "7", "wkzuche": "320100", "ctrip": "17"},
    "武汉": {"shenzhou": "8", "wkzuche": "420100", "ctrip": "19"},
    "西安": {"shenzhou": "9", "wkzuche": "610100", "ctrip": "27"},
    "重庆": {"shenzhou": "10", "wkzuche": "500100", "ctrip": "4"},
    "天津": {"shenzhou": "11", "wkzuche": "120100", "ctrip": "3"},
    "苏州": {"shenzhou": "12", "wkzuche": "320500", "ctrip": "18"},
    "厦门": {"shenzhou": "13", "wkzuche": "350200", "ctrip": "24"},
    "青岛": {"shenzhou": "14", "wkzuche": "370200", "ctrip": "10"},
    "长沙": {"shenzhou": "15", "wkzuche": "430100", "ctrip": "21"},
    "郑州": {"shenzhou": "16", "wkzuche": "410100", "ctrip": "20"},
    "济南": {"shenzhou": "17", "wkzuche": "370100", "ctrip": "9"},
    "福州": {"shenzhou": "18", "wkzuche": "350100", "ctrip": "23"},
    "合肥": {"shenzhou": "19", "wkzuche": "340100", "ctrip": "22"},
    "昆明": {"shenzhou": "20", "wkzuche": "530100", "ctrip": "30"},
}


def _generate_platform_links(brand: str, city: str, pickup_dt: datetime, return_dt: datetime) -> list[PlatformLink]:
    """生成其他平台的搜索链接（带搜索参数）"""
    links = []
    
    city_ids = _CITY_IDS.get(city, _CITY_IDS["上海"])
    pickup_str = pickup_dt.strftime("%Y-%m-%d%%20%H:%M")
    return_str = return_dt.strftime("%Y-%m-%d%%20%H:%M")
    
    # 神州租车 - 直接跳转到首页，用户手动选择
    links.append(PlatformLink(
        name="神州租车", 
        url="https://m.zuche.com/",
        available=True
    ))
    
    # 悟空租车 - 直接跳转到首页，用户手动选择
    links.append(PlatformLink(
        name="悟空租车", 
        url="https://m.wkzuche.com/",
        available=True
    ))
    
    # 携程租车 - 直接跳转到租车首页
    links.append(PlatformLink(
        name="携程租车", 
        url="https://m.ctrip.com/xtaro/car/home",
        available=True
    ))
    
    return links


@router.post("/rental/search", response_model=RentalResponse)
async def search_rental_prices(request: RentalRequest):
    """
    搜索租赁价格

    核心流程：
    1. 在新能源车型标准库中匹配用户输入
    2. 一次性从一嗨获取该城市所有可租车型
    3. 用多维度打分引擎将平台车型精准匹配到标准库
    4. 生成结果
    """
    try:
        # 检查缓存
        cached_data = cache.get(
            request.query, request.city,
            request.pickup_time, request.return_time,
        )
        if cached_data is not None:
            search_type, data = cached_data
            return RentalResponse(
                success=True, search_type=search_type,
                data=data, message="数据来自缓存",
            )

        # 第 1 步：在标准库中搜索用户输入
        search_type, matched_nev = search_cars(request.query)
        if not matched_nev:
            return RentalResponse(
                success=False, search_type=search_type, data=[],
                message=f"未找到与「{request.query}」相关的新能源车型",
            )

        pickup_time = request.pickup_time.isoformat()
        return_time = request.return_time.isoformat()
        pickup_dt = request.pickup_time
        return_dt = request.return_time
        days = max((return_dt - pickup_dt).days, 1)

        # 第 2 步：从一嗨获取该城市可租车型
        # 提取用户搜索涉及的品牌列表，传给爬虫做定向筛选，绕过 30 条限制
        target_brands = list(set(c["brand"] for c in matched_nev))
        real_cars = []
        try:
            async with YihaiScraper() as scraper:
                real_cars = await scraper.scrape_all_cars(
                    request.city, pickup_time, return_time,
                    brands=target_brands,
                )
            logger.info("Fetched %d real cars from yihai for %s (brands=%s)",
                        len(real_cars), request.city, target_brands)
        except Exception as e:
            logger.error("Failed to fetch yihai car list: %s", e)

        # 第 3 步：用匹配引擎交叉匹配
        # 收集用户搜索到的标准车型 ID 集合
        target_ids = {c["id"] for c in matched_nev}
        all_prices: list[RentalPrice] = []
        matched_nev_ids = set()  # 记录哪些标准车型已有真实匹配

        for rc in real_cars:
            # 用打分引擎将平台车型匹配到标准库
            std_car = match_platform_car(
                rc.get("name", ""),
                rc.get("specs", ""),
                candidates=matched_nev,  # 只在用户搜索结果范围内匹配
            )
            if std_car is None:
                continue

            matched_nev_ids.add(std_car["id"])
            specs = _parse_specs(rc.get("specs", ""))
            energy = "纯电动" if specs.get("engine") == "纯电动" else std_car.get("energy", "纯电动")

            # 检查是否有有效的预订链接（brandStep2 表示有具体车型预订页）
            booking_url = rc.get("booking_url", "")
            has_valid_url = "brandStep2" in booking_url

            # 在 URL 中添加取还车时间参数
            booking_url = _add_time_params_to_url(booking_url, pickup_dt, return_dt)

            # 一嗨有此车型，但真实价格需要登录才能看到
            # 不显示估算价格，引导用户跳转查看实时价格
            # 生成其他平台链接
            other_links = _generate_platform_links(std_car["brand"], request.city, pickup_dt, return_dt)
            
            all_prices.append(RentalPrice(
                brand=std_car["brand"],
                series=std_car["series"],
                model_name=_clean_name(rc["name"]),
                merchant="一嗨租车",
                merchant_url=booking_url,
                city=request.city,
                daily_price=None,
                total_price=None,
                available=has_valid_url,
                energy_type=energy,
                seats=specs.get("seats") or std_car.get("seats", 5),
                range_km=std_car.get("range_km"),
                pickup_time=pickup_dt,
                return_time=return_dt,
                scraped_at=datetime.now(),
                other_platforms=other_links,
            ))

        # 第 4 步：一嗨没有的车型标记为「暂无此车」，不编造价格
        fallback_url = _add_time_params_to_url(
            f"https://www.1hai.cn/CityCarRental/index?City={request.city}",
            pickup_dt, return_dt
        )
        for nev in matched_nev:
            if nev["id"] not in matched_nev_ids:
                all_prices.append(RentalPrice(
                    brand=nev["brand"],
                    series=nev["series"],
                    model_name=nev["model"],
                    merchant="一嗨租车",
                    merchant_url=fallback_url,
                    city=request.city,
                    daily_price=None,
                    total_price=None,
                    available=False,
                    energy_type=nev.get("energy", "纯电动"),
                    seats=nev.get("seats", 5),
                    range_km=nev.get("range_km"),
                    pickup_time=pickup_dt,
                    return_time=return_dt,
                    scraped_at=datetime.now(),
                ))

        # 去重
        seen = set()
        deduped: list[RentalPrice] = []
        for p in all_prices:
            key = (p.model_name, p.merchant, p.merchant_url)
            if key not in seen:
                seen.add(key)
                deduped.append(p)
        all_prices = deduped

        if not all_prices:
            return RentalResponse(
                success=False, search_type=search_type, data=[],
                message="未找到相关价格信息",
            )

        # 存入缓存
        cache.set(
            request.query, request.city,
            request.pickup_time, request.return_time,
            (search_type, all_prices),
        )

        real_count = len(matched_nev_ids)
        total = len(all_prices)
        if search_type == "exact":
            msg = f"精确匹配：找到 {total} 条报价（{real_count} 条来自一嗨实时数据）"
        else:
            msg = f"模糊搜索：找到 {total} 条报价（{real_count} 条来自一嗨实时数据）"

        return RentalResponse(
            success=True, search_type=search_type,
            data=all_prices, message=msg,
        )

    except Exception as e:
        logger.error("Search failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


def _parse_specs(specs: str) -> dict:
    """解析规格字符串，如 '自动 1.5L|三厢|5座'"""
    result = {"transmission": "", "engine": "", "body_type": "", "seats": None}
    parts = specs.split("|")
    if parts:
        first = parts[0].strip()
        if "0.0L" in first:
            result["engine"] = "纯电动"
    if len(parts) >= 3:
        m = re.search(r"(\d+)座", parts[2])
        if m:
            result["seats"] = int(m.group(1))
    return result


def _clean_name(name: str) -> str:
    """清理平台车型名中的地域牌照后缀"""
    for suffix in ["京牌", "沪牌", "粤牌", "浙牌", "苏牌", "川牌", "渝牌", "鄂牌"]:
        name = name.replace(suffix, "")
    return name.strip()


@router.get("/brands")
async def list_brands():
    """获取所有新能源品牌列表"""
    return {"brands": get_all_brands()}
