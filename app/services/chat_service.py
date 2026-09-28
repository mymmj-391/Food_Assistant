from datetime import datetime
from sqlalchemy import select, func
from app.models.chat import ChatSessionModel, ChatMessageModel
from app.core.database import async_session
from app.core.middleware import mask_pii

MAX_HISTORY_MESSAGES = 20
COMPRESS_THRESHOLD = 12
KEEP_RECENT = 4


async def get_or_create_session(session_id: str | None, user_id: str) -> str:
    async with async_session() as session:
        if session_id:
            result = await session.execute(
                select(ChatSessionModel).where(ChatSessionModel.session_id == session_id)
            )
            if result.scalar_one_or_none():
                return session_id

        import uuid
        new_session_id = str(uuid.uuid4())
        chat_session = ChatSessionModel(
            session_id=new_session_id,
            user_id=user_id,
        )
        session.add(chat_session)
        await session.commit()
        return new_session_id


async def save_message(session_id: str, sender: str, content: str):
    if sender == "user":
        content = mask_pii(content)
    async with async_session() as session:
        result = await session.execute(
            select(func.count()).select_from(ChatMessageModel).where(
                ChatMessageModel.session_id == session_id
            )
        )
        msg_count = result.scalar_one()

        message = ChatMessageModel(
            session_id=session_id,
            sender=sender,
            content=content,
            msg_seq=msg_count + 1,
        )
        session.add(message)

        result = await session.execute(
            select(ChatSessionModel).where(ChatSessionModel.session_id == session_id)
        )
        chat_session = result.scalar_one_or_none()
        if chat_session:
            chat_session.last_msg_time = datetime.now()

        await session.commit()


async def get_session_history(session_id: str) -> list:
    async with async_session() as session:
        result = await session.execute(
            select(ChatMessageModel)
            .where(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.msg_seq)
        )
        messages = result.scalars().all()
        return [
            {
                "sender": msg.sender,
                "content": msg.content,
                "msg_seq": msg.msg_seq,
                "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if msg.created_at else "",
            }
            for msg in messages
        ]


async def session_belongs_to_user(session_id: str, user_id: str) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(ChatSessionModel).where(
                ChatSessionModel.session_id == session_id,
                ChatSessionModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None


async def format_history_for_prompt(messages: list) -> str:
    if not messages:
        return ""

    recent_messages = messages[-MAX_HISTORY_MESSAGES:]

    if len(recent_messages) <= COMPRESS_THRESHOLD:
        history_lines = []
        for msg in recent_messages:
            role = "用户" if msg["sender"] == "user" else "助手"
            history_lines.append(f"{role}: {msg['content']}")
        return "历史对话:\n" + "\n".join(history_lines)

    early_messages = recent_messages[:-KEEP_RECENT]
    recent_preserved = recent_messages[-KEEP_RECENT:]

    lines = []
    for msg in early_messages:
        role = "用户" if msg["sender"] == "user" else "助手"
        content = msg["content"][:150]
        lines.append(f"{role}: {content}")
    raw = "\n".join(lines)

    from app.ai.llm import get_llm
    llm = get_llm()
    prompt = (
        "请将以下对话压缩为 150 字以内的摘要，重点保留："
        "用户的饮食偏好、忌口、喜欢的菜品、重要结论。"
        "不要罗列对话流水，只输出核心信息。\n\n"
        f"{raw}"
    )
    response = llm.invoke(prompt)
    summary = response.content.strip()
    print(f"[COMPRESS] {len(early_messages)} 条消息压缩为 {len(summary)} 字摘要")

    result_lines = [f"对话摘要: {summary}"]
    for msg in recent_preserved:
        role = "用户" if msg["sender"] == "user" else "助手"
        result_lines.append(f"{role}: {msg['content']}")

    return "历史对话:\n" + "\n".join(result_lines)
