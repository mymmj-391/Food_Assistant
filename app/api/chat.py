from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.rag import rag_chat, rag_chat_stream
from app.services.chat_service import (
    get_or_create_session,
    save_message,
    get_session_history,
    session_belongs_to_user,
)
from app.services.chat_service import format_history_for_prompt
from app.api.deps import get_current_user, get_current_user_optional
from app.core.context import set_client_ip

router = APIRouter(prefix="/chat", tags=["聊天"])


def extract_client_ip(request: Request) -> str:
    """从请求头中提取用户真实 IP（兼容 nginx/ngrok 代理）"""
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        # X-Forwarded-For 格式: "client_ip, proxy1_ip, proxy2_ip"，第一个是原始客户端
        return xff.split(",")[0].strip()
    x_real_ip = request.headers.get("x-real-ip", "")
    if x_real_ip:
        return x_real_ip.strip()
    if request.client:
        return request.client.host
    return ""


@router.post("/ask", response_model=ChatResponse)
async def chat_ask(
    request: ChatRequest,
    http_request: Request,
    user=Depends(get_current_user_optional),
):
    set_client_ip(extract_client_ip(http_request))

    user_id = user.username if user else "guest"
    session_id = await get_or_create_session(request.session_id, user_id)

    history = await get_session_history(session_id)
    history_prompt = await format_history_for_prompt(history)

    response = await rag_chat(
        query=request.query,
        top_k=request.top_k,
        history_prompt=history_prompt,
        user_id=user_id,
    )

    await save_message(session_id, "user", request.query)
    await save_message(session_id, "ai", response.answer)

    response.session_id = session_id
    return response


@router.get("/history/{session_id}", response_model=list)
async def chat_history(
    session_id: str,
    user=Depends(get_current_user_optional),
):
    user_id = user.username if user else "guest"
    if not await session_belongs_to_user(session_id, user_id):
        raise HTTPException(status_code=403, detail="无权访问该会话")
    return await get_session_history(session_id)


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    http_request: Request,
    user=Depends(get_current_user_optional),
):
    set_client_ip(extract_client_ip(http_request))

    user_id = user.username if user else "guest"
    session_id = await get_or_create_session(request.session_id, user_id)

    history = await get_session_history(session_id)
    history_prompt = await format_history_for_prompt(history)

    await save_message(session_id, "user", request.query)

    async def event_stream():
        full_answer = ""
        sources = []
        dish_links = []

        async for chunk in rag_chat_stream(
            query=request.query,
            top_k=request.top_k,
            history_prompt=history_prompt,
            user_id=user_id,
        ):
            if chunk["type"] == "content":
                full_answer += chunk["content"]
                data = json.dumps({"type": "content", "content": chunk["content"]}, ensure_ascii=False)
                yield f"data: {data}\n\n"
            elif chunk["type"] == "tool_call":
                data = json.dumps({"type": "tool_call", "name": chunk["name"]}, ensure_ascii=False)
                yield f"data: {data}\n\n"
            elif chunk["type"] == "done":
                sources = chunk.get("sources", [])
                dish_links = chunk.get("dish_links", [])
                data = json.dumps({
                    "type": "done",
                    "session_id": session_id,
                    "sources": sources,
                    "dish_links": dish_links,
                }, ensure_ascii=False)
                yield f"data: {data}\n\n"
            elif chunk["type"] == "error":
                data = json.dumps({"type": "error", "content": chunk.get("content", "未知错误")}, ensure_ascii=False)
                yield f"data: {data}\n\n"

        if full_answer:
            await save_message(session_id, "ai", full_answer)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
