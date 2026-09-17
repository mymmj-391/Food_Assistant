import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://root:123456@localhost:3306/Food_Assistant")
# 库名从 DATABASE_URL 中解析，避免与连接串不一致
DB_NAME = urlparse(DATABASE_URL).path.lstrip("/") or "Food_Assistant"

DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

SILICONFLOW_BASE_URL = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

MILVUS_URI = os.getenv("MILVUS_URI", "http://localhost:19530")
COLLECTION_NAME = "food_knowledge"

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
WEATHER_API_URL = "https://devapi.qweather.com/v7/weather/now"
WEATHER_CITY_URL = "https://geoapi.qweather.com/v2/city/lookup"
AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")
AMAP_IP_URL = "https://restapi.amap.com/v3/ip"

KNOWLEDGE_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "knowledge")
DISHES_ROOT = os.path.join(KNOWLEDGE_ROOT, "dishes")
TIPS_ROOT = os.path.join(KNOWLEDGE_ROOT, "tips")

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000/api")
