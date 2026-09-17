import json
import httpx
from langchain_core.tools import tool
from app.core.settings import (
    WEATHER_API_KEY,
    WEATHER_API_URL,
    WEATHER_CITY_URL,
    AMAP_API_KEY,
    AMAP_IP_URL,
)
from app.services.dish_service import get_dish_detail, get_category_list, CATEGORY_MAP


@tool
async def get_weather(city: str) -> str:
    """获取指定城市的天气信息。当用户询问天气、气温时使用，用于根据天气推荐适合的饮食（如寒冷天气推荐温热汤品，炎热天气推荐清淡凉菜）。

    Args:
        city: 城市名称，如'北京'、'上海'、'广州'等
    """
    errors = []

    # 方案1：使用和风天气API
    if WEATHER_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                city_resp = await client.get(
                    WEATHER_CITY_URL,
                    params={"location": city, "key": WEATHER_API_KEY}
                )
                city_data = city_resp.json()

                if city_data.get("code") == "200" and city_data.get("location"):
                    location_id = city_data["location"][0]["id"]

                    weather_resp = await client.get(
                        WEATHER_API_URL,
                        params={"location": location_id, "key": WEATHER_API_KEY}
                    )
                    weather_data = weather_resp.json()

                    if weather_data.get("code") == "200":
                        now = weather_data["now"]
                        result = {
                            "city": city,
                            "temperature": now.get("temp", "未知"),
                            "feels_like": now.get("feelsLike", "未知"),
                            "weather": now.get("text", "未知"),
                            "humidity": now.get("humidity", "未知"),
                            "wind": f"{now.get('windDir', '')} {now.get('windScale', '')}级",
                            "update_time": weather_data.get("updateTime", ""),
                            "source": "qweather",
                        }
                        return json.dumps(result, ensure_ascii=False)
                    else:
                        errors.append(f"和风天气: {weather_data.get('message', '未知错误')}")
                else:
                    errors.append(f"和风天气: 未找到城市 {city}")
        except Exception as e:
            errors.append(f"和风天气: {type(e).__name__}")

    # 方案2：使用高德天气API（如果配置了高德Key）
    if AMAP_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # 先获取城市adcode
                geo_resp = await client.get(
                    "https://restapi.amap.com/v3/geocode/geo",
                    params={"address": city, "key": AMAP_API_KEY, "output": "json"}
                )
                geo_data = geo_resp.json()
                if geo_data.get("status") == "1" and geo_data.get("geocodes"):
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
                        errors.append(f"高德天气: 获取失败")
                else:
                    errors.append(f"高德天气: 未找到城市 {city}")
        except Exception as e:
            errors.append(f"高德天气: {type(e).__name__}")

    # 所有方案都失败
    return json.dumps({
        "error": "暂时无法获取天气信息",
        "detail": "; ".join(errors),
        "suggestion": f"您可以告诉我{city}的天气情况，我可以为您推荐适合的美食"
    }, ensure_ascii=False)


@tool
async def get_location() -> str:
    """获取用户当前的地理位置信息，包括城市、经纬度等。当用户询问当前位置、附近美食、本地天气时使用。"""
    errors = []

    # 方案1：优先使用高德地图（国内精度高，免费额度约3万次/天）
    # 注意：必须使用"Web服务"类型的API Key，"Web端(JS API"类型不支持IP定位
    if AMAP_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(AMAP_IP_URL, params={
                    "key": AMAP_API_KEY,
                    "output": "json",
                })
                data = resp.json()
                if data.get("status") == "1":
                    result = {
                        "province": data.get("province", "未知"),
                        "city": data.get("city", "未知"),
                        "adcode": data.get("adcode", ""),
                        "rectangle": data.get("rectangle", ""),
                        "source": "amap",
                    }
                    return json.dumps(result, ensure_ascii=False)
                else:
                    error_info = data.get("info", "未知错误")
                    if data.get("infocode") == "10009":
                        error_info = "API Key类型错误，请使用'Web服务'类型的Key（非Web端JS API）"
                    errors.append(f"高德地图: {error_info}")
        except Exception as e:
            errors.append(f"高德地图: {type(e).__name__}")

    # 方案2：使用太平洋网络IP API（国内可用，无需密钥）
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(
                "https://whois.pconline.com.cn/ipJson.jsp?json=true",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            resp.encoding = resp.apparent_encoding or "utf-8"
            data = resp.json()
            if data.get("ip"):
                result = {
                    "country": "中国",
                    "province": data.get("pro", "未知"),
                    "city": data.get("city", "未知"),
                    "ip": data.get("ip", "未知"),
                    "source": "pconline",
                }
                return json.dumps(result, ensure_ascii=False)
            else:
                errors.append("太平洋IP: 返回错误")
    except Exception as e:
        errors.append(f"太平洋IP: {type(e).__name__}")

    # 方案3：使用 IP-API（需要HTTPS，45次/分钟）
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get("https://ip-api.com/json/", headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            data = resp.json()

            if data.get("status") == "success":
                result = {
                    "country": data.get("country", "未知"),
                    "region": data.get("regionName", "未知"),
                    "city": data.get("city", "未知"),
                    "latitude": data.get("lat", 0),
                    "longitude": data.get("lon", 0),
                    "ip": data.get("query", "未知"),
                    "source": "ip-api",
                }
                return json.dumps(result, ensure_ascii=False)
            else:
                errors.append(f"IP-API: {data.get('message', '未知错误')}")
    except Exception as e:
        errors.append(f"IP-API: {type(e).__name__}")

    # 所有方案都失败，返回友好提示
    return json.dumps({
        "error": "暂时无法获取位置信息",
        "detail": "; ".join(errors),
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
    """执行指定工具"""
    tool_map = {t.name: t for t in ALL_TOOLS}
    func = tool_map.get(tool_name)
    if not func:
        return {"error": f"未知工具: {tool_name}"}
    result = await func.ainvoke(arguments)
    if isinstance(result, str):
        return json.loads(result)
    return result
