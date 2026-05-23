"""
Data Manager Module - Quản lý dữ liệu văn bản pháp luật
Load, save, merge, deduplicate, validate documents
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Path to data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DOCUMENTS_FILE = DATA_DIR / "documents.json"


def ensure_data_dir():
    """Ensure data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_documents() -> Dict:
    """
    Load documents from JSON file.
    Returns dict with metadata and documents list.
    """
    ensure_data_dir()

    if not DOCUMENTS_FILE.exists():
        logger.warning(f"Documents file not found: {DOCUMENTS_FILE}")
        return {
            "last_updated": datetime.now().isoformat(),
            "total_documents": 0,
            "sources": [],
            "documents": [],
        }

    try:
        with open(DOCUMENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate structure
        if "documents" not in data:
            data["documents"] = []
        if "last_updated" not in data:
            data["last_updated"] = datetime.now().isoformat()
        if "total_documents" not in data:
            data["total_documents"] = len(data["documents"])
        if "sources" not in data:
            data["sources"] = list(set(d.get("nguon", "") for d in data["documents"]))

        logger.info(f"Loaded {len(data['documents'])} documents")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {
            "last_updated": datetime.now().isoformat(),
            "total_documents": 0,
            "sources": [],
            "documents": [],
        }
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        return {
            "last_updated": datetime.now().isoformat(),
            "total_documents": 0,
            "sources": [],
            "documents": [],
        }


def save_documents(data: Dict) -> bool:
    """Save documents to JSON file."""
    ensure_data_dir()

    try:
        # Update metadata
        data["last_updated"] = datetime.now().isoformat()
        data["total_documents"] = len(data.get("documents", []))
        data["sources"] = list(set(
            d.get("nguon", "") for d in data.get("documents", []) if d.get("nguon")
        ))

        with open(DOCUMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {data['total_documents']} documents")
        return True

    except Exception as e:
        logger.error(f"Error saving documents: {e}")
        return False


def merge_documents(existing: List[Dict], new_docs: List[Dict]) -> List[Dict]:
    """
    Merge new documents into existing list, deduplicating by ID and so_hieu.
    New documents take priority over existing ones.
    """
    # Build lookup maps
    id_map = {}
    so_hieu_map = {}

    for doc in existing:
        doc_id = doc.get("id", "")
        so_hieu = doc.get("so_hieu", "")
        if doc_id:
            id_map[doc_id] = doc
        if so_hieu:
            so_hieu_map[so_hieu] = doc

    # Merge new documents (overwrite existing)
    added = 0
    updated = 0

    for doc in new_docs:
        doc_id = doc.get("id", "")
        so_hieu = doc.get("so_hieu", "")

        if doc_id and doc_id in id_map:
            # Update existing document
            id_map[doc_id].update(doc)
            updated += 1
        elif so_hieu and so_hieu in so_hieu_map:
            # Update by so_hieu match
            so_hieu_map[so_hieu].update(doc)
            updated += 1
        else:
            # Add new document
            id_map[doc_id if doc_id else f"new_{added}"] = doc
            if so_hieu:
                so_hieu_map[so_hieu] = doc
            added += 1

    logger.info(f"Merge result: {added} added, {updated} updated")
    return list(id_map.values())


def validate_document(doc: Dict) -> bool:
    """Validate a document has required fields."""
    required_fields = ["tieu_de", "loai_van_ban"]
    return all(doc.get(field) for field in required_fields)


def clean_documents(documents: List[Dict]) -> List[Dict]:
    """Clean and normalize documents."""
    cleaned = []
    for doc in documents:
        if not validate_document(doc):
            continue

        # Ensure all fields exist with defaults
        clean_doc = {
            "id": doc.get("id", ""),
            "so_hieu": doc.get("so_hieu", "N/A"),
            "tieu_de": doc.get("tieu_de", "").strip(),
            "loai_van_ban": doc.get("loai_van_ban", "Công văn"),
            "co_quan_ban_hanh": doc.get("co_quan_ban_hanh", "N/A"),
            "ngay_ban_hanh": doc.get("ngay_ban_hanh", ""),
            "ngay_hieu_luc": doc.get("ngay_hieu_luc", ""),
            "trang_thai": doc.get("trang_thai", "Còn hiệu lực"),
            "linh_vuc": doc.get("linh_vuc", "Hải quan"),
            "tom_tat": doc.get("tom_tat", ""),
            "url": doc.get("url", ""),
            "nguon": doc.get("nguon", ""),
            "tags": doc.get("tags", []),
        }

        cleaned.append(clean_doc)

    # Sort by date (newest first)
    cleaned.sort(key=lambda x: x.get("ngay_ban_hanh", ""), reverse=True)

    return cleaned


def get_statistics(documents: List[Dict]) -> Dict:
    """Calculate statistics from documents."""
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - __import__("datetime").timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now() - __import__("datetime").timedelta(days=30)).strftime("%Y-%m-%d")

    stats = {
        "total": len(documents),
        "today": sum(1 for d in documents if d.get("ngay_ban_hanh", "") == today),
        "this_week": sum(1 for d in documents if d.get("ngay_ban_hanh", "") >= week_ago),
        "this_month": sum(1 for d in documents if d.get("ngay_ban_hanh", "") >= month_ago),
        "by_type": {},
        "by_category": {},
        "by_status": {},
        "by_source": {},
        "by_authority": {},
        "by_month": {},
    }

    for doc in documents:
        # By type
        doc_type = doc.get("loai_van_ban", "Khác")
        stats["by_type"][doc_type] = stats["by_type"].get(doc_type, 0) + 1

        # By category
        category = doc.get("linh_vuc", "Khác")
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        # By status
        status = doc.get("trang_thai", "Không rõ")
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        # By source
        source = doc.get("nguon", "Khác")
        stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

        # By authority
        authority = doc.get("co_quan_ban_hanh", "Khác")
        stats["by_authority"][authority] = stats["by_authority"].get(authority, 0) + 1

        # By month
        date = doc.get("ngay_ban_hanh", "")
        if len(date) >= 7:
            month_key = date[:7]  # YYYY-MM
            stats["by_month"][month_key] = stats["by_month"].get(month_key, 0) + 1

    return stats


# =============================================
# INCOTERMS DATA
# =============================================

INCOTERMS_2020 = [
    {
        "code": "EXW",
        "name": "Ex Works",
        "name_vi": "Giao tại xưởng",
        "group": "E",
        "description": "Người bán giao hàng khi đặt hàng hóa dưới quyền định đoạt của người mua tại cơ sở của người bán.",
        "seller_responsibility": "Đóng gói, đặt hàng tại xưởng",
        "buyer_responsibility": "Vận chuyển, bảo hiểm, thông quan XK/NK, mọi chi phí",
        "risk_transfer": "Tại xưởng người bán",
        "transport": "Mọi phương thức",
    },
    {
        "code": "FCA",
        "name": "Free Carrier",
        "name_vi": "Giao cho người chuyên chở",
        "group": "F",
        "description": "Người bán giao hàng cho người chuyên chở do người mua chỉ định tại địa điểm quy định.",
        "seller_responsibility": "Thông quan XK, giao cho carrier",
        "buyer_responsibility": "Vận chuyển chính, bảo hiểm, thông quan NK",
        "risk_transfer": "Khi giao cho carrier",
        "transport": "Mọi phương thức",
    },
    {
        "code": "CPT",
        "name": "Carriage Paid To",
        "name_vi": "Cước phí trả tới",
        "group": "C",
        "description": "Người bán trả cước vận chuyển đến nơi đến quy định, nhưng rủi ro chuyển khi giao cho carrier đầu tiên.",
        "seller_responsibility": "Thông quan XK, cước vận chuyển",
        "buyer_responsibility": "Bảo hiểm, thông quan NK, rủi ro từ khi giao carrier",
        "risk_transfer": "Khi giao cho carrier đầu tiên",
        "transport": "Mọi phương thức",
    },
    {
        "code": "CIP",
        "name": "Carriage and Insurance Paid To",
        "name_vi": "Cước phí và bảo hiểm trả tới",
        "group": "C",
        "description": "Như CPT nhưng người bán phải mua bảo hiểm hàng hóa (mức bảo hiểm tối đa theo ICC clause A).",
        "seller_responsibility": "Thông quan XK, cước vận chuyển, bảo hiểm (ICC A)",
        "buyer_responsibility": "Thông quan NK, rủi ro từ khi giao carrier",
        "risk_transfer": "Khi giao cho carrier đầu tiên",
        "transport": "Mọi phương thức",
    },
    {
        "code": "DAP",
        "name": "Delivered at Place",
        "name_vi": "Giao tại nơi đến",
        "group": "D",
        "description": "Người bán giao hàng khi đặt dưới quyền định đoạt người mua trên phương tiện vận tải tại nơi đến, sẵn sàng dỡ hàng.",
        "seller_responsibility": "Vận chuyển đến nơi đến, thông quan XK",
        "buyer_responsibility": "Dỡ hàng, thông quan NK, thuế NK",
        "risk_transfer": "Tại nơi đến (trước khi dỡ)",
        "transport": "Mọi phương thức",
    },
    {
        "code": "DPU",
        "name": "Delivered at Place Unloaded",
        "name_vi": "Giao tại nơi đến đã dỡ hàng",
        "group": "D",
        "description": "Người bán giao hàng khi đã dỡ khỏi phương tiện vận tải tại nơi đến quy định.",
        "seller_responsibility": "Vận chuyển, dỡ hàng tại nơi đến, thông quan XK",
        "buyer_responsibility": "Thông quan NK, thuế NK",
        "risk_transfer": "Tại nơi đến (sau khi dỡ)",
        "transport": "Mọi phương thức",
    },
    {
        "code": "DDP",
        "name": "Delivered Duty Paid",
        "name_vi": "Giao hàng đã nộp thuế",
        "group": "D",
        "description": "Người bán chịu mọi chi phí và rủi ro cho đến khi giao hàng tại nơi đến, bao gồm thông quan NK và thuế NK.",
        "seller_responsibility": "Mọi chi phí, thông quan XK+NK, thuế NK",
        "buyer_responsibility": "Dỡ hàng",
        "risk_transfer": "Tại nơi đến",
        "transport": "Mọi phương thức",
    },
    {
        "code": "FAS",
        "name": "Free Alongside Ship",
        "name_vi": "Giao dọc mạn tàu",
        "group": "F",
        "description": "Người bán giao hàng khi đặt dọc mạn tàu do người mua chỉ định tại cảng xếp hàng.",
        "seller_responsibility": "Thông quan XK, vận chuyển đến cảng",
        "buyer_responsibility": "Xếp hàng lên tàu, cước biển, bảo hiểm, thông quan NK",
        "risk_transfer": "Dọc mạn tàu tại cảng xếp",
        "transport": "Đường biển / thủy nội địa",
    },
    {
        "code": "FOB",
        "name": "Free On Board",
        "name_vi": "Giao lên tàu",
        "group": "F",
        "description": "Người bán giao hàng khi hàng đã xếp lên tàu do người mua chỉ định tại cảng xếp hàng.",
        "seller_responsibility": "Thông quan XK, xếp hàng lên tàu",
        "buyer_responsibility": "Cước biển, bảo hiểm, thông quan NK",
        "risk_transfer": "Khi hàng qua lan can tàu",
        "transport": "Đường biển / thủy nội địa",
    },
    {
        "code": "CFR",
        "name": "Cost and Freight",
        "name_vi": "Tiền hàng và cước phí",
        "group": "C",
        "description": "Người bán trả cước vận chuyển đường biển đến cảng đến, nhưng rủi ro chuyển khi hàng lên tàu tại cảng xếp.",
        "seller_responsibility": "Thông quan XK, cước biển",
        "buyer_responsibility": "Bảo hiểm, thông quan NK, rủi ro từ cảng xếp",
        "risk_transfer": "Khi hàng lên tàu tại cảng xếp",
        "transport": "Đường biển / thủy nội địa",
    },
    {
        "code": "CIF",
        "name": "Cost, Insurance and Freight",
        "name_vi": "Tiền hàng, bảo hiểm và cước phí",
        "group": "C",
        "description": "Như CFR nhưng người bán phải mua bảo hiểm hàng hóa (tối thiểu ICC clause C).",
        "seller_responsibility": "Thông quan XK, cước biển, bảo hiểm (ICC C tối thiểu)",
        "buyer_responsibility": "Thông quan NK, rủi ro từ cảng xếp",
        "risk_transfer": "Khi hàng lên tàu tại cảng xếp",
        "transport": "Đường biển / thủy nội địa",
    },
]


def get_incoterms() -> List[Dict]:
    """Return Incoterms 2020 data."""
    return INCOTERMS_2020
