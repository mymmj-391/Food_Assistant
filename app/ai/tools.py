import json
import time
import logging
import os
from datetime import datetime
import httpx
from langchain_core.tools import tool
from app.core.settings import AMAP_API_KEY, AMAP_IP_URL
from app.core.context import get_client_ip
from app.services.dish_service import get_dish_detail, get_category_list, CATEGORY_MAP

_tool_logger = logging.getLogger("tool_call")
_tool_logger.setLevel(logging.INFO)
_log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(_log_dir, exist_ok=True)
_handler = logging.FileHandler(os.path.join(_log_dir, "tool_calls.log"), encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(message)s"))
_tool_logger.addHandler(_handler)
_tool_logger.propagate = False


@tool
async def get_weather(city: str) -> str:
    """获取指定城市的天气信息。当用户询问天气、气温时使用，用于根据天气推荐适合的饮食（如寒冷天气推荐温热汤品，炎热天气推荐清淡凉菜）。

    Args:
        city: 城市名称，如'北京'、'上海'、'广州'等
    """
    if not AMAP_API_KEY:
        return json.dumps({
            "error": "未配置高德 API Key",
            "suggestion": f"您可以告诉我{city}的天气情况，我可以为您推荐适合的美食"
        }, ensure_ascii=False)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            geo_resp = await client.get(
                "https://restapi.amap.com/v3/geocode/geo",
                params={"address": city, "key": AMAP_API_KEY, "output": "json"}
            )
            geo_data = geo_resp.json()
            if geo_data.get("status") != "1" or not geo_data.get("geocodes"):
                return json.dumps({
                    "error": f"未找到城市 {city}",
                    "suggestion": "请确认城市名称是否正确"
                }, ensure_ascii=False)

            adcode = geo_data["geocodes"][0].get("adcode", "")

            weather_resp = await client.get(
                "https://restapi.amap.com/v3/weather/weatherInfo",
                params={"city": adcode, "key": AMAP_API_KEY, "output": "json", "extensions": "base"}
            )
            weather_data = weather_resp.json()
            if weather_data.get("status") == "1" and weather_data.get("lives"):
                live = weather_data["lives"][0]
                result = {
                    "city": live.get("city", city),
                    "temperature": live.get("temperature", "未知"),
                    "weather": live.get("weather", "未知"),
                    "humidity": live.get("humidity", "未知"),
                    "wind": f"{live.get('winddirection', '')}风 {live.get('windpower', '')}级",
                    "source": "amap",
                }
                return json.dumps(result, ensure_ascii=False)
            else:
                return json.dumps({
                    "error": "获取天气失败",
                    "suggestion": f"您可以告诉我{city}的天气情况，我可以为您推荐适合的美食"
                }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": f"获取天气异常: {type(e).__name__}",
            "suggestion": f"您可以告诉我{city}的天气情况，我可以为您推荐适合的美食"
        }, ensure_ascii=False)


@tool
async def get_location() -> str:
    """获取用户当前的地理位置信息，包括城市、经纬度等。当用户询问当前位置、附近美食、本地天气时使用。"""
    user_ip = get_client_ip()

    if not AMAP_API_KEY:
        return json.dumps({
            "error": "未配置高德 API Key",
            "suggestion": "您可以直接告诉我您所在的城市，我可以为您推荐当地美食"
        }, ensure_ascii=False)

    if not user_ip:
        return json.dumps({
            "error": "无法获取用户 IP",
            "suggestion": "您可以直接告诉我您所在的城市，我可以为您推荐当地美食"
        }, ensure_ascii=False)

    # 内网/回环 IP 高德无法定位，不传 ip 参数让高德使用请求方出口 IP
    is_private_ip = (
        user_ip in ("127.0.0.1", "0:0:0:0:0:0:0:1", "::1", "")
        or user_ip.startswith("192.168.")
        or user_ip.startswith("10.")
        or user_ip.startswith("172.16.") or user_ip.startswith("172.17.")
        or user_ip.startswith("172.18.") or user_ip.startswith("172.19.")
        or user_ip.startswith("172.2") or user_ip.startswith("172.30.")
        or user_ip.startswith("172.31.")
    )

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            params = {"key": AMAP_API_KEY, "output": "json"}
            if not is_private_ip:
                params["ip"] = user_ip
            resp = await client.get(AMAP_IP_URL, params=params)
            data = resp.json()
            if data.get("status") == "1":
                result = {
                    "province": data.get("province", "未知"),
                    "city": data.get("city", "未知"),
                    "adcode": data.get("adcode", ""),
                    "rectangle": data.get("rectangle", ""),
                    "ip": user_ip if not is_private_ip else "局域网/服务器出口",
                    "source": "amap",
                }
                return json.dumps(result, ensure_ascii=False)
            else:
                error_info = data.get("info", "未知错误")
                if data.get("infocode") == "10009":
                    error_info = "API Key类型错误，请使用'Web服务'类型的Key（非Web端JS API）"
                return json.dumps({
                    "error": f"高德定位失败: {error_info}",
                    "ip": user_ip,
                    "suggestion": "您可以直接告诉我您所在的城市，我可以为您推荐当地美食"
                }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": f"定位异常: {type(e).__name__}",
            "ip": user_ip,
            "suggestion": "您可以直接告诉我您所在的城市，我可以为您推荐当地美食"
        }, ensure_ascii=False)


@tool
async def get_time() -> str:
    """获取当前时间和日期信息。当用户询问现在几点、今天日期、是否到了吃饭时间时使用。"""
    from datetime import datetime
    now = datetime.now()
    result = {
        "date": now.strftime("%Y年%m月%d日"),
        "time": now.strftime("%H:%M:%S"),
        "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()],
        "hour": now.hour
    }
    return json.dumps(result, ensure_ascii=False)


@tool
async def get_dish_info(category: str, dish_name: str) -> str:
    """获取指定菜品的详细信息，包括食材、做法、营养价值等。当用户询问某个具体菜品的做法、食材、营养成分时使用。

    Args:
        category: 菜品分类ID，如'vegetable_dish'（素菜）、'meat_dish'（荤菜）、'soup'（汤品）等
        dish_name: 菜品名称，如'番茄炒蛋'、'红烧肉'等
    """
    try:
        detail = get_dish_detail(category, dish_name)
        if not detail:
            return json.dumps({"error": f"未找到菜品: {category}/{dish_name}"}, ensure_ascii=False)

        content = detail.get("content", "")
        if len(content) > 2000:
            content = content[:2000] + "..."

        result = {
            "name": detail.get("name", dish_name),
            "category": category,
            "content": content,
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"获取菜品信息失败: {str(e)}"}, ensure_ascii=False)


@tool
async def list_dish_categories() -> str:
    """获取所有菜品分类列表。当用户询问有哪些菜品分类、想看所有分类时使用。"""
    try:
        categories = get_category_list()
        result = [
            {"id": c["id"], "name": c["name"]}
            for c in categories
        ]
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"获取分类失败: {str(e)}"}, ensure_ascii=False)


@tool
async def get_category_name(category_id: str) -> str:
    """根据菜品分类ID获取分类的中文名称。

    Args:
        category_id: 菜品分类ID，如'vegetable_dish'、'meat_dish'等
    """
    name = CATEGORY_MAP.get(category_id, category_id)
    return json.dumps({"id": category_id, "name": name}, ensure_ascii=False)


ALL_TOOLS = [get_weather, get_location, get_time, get_dish_info, list_dish_categories, get_category_name]


async def execute_tool(tool_name: str, arguments: dict) -> dict:
    """执行指定工具，并记录结构化调用日志"""
    start = time.time()
    success = True
    error_msg = None

    tool_map = {t.name: t for t in ALL_TOOLS}
    func = tool_map.get(tool_name)
    if not func:
        success = False
        error_msg = f"未知工具: {tool_name}"
        result = {"error": error_msg}
    else:
        try:
            raw = await func.ainvoke(arguments)
            result = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(result, dict) and "error" in result:
                success = False
                error_msg = result["error"]
        except Exception as e:
            success = False
            error_msg = str(e)
            result = {"error": error_msg}

    duration_ms = round((time.time() - start) * 1000, 1)

    log_entry = json.dumps({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tool": tool_name,
        "arguments": arguments,
        "duration_ms": duration_ms,
        "success": success,
        "error": error_msg,
    }, ensure_ascii=False)
    _tool_logger.info(log_entry)

    status = "✓" if success else "✗"
    print(f"[TOOL] {status} {tool_name}  {duration_ms}ms  {arguments}")

    return result
