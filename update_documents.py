import os
import json
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import re

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cấu hình đường dẫn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'legal-documents.json')

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_id(number):
    """Tạo ID tự động từ số hiệu văn bản"""
    return unidecode(number.lower().replace('/', '-').replace(' ', '-'))

def unidecode(text):
    import unicodedata
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

def detect_type(title, number):
    title_lower = title.lower()
    if 'thông tư' in title_lower: return 'thong-tu', 'Thông tư'
    if 'nghị định' in title_lower: return 'nghi-dinh', 'Nghị định'
    if 'nghị quyết' in title_lower: return 'nghi-quyet', 'Nghị quyết'
    if 'luật' in title_lower: return 'luat', 'Luật'
    if 'quyết định' in title_lower: return 'quyet-dinh', 'Quyết định'
    return 'cong-van', 'Công văn'

from utils.scraper import scrape_all_sources

def scrape_mof():
    """Thu thập văn bản mới từ các nguồn thực tế (Hải quan, Thư viện pháp luật, VBPL)"""
    logging.info("Đang kết nối để cào dữ liệu từ các trang web chính phủ...")
    try:
        raw_docs = scrape_all_sources(max_pages=1)
    except Exception as e:
        logging.error(f"Lỗi khi cào dữ liệu: {e}")
        return []
        
    new_docs = []
    for d in raw_docs:
        # Chuyển đổi định dạng dữ liệu (Schema mapping)
        doc = {
            "id": d["id"],
            "type": d["loai_van_ban"].lower().replace(' ', '-'),
            "typeName": d["loai_van_ban"],
            "number": d.get("so_hieu", "N/A"),
            "title": d["tieu_de"],
            "issueDate": d.get("ngay_ban_hanh", datetime.now().strftime("%Y-%m-%d")),
            "effectiveDate": d.get("ngay_hieu_luc", datetime.now().strftime("%Y-%m-%d")),
            "issuingBody": d.get("co_quan_ban_hanh", "Chính phủ"),
            "summary": d.get("tom_tat", ""),
            "purpose": f"Nguồn gốc tự động: {d.get('nguon', 'Internet')}",
            "keyPoints": ["Văn bản tự động cập nhật từ Internet", "Sử dụng cho tra cứu cơ bản"],
            "articles": [],
            "content": f"VĂN BẢN ĐƯỢC CẬP NHẬT TỰ ĐỘNG\n\nNguồn: {d.get('nguon', 'Internet')}\nLink gốc: {d.get('url', '')}\n\n[TÓM TẮT NỘI DUNG]:\n{d.get('tom_tat', d['tieu_de'])}\n\n(Để đọc toàn văn chi tiết, vui lòng truy cập đường link đính kèm).",
            "status": "active" if d.get("trang_thai") == "Còn hiệu lực" else "expired",
            "folder": "Z",
            "tags": d.get("tags", []),
            "relatedDocs": []
        }
        new_docs.append(doc)
        
    logging.info(f"Đã chuyển đổi thành công {len(new_docs)} văn bản thực tế.")
    return new_docs

def update_status_old_documents(data):
    """
    Cập nhật trạng thái các văn bản cũ (Không xóa).
    Nếu văn bản đã bị thay thế, chuyển status thành 'expired'
    """
    logging.info("Đang kiểm tra tình trạng hiệu lực của các văn bản cũ...")
    changed = False
    current_year = datetime.now().year
    
    for doc in data:
        # Ví dụ logic: Đánh dấu các văn bản từ trước năm 2015 thành hết hiệu lực (chỉ là giả lập logic)
        # Thực tế sẽ cần API của VBPL để check status chính xác.
        if doc.get('status') == 'active':
            try:
                issue_year = int(doc.get('issueDate', '2000-01-01').split('-')[0])
                if issue_year < 2015:  
                    # doc['status'] = 'expired'
                    # changed = True
                    pass
            except:
                pass
                
    return changed

def main():
    logging.info(f"BẮT ĐẦU CẬP NHẬT DỮ LIỆU - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Đọc dữ liệu cũ
    data = load_data()
    existing_ids = {doc['id'] for doc in data if 'id' in doc}
    
    # 2. Cào văn bản mới
    new_documents = scrape_mof()
    
    # 3. Lọc trùng lặp và thêm vào kho
    added_count = 0
    for doc in new_documents:
        if doc['id'] not in existing_ids:
            data.insert(0, doc) # Thêm lên đầu danh sách
            existing_ids.add(doc['id'])
            added_count += 1
            logging.info(f"Đã thêm văn bản mới: {doc['title']}")
            
    # 4. Kiểm tra và cập nhật trạng thái văn bản cũ (Lưu lại, không xóa)
    status_changed = update_status_old_documents(data)
    
    # 5. Lưu file
    if added_count > 0 or status_changed:
        save_data(data)
        logging.info(f"Đã lưu file JSON. Thêm mới: {added_count} văn bản.")
    else:
        logging.info("Không có văn bản nào mới trong ngày hôm nay.")
        
    logging.info("HOÀN THÀNH QUÁ TRÌNH CẬP NHẬT.")

if __name__ == "__main__":
    main()
