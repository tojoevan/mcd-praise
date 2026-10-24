#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
麦麦夸我好身材 (McPraise) —— 离线命令行工具（趣味夸张风）

把麦当劳套餐热量，换算成：
  1) 最近门店有多近（夸张炫耀）
  2) 主推套餐热量榜
  3) 为了吃这顿走了多少路、烧掉几个卡
  4) 还欠多少卡、要用哪些撸铁动作"补作业"

纯本地计算，不依赖网络。正式 Skill 运行时应改用麦当劳 MCP：
  - list-nutrition-foods 取实时卡路里
  - query-nearby-stores 取带 distance(米) 的门店
详见仓库根目录 MCP_INTEGRATION.md 与 SKILL.md。

用法示例：
  python mcwalkoff.py --demo
  python mcwalkoff.py --nearest-m 144 --stores "华旭国际大厦,福州路,食品一店" --weight 60
"""

import argparse
import json
import math
import os
import re
import sys
import urllib.request
import urllib.error

DEFAULT_WEIGHT = 60.0       # kg
DEFAULT_K = 0.75            # kcal/(kg·km)
DEFAULT_CITY = "上海"       # 定位失败时的兜底城市

HERE = os.path.dirname(os.path.abspath(__file__))
NUTRITION_PATH = os.path.join(HERE, "nutrition.json")

# 撸铁动作：每下消耗（kcal，70kg 成人自重/轻重量粗略估算，详见 walk-formula.md）
EXERCISES = [
    ("深蹲", 0.35),
    ("硬拉", 0.50),
    ("卧推", 0.30),
    ("引体向上", 0.40),
    ("俯卧撑", 0.25),
    ("二头弯举", 0.20),
]

# 招牌主推套餐（构成透明，卡路里由 nutrition.json 累加得出）
SIGNATURE_COMBOS = [
    ("巨无霸三件套", ["巨无霸", "中薯条", "可口可乐中杯"]),
    ("麦辣鸡腿三件套", ["麦辣鸡腿汉堡", "中薯条", "可口可乐中杯"]),
    ("安格斯豪华三件套", ["培根安格斯厚牛堡", "大薯条", "可口可乐中杯"]),
]


def load_nutrition():
    with open(NUTRITION_PATH, "r", encoding="utf-8") as f:
        return {it["name"]: it["kcal"] for it in json.load(f)["items"]}


# IP 定位：返回城市级位置（中文城市名）。仅到城市级、可能不准，失败回退默认城市。
_CITY_MAP = {
    "shanghai": "上海", "beijing": "北京", "nanjing": "南京",
    "shenzhen": "深圳", "guangzhou": "广州", "hangzhou": "杭州",
    "chengdu": "成都", "wuhan": "武汉", "xian": "西安", "tianjin": "天津",
    "chongqing": "重庆", "suzhou": "苏州", "shenyang": "沈阳",
    "jinan": "济南", "qingdao": "青岛", "dalian": "大连", "xiamen": "厦门",
    "changsha": "长沙", "zhengzhou": "郑州", "hefei": "合肥", "kunming": "昆明",
    "fuzhou": "福州", "nanchang": "南昌", "lanzhou": "兰州", "taiyuan": "太原",
    "wuxi": "无锡", "ningbo": "宁波", "wenzhou": "温州", "dongguan": "东莞",
}


def locate_city():
    """用 IP 定位返回城市级位置（中文城市名）。失败/超时回退 DEFAULT_CITY。"""
    try:
        req = urllib.request.Request(
            "https://ipapi.co/json/",
            headers={"User-Agent": "mcwalkoff/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        city = (data.get("city") or "").strip()
        if not city:
            return DEFAULT_CITY
        low = city.lower()
        if low in _CITY_MAP:
            return _CITY_MAP[low]
        if re.search(r"[一-鿿]", city):   # 已经是中文城市名
            return city
        return DEFAULT_CITY
    except Exception:
        return DEFAULT_CITY


def combo_kcal(parts, table):
    bd = []
    total = 0
    for p in parts:
        k = table[p]
        bd.append((p, k))
        total += k
    return total, bd


def walk_kcal(nearest_m, weight, k):
    roundtrip_km = 2 * nearest_m / 1000.0
    return weight * roundtrip_km * k, roundtrip_km


def lifting_reps(remaining):
    out = []
    for name, per in EXERCISES:
        reps = math.ceil(remaining / per) if remaining > 0 else 0
        out.append((name, per, reps))
    return out


def render(stores, nearest_m, weight, k, combos):
    walk, rt_km = walk_kcal(nearest_m, weight, k)
    lines = []
    lines.append("🍟 门店近报：离你最近的【%s】只有 %d 米！" % (stores[0], nearest_m))
    lines.append("   出门右拐、电梯下楼、顺便还能取个快递，这距离属于"
                 "「闻到香味就能走过去」级别。")
    if len(stores) > 1:
        others = "、".join("%s %dm" % (s, d) for s, d in zip(stores[1:], _other_dists(stores, nearest_m)))
        lines.append("   （另几家也近得不像话：%s）" % others)

    lines.append("")
    lines.append("🔥 主推热量榜（麦当劳卡路里天梯榜）：")
    for title, parts in combos:
        total, bd = combo_kcal(parts, NUTRITION)
        detail = " + ".join("%s%d" % (n, kk) for n, kk in bd)
        lines.append("   %s ≈ %d kcal（%s）" % (title, total, detail))

    lines.append("")
    lines.append("🚶 走路作业：你为了吃这顿，走去店里再走回来 ≈ %d 米，"
                 % int(rt_km * 1000))
    lines.append("   消耗 %.0f 大卡——差不多是你咬一口汉堡的热量，先感动自己一下。" % walk)

    lines.append("")
    # 以第一个套餐为例做撸铁补作业
    title0, parts0 = combos[0]
    total0, _ = combo_kcal(parts0, NUTRITION)
    remaining = max(total0 - walk, 0)
    lines.append("🏋️ 撸铁补作业（以%s为例，这顿 %d，走路只烧掉 %.0f，还欠 %d 大卡）："
                 % (title0, total0, walk, remaining))
    for name, per, reps in lifting_reps(remaining):
        lines.append("   · %s %d 个（每下约 %.2f kcal）" % (name, reps, per))

    lines.append("")
    lines.append("（估算，仅供参考，非专业运动/营养建议；实际以麦当劳 MCP 实时数据为准）")
    return "\n".join(lines)


def _other_dists(stores, nearest_m):
    # 仅为展示：其余门店距离按最近店依次递增估算（真实场景由 MCP 返回）
    step = max(nearest_m // 2, 50)
    return [nearest_m + step * (i + 1) for i in range(len(stores) - 1)]


def demo():
    global NUTRITION
    NUTRITION = load_nutrition()
    stores = ["华旭国际大厦餐厅", "福州路餐厅", "食品一店"]
    print(render(stores, 144, DEFAULT_WEIGHT, DEFAULT_K, SIGNATURE_COMBOS))


def main():
    global NUTRITION
    p = argparse.ArgumentParser(description="麦麦夸我好身材 · 麦当劳卡路里补作业（离线版）")
    p.add_argument("--nearest-m", type=int, default=144, help="最近门店距离(米)，默认 144")
    p.add_argument("--stores", default="华旭国际大厦餐厅,福州路餐厅,食品一店",
                   help="最近 1-3 家店名，逗号分隔")
    p.add_argument("--weight", type=float, default=DEFAULT_WEIGHT, help="体重 kg，默认 60")
    p.add_argument("--k", type=float, default=DEFAULT_K, help="系数 K kcal/(kg·km)，默认 0.75")
    p.add_argument("--demo", action="store_true", help="运行内置示例（上海·人民广场真实快照）")
    p.add_argument("--locate", action="store_true",
                   help="仅输出 IP 定位得到的城市名（用于 Skill 自动定位兜底）")
    args = p.parse_args()

    if args.locate:
        print(locate_city())
        return

    NUTRITION = load_nutrition()
    stores = [s.strip() for s in args.stores.split(",") if s.strip()]
    if not stores:
        p.print_help()
        sys.exit(1)
    print(render(stores, args.nearest_m, args.weight, args.k, SIGNATURE_COMBOS))


if __name__ == "__main__":
    main()
