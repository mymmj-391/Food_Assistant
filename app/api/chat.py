from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.rag import rag_chat, rag_chat_stream
from app.services.chat_service import (
    get_or_create_session,
    save_message,
    get_session_history,
    session_belongs_to_user,
    format_history_for_prompt,
)
from app.dependencies import get_current_user, get_current_user_optional

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post("/ask", response_model=ChatResponse)
async def chat_ask(
    request: ChatRequest,
    user=Depends(get_current_user_optional),
):
    user_id = user.username if user else "guest"
    session_id = await get_or_create_session(request.session_id, user_id)

    history = await get_session_history(session_id)
    history_prompt = format_history_for_prompt(history)

    response = await rag_chat(
        query=request.query,
        top_k=request.top_k,
        history_prompt=history_prompt,
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
    user=Depends(get_current_user_optional),
):
    user_id = user.username if user else "guest"
    session_id = await get_or_create_session(request.session_id, user_id)

    history = await get_session_history(session_id)
    history_prompt = format_history_for_prompt(history)

    await save_message(session_id, "user", request.query)

    async def event_stream():
        full_answer = ""
        sources = []
        dish_links = []

        async for chunk in rag_chat_stream(
            query=request.query,
            top_k=request.top_k,
            history_prompt=history_prompt,
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
