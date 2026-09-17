import hashlib
from pathlib import Path
from collections import defaultdict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.settings import DISHES_ROOT, TIPS_ROOT
from app.core.vector_db import (
    get_or_create_collection,
    insert_data,
    search,
    get_collection_stats,
    drop_collection,
    get_existing_md5s,
    compute_md5,
)
from app.ai.embeddings import encode_query

DISHES_CATEGORY_MAP = {
    "aquatic": "水产",
    "breakfast": "早餐",
    "condiment": "调味品",
    "dessert": "甜品",
    "drink": "饮品",
    "meat_dish": "荤菜",
    "semi-finished": "半成品",
    "soup": "汤品",
    "staple": "主食",
    "vegetable_dish": "素菜",
}

TIPS_CATEGORY_MAP = {
    "advanced": "高级技巧",
    "learn": "学习技巧",
}


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n## ",
            "\n### ",
            "\n#### ",
            "\n\n",
            "\n",
            "。",
            "！",
            "？",
            ".",
            "!",
            "?",
            "；",
            ";",
            "，",
            ",",
            " ",
            "",
        ],
        length_function=len,
        is_separator_regex=False,
    )
    return splitter.split_text(text)


def read_dishes_files() -> list:
    chunks = []
    dishes_path = Path(DISHES_ROOT)

    if not dishes_path.exists():
        return chunks

    for category_dir in dishes_path.iterdir():
        if not category_dir.is_dir():
            continue

        category_name = DISHES_CATEGORY_MAP.get(category_dir.name, category_dir.name)

        for item in category_dir.iterdir():
            if item.is_file() and item.suffix == ".md":
                text = item.read_text(encoding="utf-8").strip()
                if not text:
                    continue

                sub_chunks = split_text(text, chunk_size=500, chunk_overlap=50)
                for chunk_text in sub_chunks:
                    chunks.append({
                        "text": chunk_text,
                        "source": f"{category_dir.name}/{item.name}",
                        "category": category_name,
                        "type": "菜品",
                    })

            elif item.is_dir():
                md_files = list(item.glob("*.md"))
                for md_file in md_files:
                    text = md_file.read_text(encoding="utf-8").strip()
                    if not text:
                        continue

                    sub_chunks = split_text(text, chunk_size=500, chunk_overlap=50)
                    for chunk_text in sub_chunks:
                        chunks.append({
                            "text": chunk_text,
                            "source": f"{category_dir.name}/{item.name}/{md_file.name}",
                            "category": category_name,
                            "type": "菜品",
                        })

    return chunks


def read_tips_files() -> list:
    chunks = []
    tips_path = Path(TIPS_ROOT)

    if not tips_path.exists():
        return chunks

    for item in tips_path.iterdir():
        if item.is_file() and item.suffix == ".md":
            text = item.read_text(encoding="utf-8").strip()
            if not text:
                continue

            sub_chunks = split_text(text, chunk_size=500, chunk_overlap=50)
            for chunk_text in sub_chunks:
                chunks.append({
                    "text": chunk_text,
                    "source": item.name,
                    "category": "通用技巧",
                    "type": "技巧",
                })

        elif item.is_dir():
            category_name = TIPS_CATEGORY_MAP.get(item.name, item.name)

            for md_file in item.rglob("*.md"):
                text = md_file.read_text(encoding="utf-8").strip()
                if not text:
                    continue

                sub_chunks = split_text(text, chunk_size=500, chunk_overlap=50)
                for chunk_text in sub_chunks:
                    chunks.append({
                        "text": chunk_text,
                        "source": f"{item.name}/{md_file.name}",
                        "category": category_name,
                        "type": "技巧",
                    })

    return chunks


def read_all_files() -> list:
    dishes_chunks = read_dishes_files()
    tips_chunks = read_tips_files()
    return dishes_chunks + tips_chunks


def import_knowledge(full_reload: bool = False) -> dict:
    chunks = read_all_files()

    if not chunks:
        return {"status": "empty", "message": "没有找到知识库文件", "count": 0}

    for chunk in chunks:
        chunk["md5"] = compute_md5(chunk["text"])

    if full_reload:
        drop_collection()
        get_or_create_collection()
        new_chunks = chunks
        skipped = 0
    else:
        get_or_create_collection()
        existing_md5s = get_existing_md5s()
        new_chunks = [c for c in chunks if c["md5"] not in existing_md5s]
        skipped = len(chunks) - len(new_chunks)

    if not new_chunks:
        return {
            "status": "success",
            "count": len(chunks),
            "insert_count": 0,
            "skipped_count": skipped,
            "message": "所有内容均已存在，无需导入",
        }

    data = [
        {
            "text": c["text"],
            "source": c["source"],
            "category": c["category"],
            "type": c["type"],
            "md5": c["md5"],
        }
        for c in new_chunks
    ]

    result = insert_data(data)

    all_category_stats = defaultdict(int)
    all_type_stats = defaultdict(int)
    for c in chunks:
        all_category_stats[c["category"]] += 1
        all_type_stats[c["type"]] += 1

    new_category_stats = defaultdict(int)
    for c in new_chunks:
        new_category_stats[c["category"]] += 1

    return {
        "status": "success",
        "count": len(chunks),
        "insert_count": len(new_chunks),
        "skipped_count": skipped,
        "category_stats": dict(all_category_stats),
        "new_category_stats": dict(new_category_stats),
        "type_stats": dict(all_type_stats),
    }


def search_knowledge(query: str, top_k: int = 5, category: str = None, type_: str = None) -> list:
    query_embedding = encode_query(query)

    results = search(query_embedding, top_k=top_k * 2)

    formatted_results = []
    for hit in results:
        entity = hit.get("entity", {})
        result_category = entity.get("category", "")
        result_type = entity.get("type", "")

        if category and result_category != category:
            continue
        if type_ and result_type != type_:
            continue

        formatted_results.append({
            "text": entity.get("text", ""),
            "source": entity.get("source", ""),
            "category": result_category,
            "type": result_type,
            "distance": hit.get("distance", 0),
        })

        if len(formatted_results) >= top_k:
            break

    return formatted_results


def get_stats() -> dict:
    return get_collection_stats()
