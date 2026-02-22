"""
新能源车型标准数据库

每个车型拥有唯一 ID 和别名列表，用于跨平台精准匹配。

匹配原理：
  平台原文 "比亚迪秦PLUS京牌 自动 0.0L"
      ↓ 提取关键词
  ["比亚迪", "秦PLUS", "0.0L"]
      ↓ 与标准库别名/品牌/车系逐一比对，累计得分
  命中 byd_qinplus_ev (得分 85) > byd_qinplus_dmi (得分 45)
      ↓
  返回最佳匹配
"""
from typing import List, Optional, Tuple


# =====================================================================
# 车型标准库
#
# 每条记录的 aliases 字段包含该车型在各平台可能出现的名称变体。
# 匹配引擎会用这些别名来识别平台上的车辆。
# =====================================================================
NEV_CATALOG: List[dict] = [
    # ---- 比亚迪 ----
    {
        "id": "byd_qinplus_ev", "brand": "比亚迪", "series": "秦PLUS",
        "model": "秦PLUS EV 冠军版", "energy": "纯电动", "seats": 5, "range_km": 510,
        "aliases": ["秦PLUS EV", "秦PLUS纯电", "秦PLUS电动", "比亚迪秦PLUS EV", "BYD秦PLUS EV"],
        # 纯电标识：平台规格中出现 "0.0L" 时，优先匹配此条而非 DM-i
        "energy_hints": ["0.0L", "纯电", "EV"],
    },
    {
        "id": "byd_qinplus_dmi", "brand": "比亚迪", "series": "秦PLUS",
        "model": "秦PLUS DM-i 冠军版", "energy": "插电混动", "seats": 5, "range_km": 120,
        "aliases": ["秦PLUS DM-i", "秦PLUS混动", "秦PLUS插混", "比亚迪秦PLUS DM", "BYD秦PLUS DM-i"],
        "energy_hints": ["1.5L", "DM-i", "混动", "HEV"],
    },
    {
        "id": "byd_han_ev", "brand": "比亚迪", "series": "汉",
        "model": "汉EV 冠军版", "energy": "纯电动", "seats": 5, "range_km": 610,
        "aliases": ["汉EV", "比亚迪汉EV", "比亚迪汉纯电", "BYD汉EV"],
        "energy_hints": ["0.0L", "纯电", "EV"],
    },
    {
        "id": "byd_han_dmi", "brand": "比亚迪", "series": "汉",
        "model": "汉DM-i 冠军版", "energy": "插电混动", "seats": 5, "range_km": 200,
        "aliases": ["汉DM-i", "比亚迪汉DM", "比亚迪汉混动"],
        "energy_hints": ["DM-i", "混动"],
    },
    {
        "id": "byd_dolphin", "brand": "比亚迪", "series": "海豚",
        "model": "海豚 时尚版", "energy": "纯电动", "seats": 5, "range_km": 420,
        "aliases": ["海豚", "比亚迪海豚", "BYD海豚", "Dolphin"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "byd_seagull", "brand": "比亚迪", "series": "海鸥",
        "model": "海鸥 灵动版", "energy": "纯电动", "seats": 5, "range_km": 305,
        "aliases": ["海鸥", "比亚迪海鸥", "BYD海鸥", "Seagull"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "byd_sealion06", "brand": "比亚迪", "series": "海狮06",
        "model": "海狮06 EV", "energy": "纯电动", "seats": 5, "range_km": 502,
        "aliases": ["海狮06", "比亚迪海狮", "海狮", "BYD海狮06"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "byd_songplus_ev", "brand": "比亚迪", "series": "宋PLUS",
        "model": "宋PLUS EV 冠军版", "energy": "纯电动", "seats": 5, "range_km": 520,
        "aliases": ["宋PLUS EV", "宋PLUS纯电", "比亚迪宋PLUS EV"],
        "energy_hints": ["0.0L", "纯电", "EV"],
    },
    {
        "id": "byd_songplus_dmi", "brand": "比亚迪", "series": "宋PLUS",
        "model": "宋PLUS DM-i 冠军版", "energy": "插电混动", "seats": 5, "range_km": 110,
        "aliases": ["宋PLUS DM-i", "宋PLUS混动", "比亚迪宋PLUS DM"],
        "energy_hints": ["1.5L", "DM-i", "混动"],
    },
    {
        "id": "byd_songpro", "brand": "比亚迪", "series": "宋Pro",
        "model": "宋Pro DM-i 冠军版", "energy": "插电混动", "seats": 5, "range_km": 110,
        "aliases": ["宋Pro", "宋PRO", "比亚迪宋Pro", "比亚迪宋PRO"],
        "energy_hints": ["1.5L", "DM-i"],
    },
    {
        "id": "byd_yuanplus", "brand": "比亚迪", "series": "元PLUS",
        "model": "元PLUS 510km 旗舰版", "energy": "纯电动", "seats": 5, "range_km": 510,
        "aliases": ["元PLUS", "元Plus", "比亚迪元PLUS", "Atto 3"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 特斯拉 ----
    {
        "id": "tesla_model3", "brand": "特斯拉", "series": "Model 3",
        "model": "Model 3 焕新版", "energy": "纯电动", "seats": 5, "range_km": 606,
        "aliases": ["Model 3", "Model3", "特斯拉3", "Tesla Model 3", "特斯拉Model 3", "model3"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "tesla_modely", "brand": "特斯拉", "series": "Model Y",
        "model": "Model Y 标准版", "energy": "纯电动", "seats": 5, "range_km": 554,
        "aliases": ["Model Y", "ModelY", "特斯拉Y", "Tesla Model Y", "特斯拉Model Y", "modely"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 蔚来 ----
    {
        "id": "nio_et5", "brand": "蔚来", "series": "ET5",
        "model": "ET5 75kWh", "energy": "纯电动", "seats": 5, "range_km": 560,
        "aliases": ["ET5", "蔚来ET5", "NIO ET5"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "nio_es6", "brand": "蔚来", "series": "ES6",
        "model": "ES6 75kWh", "energy": "纯电动", "seats": 5, "range_km": 490,
        "aliases": ["ES6", "蔚来ES6", "NIO ES6"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "nio_et7", "brand": "蔚来", "series": "ET7",
        "model": "ET7 100kWh", "energy": "纯电动", "seats": 5, "range_km": 700,
        "aliases": ["ET7", "蔚来ET7", "NIO ET7"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 小鹏 ----
    {
        "id": "xpeng_p7", "brand": "小鹏", "series": "P7",
        "model": "P7i 702 Max", "energy": "纯电动", "seats": 5, "range_km": 702,
        "aliases": ["P7", "P7i", "小鹏P7", "XPeng P7"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "xpeng_g6", "brand": "小鹏", "series": "G6",
        "model": "G6 755 Max", "energy": "纯电动", "seats": 5, "range_km": 755,
        "aliases": ["G6", "小鹏G6", "XPeng G6"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "xpeng_mona", "brand": "小鹏", "series": "MONA M03",
        "model": "MONA M03 620 Max", "energy": "纯电动", "seats": 5, "range_km": 620,
        "aliases": ["MONA M03", "M03", "小鹏MONA"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 理想 ----
    {
        "id": "li_l7", "brand": "理想", "series": "L7",
        "model": "理想L7 Pro", "energy": "增程式", "seats": 5, "range_km": 210,
        "aliases": ["L7", "理想L7", "Li L7"],
        "energy_hints": ["增程"],
    },
    {
        "id": "li_l8", "brand": "理想", "series": "L8",
        "model": "理想L8 Pro", "energy": "增程式", "seats": 6, "range_km": 210,
        "aliases": ["L8", "理想L8", "Li L8"],
        "energy_hints": ["增程"],
    },
    {
        "id": "li_l9", "brand": "理想", "series": "L9",
        "model": "理想L9 Max", "energy": "增程式", "seats": 6, "range_km": 215,
        "aliases": ["L9", "理想L9", "Li L9"],
        "energy_hints": ["增程"],
    },
    {
        "id": "li_mega", "brand": "理想", "series": "MEGA",
        "model": "理想MEGA", "energy": "纯电动", "seats": 7, "range_km": 710,
        "aliases": ["MEGA", "理想MEGA", "Li MEGA"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 极氪 ----
    {
        "id": "zeekr_001", "brand": "极氪", "series": "001",
        "model": "极氪001 100kWh WE版", "energy": "纯电动", "seats": 5, "range_km": 656,
        "aliases": ["极氪001", "001", "Zeekr 001"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "zeekr_007", "brand": "极氪", "series": "007",
        "model": "极氪007 后驱版", "energy": "纯电动", "seats": 5, "range_km": 688,
        "aliases": ["极氪007", "007", "Zeekr 007"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "zeekr_x", "brand": "极氪", "series": "X",
        "model": "极氪X 后驱超长续航", "energy": "纯电动", "seats": 5, "range_km": 560,
        "aliases": ["极氪X", "Zeekr X"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 问界 ----
    {
        "id": "aito_m5", "brand": "问界", "series": "M5",
        "model": "问界M5 增程版", "energy": "增程式", "seats": 5, "range_km": 200,
        "aliases": ["问界M5", "M5", "AITO M5", "华为问界M5"],
        "energy_hints": ["增程"],
    },
    {
        "id": "aito_m7", "brand": "问界", "series": "M7",
        "model": "问界M7 增程版 Plus", "energy": "增程式", "seats": 6, "range_km": 240,
        "aliases": ["问界M7", "M7", "AITO M7", "华为问界M7"],
        "energy_hints": ["增程"],
    },
    {
        "id": "aito_m9", "brand": "问界", "series": "M9",
        "model": "问界M9 增程版 Max", "energy": "增程式", "seats": 6, "range_km": 275,
        "aliases": ["问界M9", "M9", "AITO M9", "华为问界M9"],
        "energy_hints": ["增程"],
    },

    # ---- 小米 ----
    {
        "id": "xiaomi_su7", "brand": "小米", "series": "SU7",
        "model": "小米SU7 标准版", "energy": "纯电动", "seats": 5, "range_km": 700,
        "aliases": ["小米SU7", "SU7", "Xiaomi SU7", "小米汽车SU7"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 零跑 ----
    {
        "id": "leapmotor_c11", "brand": "零跑", "series": "C11",
        "model": "零跑C11 纯电版", "energy": "纯电动", "seats": 5, "range_km": 530,
        "aliases": ["零跑C11", "C11", "Leapmotor C11"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 哪吒 ----
    {
        "id": "neta_x", "brand": "哪吒", "series": "X",
        "model": "哪吒X 400 Lite", "energy": "纯电动", "seats": 5, "range_km": 401,
        "aliases": ["哪吒X", "Neta X"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 萤火虫 ----
    {
        "id": "firefly_glow", "brand": "firefly", "series": "萤火虫",
        "model": "萤火虫发光版", "energy": "纯电动", "seats": 5, "range_km": 318,
        "aliases": ["萤火虫发光版", "萤火虫 发光版", "firefly发光版", "Firefly Glow"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "firefly_shine", "brand": "firefly", "series": "萤火虫",
        "model": "萤火虫闪耀版", "energy": "纯电动", "seats": 5, "range_km": 318,
        "aliases": ["萤火虫闪耀版", "萤火虫 闪耀版", "firefly闪耀版", "Firefly Shine"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 埃安 ----
    {
        "id": "aion_s", "brand": "埃安", "series": "AION S",
        "model": "AION S Plus 70 乐享版", "energy": "纯电动", "seats": 5, "range_km": 510,
        "aliases": ["AION S", "埃安S", "广汽埃安S", "Aion S Plus", "AIONS"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "aion_y", "brand": "埃安", "series": "AION Y",
        "model": "AION Y Plus 510 领先版", "energy": "纯电动", "seats": 5, "range_km": 510,
        "aliases": ["AION Y", "埃安Y", "广汽埃安Y", "Aion Y Plus", "AIONY"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 深蓝 ----
    {
        "id": "deepal_sl03", "brand": "深蓝", "series": "SL03",
        "model": "深蓝SL03 增程版", "energy": "增程式", "seats": 5, "range_km": 200,
        "aliases": ["深蓝SL03", "SL03", "长安深蓝SL03"],
        "energy_hints": ["增程"],
    },
    {
        "id": "deepal_s7", "brand": "深蓝", "series": "S7",
        "model": "深蓝S7 纯电版", "energy": "纯电动", "seats": 5, "range_km": 620,
        "aliases": ["深蓝S7", "S7", "长安深蓝S7"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 智己 ----
    {
        "id": "zhiji_l6", "brand": "智己", "series": "L6",
        "model": "智己L6 Max", "energy": "纯电动", "seats": 5, "range_km": 780,
        "aliases": ["智己L6", "L6", "IM L6"],
        "energy_hints": ["0.0L", "纯电"],
    },
    {
        "id": "zhiji_ls6", "brand": "智己", "series": "LS6",
        "model": "智己LS6 长续航版", "energy": "纯电动", "seats": 5, "range_km": 760,
        "aliases": ["智己LS6", "LS6", "IM LS6"],
        "energy_hints": ["0.0L", "纯电"],
    },

    # ---- 岚图 ----
    {
        "id": "voyah_free", "brand": "岚图", "series": "FREE",
        "model": "岚图FREE 增程版", "energy": "增程式", "seats": 5, "range_km": 210,
        "aliases": ["岚图FREE", "岚图FREE+", "FREE+", "FREE", "Voyah Free", "Voyah FREE+"],
        "energy_hints": ["增程"],
    },
    {
        "id": "voyah_dreamer", "brand": "岚图", "series": "梦想家",
        "model": "岚图梦想家 增程版", "energy": "增程式", "seats": 7, "range_km": 236,
        "aliases": ["岚图梦想家", "梦想家", "Voyah Dreamer"],
        "energy_hints": ["增程"],
    },

    # ---- smart ----
    {
        "id": "smart_3", "brand": "smart", "series": "精灵#3",
        "model": "smart精灵#3", "energy": "纯电动", "seats": 5, "range_km": 520,
        "aliases": ["smart精灵#3", "精灵#3", "smart #3", "smart精灵3", "精灵3"],
        "energy_hints": ["0.0L", "纯电"],
    },
]


# =====================================================================
# 用户搜索（搜索框 → 标准库）
# =====================================================================
def search_cars(query: str) -> Tuple[str, List[dict]]:
    """
    搜索新能源车型（用户输入 → 标准库匹配）

    搜索优先级：
    1. 精确匹配车型全称 / 别名
    2. 匹配品牌名
    3. 匹配车系名
    4. 模糊包含匹配
    """
    q = query.strip().lower()
    if not q:
        return "fuzzy", []

    # 第 1 步：精确匹配车型全称或别名
    for car in NEV_CATALOG:
        if q == car["model"].lower():
            return "exact", [car]
        for alias in car.get("aliases", []):
            if q == alias.lower():
                return "exact", [car]

    # 第 2 步：精确匹配品牌
    brand_matches = [c for c in NEV_CATALOG if q == c["brand"].lower()]
    if brand_matches:
        return "fuzzy", brand_matches

    # 第 3 步：精确匹配车系
    series_matches = [c for c in NEV_CATALOG if q == c["series"].lower()]
    if series_matches:
        return "fuzzy", series_matches

    # 第 4 步：模糊包含（品牌、车系、车型名、别名）
    fuzzy = []
    for car in NEV_CATALOG:
        if (q in car["brand"].lower()
                or q in car["series"].lower()
                or q in car["model"].lower()
                or any(q in a.lower() for a in car.get("aliases", []))):
            fuzzy.append(car)
    if fuzzy:
        return "fuzzy", fuzzy

    return "fuzzy", []


# =====================================================================
# 跨平台匹配引擎（平台车型名 → 标准库）
# =====================================================================
def match_platform_car(
    platform_name: str,
    platform_specs: str = "",
    candidates: Optional[List[dict]] = None,
) -> Optional[dict]:
    """
    将平台上的一条车型信息匹配到标准库中的最佳车型

    采用多维度打分机制：
      - 品牌匹配：+40 分
      - 车系匹配：+30 分
      - 别名命中：+20 分
      - 能源类型匹配：+10 分（通过 energy_hints 与 specs 交叉）

    :param platform_name: 平台显示的车型名，如 "比亚迪秦PLUS京牌"
    :param platform_specs: 平台显示的规格，如 "自动 0.0L|三厢|5座"
    :param candidates: 候选范围（可选），不传则搜索全库
    :return: 最佳匹配的标准库条目，或 None
    """
    catalog = candidates if candidates is not None else NEV_CATALOG
    name_lower = platform_name.lower()
    specs_lower = platform_specs.lower()
    combined = f"{name_lower} {specs_lower}"

    best_car = None
    best_score = 0

    for car in catalog:
        score = 0

        # --- 品牌匹配（40 分）---
        brand = car["brand"].lower()
        if brand in name_lower:
            score += 40

        # --- 车系匹配（30 分）---
        series = car["series"].lower()
        if series in name_lower:
            score += 30

        # --- 别名命中（20 分）---
        # 别名越长越精确，给额外加分
        alias_bonus = 0
        for alias in car.get("aliases", []):
            if alias.lower() in name_lower:
                # 按别名长度给分：长别名更精确
                bonus = 20 + len(alias)
                alias_bonus = max(alias_bonus, bonus)
        score += alias_bonus

        # --- 能源类型校验（10 分）---
        # 用 energy_hints 判断平台车辆是纯电还是混动
        for hint in car.get("energy_hints", []):
            if hint.lower() in combined:
                score += 10
                break

        # --- 座位数校验（5 分）---
        import re
        seat_match = re.search(r"(\d+)座", platform_specs)
        if seat_match and int(seat_match.group(1)) == car.get("seats", 5):
            score += 5

        # 至少要匹配到品牌或车系才算有效
        if score > best_score and score >= 30:
            best_score = score
            best_car = car

    return best_car


def match_platform_car_list(
    platform_cars: List[dict],
    nev_candidates: Optional[List[dict]] = None,
) -> List[dict]:
    """
    批量匹配：将平台的车型列表与标准库交叉匹配

    :param platform_cars: 平台车型列表 [{"name": "...", "specs": "...", ...}]
    :param nev_candidates: 标准库候选（可选），用于缩小范围
    :return: 匹配结果列表 [{"platform_car": {...}, "std_car": {...}, "score": int}]
    """
    results = []
    catalog = nev_candidates if nev_candidates is not None else NEV_CATALOG

    for pc in platform_cars:
        name = pc.get("name", "")
        specs = pc.get("specs", "")

        best_car = match_platform_car(name, specs, catalog)
        if best_car:
            results.append({
                "platform_car": pc,
                "std_car": best_car,
            })

    return results


def get_all_brands() -> List[str]:
    """获取所有品牌列表（去重）"""
    return sorted(set(car["brand"] for car in NEV_CATALOG))
