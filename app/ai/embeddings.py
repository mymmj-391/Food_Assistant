from langchain_openai import OpenAIEmbeddings
from app.core.settings import SILICONFLOW_BASE_URL, SILICONFLOW_API_KEY, EMBEDDING_MODEL

_embeddings = None


def get_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=SILICONFLOW_API_KEY,
            base_url=SILICONFLOW_BASE_URL,
        )
    return _embeddings


def encode_query(text: str) -> list:
    embeddings = get_embeddings()
    return embeddings.embed_query(text)
