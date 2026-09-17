from datetime import datetime
from sqlalchemy import select, func
from app.models.chat import ChatSessionModel, ChatMessageModel
from app.core.database import async_session

MAX_HISTORY_MESSAGES = 20


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


def format_history_for_prompt(messages: list) -> str:
    if not messages:
        return ""

    recent_messages = messages[-MAX_HISTORY_MESSAGES:]
    history_lines = []
    for msg in recent_messages:
        role = "用户" if msg["sender"] == "user" else "助手"
        history_lines.append(f"{role}: {msg['content']}")

    return "历史对话:\n" + "\n".join(history_lines)
