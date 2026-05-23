"""
Standalone Data Fetch Script
Chạy bởi GitHub Actions để tự động cập nhật dữ liệu văn bản pháp luật.
Usage: python scripts/fetch_data.py
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path so we can import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.scraper import scrape_all_sources
from utils.data_manager import load_documents, save_documents, merge_documents, clean_documents

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("fetch_data")


def main():
    """Main fetch data pipeline."""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("BẮT ĐẦU CẬP NHẬT DỮ LIỆU VĂN BẢN PHÁP LUẬT")
    logger.info(f"Thời gian: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Step 1: Load existing data
    logger.info("\n📂 Bước 1: Đọc dữ liệu hiện có...")
    existing_data = load_documents()
    existing_docs = existing_data.get("documents", [])
    logger.info(f"   → Số văn bản hiện có: {len(existing_docs)}")

    # Step 2: Scrape new data from all sources
    logger.info("\n🌐 Bước 2: Thu thập dữ liệu mới từ Internet...")
    try:
        new_docs = scrape_all_sources(max_pages=3)
        logger.info(f"   → Số văn bản thu thập được: {len(new_docs)}")
    except Exception as e:
        logger.error(f"   ❌ Lỗi khi thu thập dữ liệu: {e}")
        new_docs = []

    # Step 3: Merge and deduplicate
    if new_docs:
        logger.info("\n🔄 Bước 3: Gộp và loại bỏ trùng lặp...")
        merged_docs = merge_documents(existing_docs, new_docs)
        logger.info(f"   → Số văn bản sau khi gộp: {len(merged_docs)}")
    else:
        logger.info("\n⚠️ Bước 3: Không có dữ liệu mới, giữ nguyên dữ liệu hiện có")
        merged_docs = existing_docs

    # Step 4: Clean and validate
    logger.info("\n🧹 Bước 4: Làm sạch và xác thực dữ liệu...")
    cleaned_docs = clean_documents(merged_docs)
    logger.info(f"   → Số văn bản sau khi làm sạch: {len(cleaned_docs)}")

    # Step 5: Save
    logger.info("\n💾 Bước 5: Lưu dữ liệu...")
    updated_data = {
        "last_updated": datetime.now().isoformat(),
        "total_documents": len(cleaned_docs),
        "sources": list(set(d.get("nguon", "") for d in cleaned_docs if d.get("nguon"))),
        "documents": cleaned_docs,
    }

    success = save_documents(updated_data)
    if success:
        logger.info("   → ✅ Lưu dữ liệu thành công!")
    else:
        logger.error("   → ❌ Lỗi khi lưu dữ liệu!")
        sys.exit(1)

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info("\n" + "=" * 60)
    logger.info("📊 TÓM TẮT KẾT QUẢ")
    logger.info("=" * 60)
    logger.info(f"   Tổng văn bản:        {len(cleaned_docs)}")
    logger.info(f"   Văn bản mới crawl:   {len(new_docs)}")
    logger.info(f"   Nguồn dữ liệu:      {', '.join(updated_data['sources'])}")
    logger.info(f"   Thời gian chạy:      {duration:.1f} giây")
    logger.info(f"   Trạng thái:          ✅ THÀNH CÔNG")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
