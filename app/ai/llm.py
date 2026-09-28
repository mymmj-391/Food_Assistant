import time
import logging
from langchain_openai import ChatOpenAI
from app.core.settings import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEEPSEEK_MODEL

logger = logging.getLogger("middleware")

_llm = None


def get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=0.7,
            max_tokens=2048,
        )
    return _llm


def _retry_sync(func, max_retries: int = 3, base_delay: float = 1.0):
    """同步重试包装器（带指数退避）"""
    last_exception = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"[RETRY] 第{attempt + 1}次失败: {type(e).__name__}, {delay}s后重试")
                time.sleep(delay)
    raise last_exception


def chat_with_tools(
    messages: list,
    tools: list = None,
    model: str = DEEPSEEK_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 2048,
):
    llm = get_llm()
    llm.model_name = model
    llm.temperature = temperature
    llm.max_tokens = max_tokens

    if tools:
        llm_with_tools = llm.bind_tools(tools)
        response = _retry_sync(lambda: llm_with_tools.invoke(messages))
    else:
        response = _retry_sync(lambda: llm.invoke(messages))

    return response
