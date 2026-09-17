import json
import traceback
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from app.ai.llm import chat_with_tools
from app.ai.tools import ALL_TOOLS, execute_tool
from app.ai.knowledge import search_knowledge
from app.schemas.chat import ChatResponse, SourceInfo, DishLink

SYSTEM_PROMPT = """你是一个专业的健康饮食助手，擅长根据用户的问题提供个性化的饮食建议。

你的核心职责：
1. 根据知识库内容回答用户关于菜品、食材、烹饪技巧的问题
2. 在需要时调用工具获取菜品详细信息
3. 提供健康、实用的饮食建议
4. 根据天气和时间信息给出饮食建议（如天气推荐温热食物，夏季推荐清淡食物）

可用工具：
- get_weather: 获取城市天气信息，用于根据天气推荐适合的饮食（如寒冷天气推荐温热食物）
- get_location: 获取用户位置，用于推荐当地特色美食
- get_time: 获取当前时间，用于用餐时间建议（早餐、午餐、晚餐）
- get_dish_info: 获取具体菜品的详细做法和食材信息
- list_dish_categories: 获取所有菜品分类列表
- get_category_name: 根据分类ID获取分类的中文名称

工具使用规则：
- 当用户询问某个具体菜品的做法、食材时，必须调用 get_dish_info 获取详细信息
- 当用户询问有哪些分类时，必须调用 list_dish_categories
- 当用户询问天气、气温时，必须调用 get_weather 获取天气后给出适合的饮食建议
- 当用户询问当前位置时，必须调用 get_location 获取位置后推荐当地美食
- 当用户询问现在几点、今天日期时，必须调用 get_time 给出用餐建议
- 当知识库中的信息不够详细时，主动调用工具补充信息

回答要求：
- 回答要简洁、专业、易懂
- 回答必须与美食、饮食、烹饪密切相关
- 不要提及"知识库"、"数据库"等词汇
- 回答要基于工具返回的实际数据，不要编造信息
- 当工具调用失败时，给出友好的美食建议而不是错误信息
- 始终围绕"吃"这个核心主题，给出实用的饮食建议"""


def build_context(search_results: list) -> str:
    if not search_results:
        return "（暂无相关知识库内容）"

    context_parts = []
    for i, result in enumerate(search_results, 1):
        category = result.get("category", "")
        type_ = result.get("type", "")
        text = result.get("text", "")
        context_parts.append(f"[{i}] ({category}/{type_}) {text}")

    return "\n\n".join(context_parts)


def extract_dish_names(search_results: list) -> list:
    dish_links = []
    seen = set()

    for result in search_results:
        source = result.get("source", "")
        category = result.get("category", "")
        type_ = result.get("type", "")

        if not source or not category:
            continue

        if type_ != "菜品":
            continue

        parts = source.split("/")
        if len(parts) >= 2:
            category_folder = parts[0]
            dish_name = parts[1].replace(".md", "")

            if dish_name not in seen:
                seen.add(dish_name)
                dish_links.append(DishLink(
                    name=dish_name,
                    category=category_folder,
                    url=f"/pages/dish-detail/dish-detail?category={category_folder}&dish={dish_name}",
                ))

    return dish_links


async def rag_chat(query: str, top_k: int = 5, history_prompt: str = "") -> ChatResponse:
    try:
        print(f"[RAG] 搜索知识库: query={query}, top_k={top_k}")
        search_results = search_knowledge(query, top_k=top_k)
        print(f"[RAG] 搜索完成: 找到 {len(search_results)} 条结果")
    except Exception as e:
        print(f"[RAG] 搜索知识库失败: {e}")
        traceback.print_exc()
        search_results = []

    context = build_context(search_results)

    history_section = f"\n\n{history_prompt}" if history_prompt else ""

    dish_links = extract_dish_names(search_results)

    # 构建可用菜品列表，方便AI调用工具时引用
    available_dishes = ""
    if dish_links:
        dish_list = ", ".join([f"{d.name}({d.category})" for d in dish_links[:5]])
        available_dishes = f"\n\n相关菜品: {dish_list}"

    user_content = f"""相关知识库内容:
{context}{available_dishes}{history_section}

用户问题: {query}"""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    sources = [
        SourceInfo(
            source=r.get("source", ""),
            category=r.get("category", ""),
            type=r.get("type", ""),
            text=r.get("text", "")[:200],
            distance=r.get("distance", 0),
        )
        for r in search_results
    ]

    try:
        print("[RAG] 调用 LLM...")
        max_rounds = 3
        for i in range(max_rounds):
            response = chat_with_tools(messages=messages, tools=ALL_TOOLS)
            print(f"[RAG] LLM 响应完成 (轮次 {i+1})")

            tool_calls = getattr(response, 'tool_calls', None)
            if tool_calls:
                messages.append(AIMessage(
                    content=response.content or "",
                    tool_calls=[{
                        "id": tc.get("id") if isinstance(tc, dict) else tc.id,
                        "name": tc.get("name") if isinstance(tc, dict) else tc.name,
                        "args": tc.get("args") if isinstance(tc, dict) else tc.args,
                    } for tc in tool_calls]
                ))

                for tc in tool_calls:
                    tc_id = tc.get("id") if isinstance(tc, dict) else tc.id
                    tc_name = tc.get("name") if isinstance(tc, dict) else tc.name
                    tc_args = tc.get("args") if isinstance(tc, dict) else tc.args
                    print(f"[RAG] 调用工具: {tc_name}, 参数: {tc_args}")
                    result = await execute_tool(tc_name, tc_args)
                    print(f"[RAG] 工具结果: {json.dumps(result, ensure_ascii=False)[:200]}")
                    messages.append(ToolMessage(
                        content=json.dumps(result, ensure_ascii=False),
                        tool_call_id=tc_id,
                    ))
            else:
                return ChatResponse(
                    session_id="",
                    answer=response.content or "",
                    sources=sources,
                    dish_links=dish_links,
                )

        return ChatResponse(
            session_id="",
            answer="抱歉，处理时间过长，请稍后再试。",
            sources=sources,
            dish_links=dish_links,
        )
    except Exception as e:
        print(f"[RAG] LLM 调用失败: {e}")
        traceback.print_exc()
        return ChatResponse(
            session_id="",
            answer=f"抱歉，AI 服务暂时不可用：{str(e)[:100]}",
            sources=sources,
            dish_links=dish_links,
        )


async def rag_chat_stream(query: str, top_k: int = 5, history_prompt: str = ""):
    try:
        print(f"[RAG Stream] 搜索知识库: query={query}, top_k={top_k}")
        search_results = search_knowledge(query, top_k=top_k)
        print(f"[RAG Stream] 搜索完成: 找到 {len(search_results)} 条结果")
    except Exception as e:
        print(f"[RAG Stream] 搜索知识库失败: {e}")
        traceback.print_exc()
        search_results = []

    context = build_context(search_results)
    history_section = f"\n\n{history_prompt}" if history_prompt else ""
    dish_links = extract_dish_names(search_results)

    available_dishes = ""
    if dish_links:
        dish_list = ", ".join([f"{d.name}({d.category})" for d in dish_links[:5]])
        available_dishes = f"\n\n相关菜品: {dish_list}"

    user_content = f"""相关知识库内容:
{context}{available_dishes}{history_section}

用户问题: {query}"""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    sources = [
        SourceInfo(
            source=r.get("source", ""),
            category=r.get("category", ""),
            type=r.get("type", ""),
            text=r.get("text", "")[:200],
            distance=r.get("distance", 0),
        )
        for r in search_results
    ]

    try:
        print("[RAG Stream] 调用 LLM...")
        from app.ai.llm import get_llm
        llm = get_llm()
        llm_with_tools = llm.bind_tools(ALL_TOOLS)

        max_rounds = 3
        for i in range(max_rounds):
            response = llm_with_tools.invoke(messages)
            print(f"[RAG Stream] LLM 响应完成 (轮次 {i+1})")

            tool_calls = getattr(response, 'tool_calls', None)
            if tool_calls:
                messages.append(AIMessage(
                    content=response.content or "",
                    tool_calls=[{
                        "id": tc.get("id") if isinstance(tc, dict) else tc.id,
                        "name": tc.get("name") if isinstance(tc, dict) else tc.name,
                        "args": tc.get("args") if isinstance(tc, dict) else tc.args,
                    } for tc in tool_calls]
                ))

                for tc in tool_calls:
                    tc_id = tc.get("id") if isinstance(tc, dict) else tc.id
                    tc_name = tc.get("name") if isinstance(tc, dict) else tc.name
                    tc_args = tc.get("args") if isinstance(tc, dict) else tc.args

                    yield {"type": "tool_call", "name": tc_name}

                    print(f"[RAG Stream] 调用工具: {tc_name}, 参数: {tc_args}")
                    result = await execute_tool(tc_name, tc_args)
                    print(f"[RAG Stream] 工具结果: {json.dumps(result, ensure_ascii=False)[:200]}")
                    messages.append(ToolMessage(
                        content=json.dumps(result, ensure_ascii=False),
                        tool_call_id=tc_id,
                    ))
            else:
                async for chunk in llm.astream(messages):
                    if chunk.content:
                        yield {"type": "content", "content": chunk.content}

                yield {"type": "done", "sources": [s.model_dump() for s in sources], "dish_links": [d.model_dump() for d in dish_links]}
                return

        yield {"type": "error", "content": "抱歉，处理时间过长，请稍后再试。"}
    except Exception as e:
        print(f"[RAG Stream] LLM 调用失败: {e}")
        traceback.print_exc()
        yield {"type": "error", "content": f"抱歉，AI 服务暂时不可用：{str(e)[:100]}"}
