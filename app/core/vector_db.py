import hashlib
from langchain_milvus import Milvus
from pymilvus import MilvusClient, DataType
from app.core.settings import MILVUS_URI, COLLECTION_NAME
from app.ai.embeddings import get_embeddings

_vector_store = None


def compute_md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def get_vector_store() -> Milvus:
    global _vector_store
    if _vector_store is None:
        embeddings = get_embeddings()
        try:
            _vector_store = Milvus(
                embedding_function=embeddings,
                collection_name=COLLECTION_NAME,
                connection_args={"uri": MILVUS_URI},
                auto_id=True,
                enable_dynamic_field=True,
                index_params={"metric_type": "COSINE", "index_type": "FLAT"},
            )
        except Exception as e:
            error_msg = str(e)
            if "non-exist field" in error_msg or "cannot create index" in error_msg:
                print(f"[Milvus] 集合 schema 不匹配，正在重建集合: {error_msg}")
                drop_collection()
                _vector_store = Milvus(
                    embedding_function=embeddings,
                    collection_name=COLLECTION_NAME,
                    connection_args={"uri": MILVUS_URI},
                    auto_id=True,
                    enable_dynamic_field=True,
                    index_params={"metric_type": "COSINE", "index_type": "FLAT"},
                )
            else:
                raise
    return _vector_store


def create_collection():
    get_vector_store()


def has_collection() -> bool:
    from pymilvus import MilvusClient
    client = MilvusClient(uri=MILVUS_URI)
    return client.has_collection(collection_name=COLLECTION_NAME)


def get_or_create_collection():
    if not has_collection():
        create_collection()


def drop_collection():
    global _vector_store
    if has_collection():
        from pymilvus import MilvusClient
        client = MilvusClient(uri=MILVUS_URI)
        client.drop_collection(collection_name=COLLECTION_NAME)
        _vector_store = None


def insert_data(data: list) -> dict:
    vector_store = get_vector_store()
    documents = [
        {
            "text": item["text"],
            "source": item.get("source", ""),
            "category": item.get("category", ""),
            "type": item.get("type", ""),
            "md5": item.get("md5", compute_md5(item["text"])),
        }
        for item in data
    ]
    vector_store.add_texts(
        texts=[d["text"] for d in documents],
        metadatas=[{k: v for k, v in d.items() if k != "text"} for d in documents],
    )
    return {"insert_count": len(data)}


def get_existing_md5s() -> set:
    if not has_collection():
        return set()
    client = MilvusClient(uri=MILVUS_URI)
    results = client.query(
        collection_name=COLLECTION_NAME,
        filter="",
        output_fields=["md5"],
        limit=16384,
    )
    return {r["md5"] for r in results if "md5" in r}


def delete_by_md5(md5s: list) -> dict:
    if not md5s or not has_collection():
        return {"delete_count": 0}
    client = MilvusClient(uri=MILVUS_URI)
    filter_expr = " or ".join([f'md5 == "{m}"' for m in md5s])
    result = client.delete(
        collection_name=COLLECTION_NAME,
        filter=filter_expr,
    )
    return {"delete_count": result.get("delete_count", 0)}


def search(query_embedding: list, top_k: int = 5) -> list:
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_score_by_vector(
        embedding=query_embedding,
        k=top_k,
    )
    formatted_results = []
    for doc, score in results:
        formatted_results.append({
            "entity": {
                "text": doc.page_content,
                "source": doc.metadata.get("source", ""),
                "category": doc.metadata.get("category", ""),
                "type": doc.metadata.get("type", ""),
                "md5": doc.metadata.get("md5", ""),
            },
            "distance": score,
        })
    return formatted_results


def get_collection_stats() -> dict:
    if not has_collection():
        return {"exists": False, "row_count": 0, "total_vectors": 0}
    from pymilvus import MilvusClient
    client = MilvusClient(uri=MILVUS_URI)
    stats = client.get_collection_stats(collection_name=COLLECTION_NAME)
    row_count = stats.get("row_count", 0)
    return {"exists": True, "row_count": row_count, "total_vectors": row_count}


def close_milvus():
    global _vector_store
    _vector_store = None
