from pathlib import Path
from app.core.settings import DISHES_ROOT, TIPS_ROOT, BASE_URL

CATEGORY_MAP = {
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

def get_category_list() -> list:
    categories = []
    dishes_path = Path(DISHES_ROOT)

    if not dishes_path.exists():
        return categories

    for item in sorted(dishes_path.iterdir()):
        if item.is_dir():
            category_id = item.name
            category_name = CATEGORY_MAP.get(category_id, category_id)
            categories.append({
                "id": category_id,
                "name": category_name,
            })

    return categories


def get_dish_list(category_id: str) -> list:
    dishes = []
    category_path = Path(DISHES_ROOT) / category_id

    if not category_path.exists():
        return dishes

    for item in sorted(category_path.iterdir()):
        if item.is_file() and item.suffix == ".md":
            name = item.stem
            content = item.read_text(encoding="utf-8").strip()
            summary = content[:100] if content else ""
            dishes.append({
                "id": name,
                "name": name,
                "summary": summary,
                "type": "file",
                "image": None,
            })
        elif item.is_dir():
            name = item.name
            md_files = sorted(item.glob("*.md"))
            if md_files:
                content = md_files[0].read_text(encoding="utf-8").strip()
                summary = content[:100] if content else ""
            else:
                summary = ""
            # 查找第一张图片作为封面
            image = None
            for img_file in sorted(item.iterdir()):
                if img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
                    image = f"{BASE_URL}/dishes/image/{category_id}/{name}/{img_file.name}"
                    break
            dishes.append({
                "id": name,
                "name": name,
                "summary": summary,
                "type": "folder",
                "image": image,
            })

    return dishes


def get_dish_detail(category_id: str, dish_name: str) -> dict | None:
    category_path = Path(DISHES_ROOT) / category_id

    if not category_path.exists():
        return None

    md_file = category_path / f"{dish_name}.md"
    if md_file.exists():
        content = md_file.read_text(encoding="utf-8").strip()
        return {"name": dish_name, "content": content}

    dish_dir = category_path / dish_name
    if dish_dir.exists() and dish_dir.is_dir():
        md_files = sorted(dish_dir.glob("*.md"))
        if md_files:
            content = md_files[0].read_text(encoding="utf-8").strip()
            return {"name": dish_name, "content": content}

    return None


def get_dish_images(category_id: str, dish_name: str) -> list:
    images = []
    category_path = Path(DISHES_ROOT) / category_id

    if not category_path.exists():
        return images

    dish_dir = category_path / dish_name
    if dish_dir.exists() and dish_dir.is_dir():
        for img_file in sorted(dish_dir.iterdir()):
            if img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
                images.append(f"{BASE_URL}/dishes/image/{category_id}/{dish_name}/{img_file.name}")

    return images


def get_tips_list() -> list:
    tips = []
    tips_path = Path(TIPS_ROOT)

    if not tips_path.exists():
        return tips

    for item in sorted(tips_path.iterdir()):
        if item.is_file() and item.suffix == ".md":
            name = item.stem
            content = item.read_text(encoding="utf-8").strip()
            summary = content[:100] if content else ""
            tips.append({
                "id": name,
                "name": name,
                "summary": summary,
                "type": "file",
            })
        elif item.is_dir():
            name = item.name
            md_files = sorted(item.glob("*.md"))
            if md_files:
                content = md_files[0].read_text(encoding="utf-8").strip()
                summary = content[:100] if content else ""
            else:
                summary = ""
            tips.append({
                "id": name,
                "name": name,
                "summary": summary,
                "type": "folder",
            })

    return tips


def get_tip_detail(tip_name: str) -> dict | None:
    tips_path = Path(TIPS_ROOT)

    if not tips_path.exists():
        return None

    md_file = tips_path / f"{tip_name}.md"
    if md_file.exists():
        content = md_file.read_text(encoding="utf-8").strip()
        return {"name": tip_name, "content": content}

    tip_dir = tips_path / tip_name
    if tip_dir.exists() and tip_dir.is_dir():
        md_files = sorted(tip_dir.glob("*.md"))
        if md_files:
            content = md_files[0].read_text(encoding="utf-8").strip()
            return {"name": tip_name, "content": content}

    # 在子目录中递归查找同名 .md 文件
    for sub_file in tips_path.rglob(f"{tip_name}.md"):
        content = sub_file.read_text(encoding="utf-8").strip()
        return {"name": tip_name, "content": content}

    return None
