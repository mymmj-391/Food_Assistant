import sys
import os
from pathlib import Path
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载 .env 文件（必须在导入其他模块之前）
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)
    print("已加载环境配置: .env")
else:
    print("警告: 未找到 .env，使用系统环境变量")

from app.ai.knowledge import import_knowledge, get_stats
from app.core.settings import EMBEDDING_MODEL


def main():
    parser = argparse.ArgumentParser(description="导入知识库到 Milvus 向量数据库")
    parser.add_argument(
        "--full-reload",
        action="store_true",
        help="全量重建：删除旧数据后重新导入（默认增量导入，跳过已存在内容）",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("开始导入知识库到 Milvus 向量数据库")
    print(f"当前环境: {os.getenv('ENV', 'production')}")
    print(f"导入模式: {'全量重建' if args.full_reload else '增量导入（MD5去重）'}")
    print("=" * 50)
    print(f"\n嵌入模型: {EMBEDDING_MODEL}")
    print("使用硅基流动 API 进行向量化...")

    print("\n正在读取知识库文件...")
    result = import_knowledge(full_reload=args.full_reload)

    if result["status"] == "empty":
        print(f"提示: {result['message']}")
        return

    print(f"\n导入完成!")
    print(f"  - 文档块总数: {result['count']}")
    print(f"  - 成功插入: {result['insert_count']}")
    print(f"  - 跳过重复: {result.get('skipped_count', 0)}")

    if result.get("message"):
        print(f"  - 提示: {result['message']}")

    if result.get("new_category_stats"):
        print(f"\n新增内容按分类统计:")
        for cat_name, count in sorted(result["new_category_stats"].items(), key=lambda x: -x[1]):
            print(f"  - {cat_name}: {count} 条")

    if result.get("type_stats"):
        print(f"\n按类型统计:")
        for type_name, count in result["type_stats"].items():
            print(f"  - {type_name}: {count} 条")

    if result.get("category_stats"):
        print(f"\n按分类统计:")
        for cat_name, count in sorted(result["category_stats"].items(), key=lambda x: -x[1]):
            print(f"  - {cat_name}: {count} 条")

    stats = get_stats()
    print(f"\n向量数据库状态:")
    print(f"  - 集合存在: {stats['exists']}")
    print(f"  - 总记录数: {stats['row_count']}")


if __name__ == "__main__":
    main()
