from langchain_openai import ChatOpenAI
from app.core.settings import DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY, DEEPSEEK_MODEL

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
        response = llm_with_tools.invoke(messages)
    else:
        response = llm.invoke(messages)

    return response
