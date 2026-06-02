"""
CỔNG PHÁP LUẬT HẢI QUAN VIỆT NAM
Tra cứu Thông tư - Nghị định - Nghị quyết - Luật - Công văn - Quyết định
URL: tinnam888888_haiquan.streamlit.app
"""

import streamlit as st
import json
import os
import re
from datetime import datetime, timedelta, timezone

def get_vn_time():
    return datetime.now(timezone.utc) + timedelta(hours=7)

from pathlib import Path
from unidecode import unidecode
from thefuzz import fuzz
import requests
from bs4 import BeautifulSoup
import feedparser
import google.generativeai as genai
import time
from uuid import uuid4
import pandas as pd
# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Cổng Pháp Luật Hải Quan Việt Nam - Tra cứu Thông tư, Nghị định, Luật XNK",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "## ⚖️ Cổng Pháp Luật Hải Quan Việt Nam\n"
                 "Hệ thống tra cứu văn bản pháp luật về Hải quan & Xuất nhập khẩu.\n\n"
                 "**Liên hệ:** tinnam888888_haiquan.streamlit.app"
    }
)

# ============================================
# BẢO MẬT - KIỂM TRA MẬT KHẨU NGAY TỪ ĐẦU
# ============================================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <style>
    .block-container { max-width: 500px !important; margin: auto; }
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif !important; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; padding: 60px 20px 20px;'>
        <div style='font-size: 4rem;'>🔐</div>
        <h2 style='color: #e2e8f0; margin-top: 1rem;'>CỔNG PHÁP LUẬT HẢI QUAN</h2>
        <p style='color: #94a3b8;'>Nhập mật khẩu để truy cập hệ thống</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        password = st.text_input("🔑 Mật khẩu", type="password", placeholder="Nhập mật khẩu...", key="login_pw")
        login_btn = st.button("🚀 Đăng nhập", use_container_width=True, type="primary")
        
        if login_btn:
            if password == "1991":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Sai mật khẩu! Vui lòng thử lại.")
    
    st.stop()

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
/* ===== GLOBAL ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.block-container {
    padding-top: 1rem !important;
    max-width: 1400px !important;
}

/* ===== HEADER ===== */
.main-header {
    text-align: center;
    padding: 1.5rem 1rem;
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 30%, #4338ca 60%, #6366f1 100%);
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.3);
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(255,255,255,0.05) 0%, transparent 70%);
    animation: shimmer 8s ease-in-out infinite;
}
@keyframes shimmer {
    0%, 100% { transform: translateX(-30%) translateY(-30%); }
    50% { transform: translateX(30%) translateY(30%); }
}
.main-header h1 {
    color: #fff !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    position: relative;
    z-index: 1;
}
.main-header p {
    color: #c7d2fe !important;
    font-size: 0.95rem !important;
    margin-top: 0.5rem !important;
    position: relative;
    z-index: 1;
}

/* ===== SEARCH HIGHLIGHT (BÔI ĐỎ) ===== */
.search-match {
    background-color: #ef4444 !important;
    color: #fff !important;
    padding: 1px 4px;
    border-radius: 3px;
    font-weight: 600;
}

/* ===== STAT CARDS ===== */
.stat-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
}
.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.2);
    border-color: #6366f1;
}
.stat-number {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.stat-label {
    color: #94a3b8;
    font-size: 0.8rem;
    margin-top: 0.3rem;
    font-weight: 500;
}

/* ===== TYPE BADGES ===== */
.type-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.badge-thong-tu { background: rgba(59,130,246,0.15); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
.badge-nghi-dinh { background: rgba(16,185,129,0.15); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
.badge-nghi-quyet { background: rgba(139,92,246,0.15); color: #a78bfa; border: 1px solid rgba(139,92,246,0.3); }
.badge-luat { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
.badge-cong-van { background: rgba(249,115,22,0.15); color: #fb923c; border: 1px solid rgba(249,115,22,0.3); }
.badge-quyet-dinh { background: rgba(20,184,166,0.15); color: #2dd4bf; border: 1px solid rgba(20,184,166,0.3); }

/* ===== STATUS BADGES ===== */
.status-active { background: rgba(16,185,129,0.15); color: #34d399; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; }
.status-amended { background: rgba(245,158,11,0.15); color: #fbbf24; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; }
.status-expired { background: rgba(239,68,68,0.15); color: #f87171; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; }

/* ===== DOC CARDS ===== */
.doc-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.doc-card:hover {
    border-color: #6366f1;
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
    transform: translateY(-2px);
}
.doc-card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e2e8f0;
    margin: 0.5rem 0;
    line-height: 1.4;
}
.doc-card-number {
    color: #6366f1;
    font-weight: 700;
    font-size: 0.9rem;
}
.doc-card-meta {
    color: #94a3b8;
    font-size: 0.78rem;
    margin-top: 0.3rem;
}
.doc-card-summary {
    color: #cbd5e1;
    font-size: 0.82rem;
    margin-top: 0.5rem;
    line-height: 1.5;
}

/* ===== ANSWER PANEL ===== */
.answer-panel {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
    border: 2px solid #6366f1;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.2);
}
.answer-panel h3 {
    color: #a5b4fc !important;
    font-size: 1.1rem !important;
    margin-bottom: 1rem !important;
}
.answer-item {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    border-left: 3px solid #6366f1;
}
.answer-item-title {
    color: #c7d2fe;
    font-weight: 600;
    font-size: 0.9rem;
}
.answer-item-content {
    color: #e2e8f0;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    line-height: 1.6;
}

/* ===== DETAIL SECTIONS ===== */
.detail-section {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}
.detail-section h4 {
    color: #a5b4fc !important;
    font-size: 0.95rem !important;
    margin-bottom: 0.8rem !important;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ===== ARTICLE EXPANDER ===== */
.article-item {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.5rem;
}
.article-title {
    color: #fbbf24;
    font-weight: 600;
    font-size: 0.9rem;
}
.article-content {
    color: #cbd5e1;
    font-size: 0.85rem;
    line-height: 1.6;
    margin-top: 0.5rem;
    white-space: pre-wrap;
}

/* ===== QUICK TAGS ===== */
.quick-tag {
    display: inline-block;
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.3);
    color: #a5b4fc;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    margin: 2px;
    cursor: pointer;
    transition: all 0.2s;
}
.quick-tag:hover {
    background: rgba(99, 102, 241, 0.3);
    color: #fff;
}

/* ===== FOOTER ===== */
.footer {
    text-align: center;
    padding: 2rem 1rem;
    color: #64748b;
    font-size: 0.8rem;
    border-top: 1px solid #1e293b;
    margin-top: 3rem;
}

/* ===== STREAMLIT OVERRIDES ===== */
.stTextInput > div > div > input {
    background-color: #1e293b !important;
    border: 2px solid #334155 !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 1rem !important;
    padding: 0.8rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
}
.stSelectbox > div > div {
    background-color: #1e293b !important;
    border-color: #334155 !important;
    border-radius: 10px !important;
}
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
}
div[data-testid="stExpander"] {
    background: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 16px;
}
/* ===== AI RESPONSE BOX ===== */
.ai-response-box {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid #6366f1;
    border-left: 6px solid #fbbf24;
    border-radius: 12px;
    padding: 1.8rem 2.2rem;
    font-size: 1.15rem;
    line-height: 1.8;
    color: #f8fafc;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    margin-top: 1rem;
    margin-bottom: 2rem;
}
.ai-response-box h1, .ai-response-box h2, .ai-response-box h3, .ai-response-box h4 {
    color: #818cf8 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1rem !important;
}
.ai-response-box mark {
    background-color: #ffd700 !important;
    color: #000000 !important;
    font-weight: 900 !important;
    padding: 2px 8px;
    border-radius: 6px;
}
.ai-response-box strong {
    color: #c7d2fe;
}
</style>
""", unsafe_allow_html=True)


# ============================================
# DATA LOADING
# ============================================
@st.cache_data(ttl=300)
def fetch_live_data(domain):
    """Tự động quét (crawl) các văn bản mới nhất từ các nguồn uy tín."""
    live_docs = []
    
    if domain == "Hải quan & Xuất nhập khẩu":
        sources = [
            ('LuatVietnam', 'https://luatvietnam.vn/tin-phap-luat.rss'),
            ('HaiQuanOnline', 'https://haiquanonline.com.vn/rss/hai-quan-c4.rss'),
            ('HaiQuanXNK', 'https://haiquanonline.com.vn/rss/xuat-nhap-khau-c5.rss'),
        ]
        keywords = ['hải quan', 'xuất nhập', 'thuế', 'nghị định', 'c/o', 'incoterm', 'biểu thuế', 'xuất xứ']
    else:
        sources = [
            ('LuatVietnam', 'https://luatvietnam.vn/tin-phap-luat.rss'),
            ('BaoPhapLuat', 'https://baophapluat.vn/rss/kinh-te-c3.rss'),
            ('TaiChinh', 'https://tapchitaichinh.vn/rss/ke-toan-kiem-toan.rss'),
        ]
        keywords = ['kế toán', 'thuế thu nhập', 'thuế tndn', 'thuế tncn', 'thuế gtgt', 'kiểm toán', 'hóa đơn', 'chứng từ', 'vas', 'chuẩn mực', 'nghị định', 'thông tư']
    
    for source_name, url in sources:
        try:
            # Thêm timeout 3 giây để tránh bị treo (hang) khi server từ chối IP nước ngoài
            resp = requests.get(url, timeout=3, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200:
                continue
            feed = feedparser.parse(resp.content)
            for entry in feed.entries[:30]:
                title_lower = entry.title.lower()
                desc_lower = getattr(entry, 'description', '').lower()
                
                # Lọc văn bản theo từ khóa
                if any(kw in title_lower or kw in desc_lower for kw in keywords):
                    # Lọc tìm số hiệu trong tiêu đề (VD: Nghị định 12/2024/NĐ-CP)
                    number_match = re.search(r'([0-9]+/[0-9]+/[A-ZĐ-]+)', entry.title)
                    doc_number = number_match.group(1) if number_match else "CẬP NHẬT MỚI"
                    
                    doc_type = "cong-van"
                    if 'thông tư' in title_lower: doc_type = "thong-tu"
                    elif 'nghị định' in title_lower: doc_type = "nghi-dinh"
                    elif 'quyết định' in title_lower: doc_type = "quyet-dinh"
                    elif 'nghị quyết' in title_lower: doc_type = "nghi-quyet"
                    elif 'luật' in title_lower: doc_type = "luat"

                    live_docs.append({
                        "id": f"live-{source_name}-{len(live_docs)}",
                        "type": doc_type,
                        "number": doc_number,
                        "title": entry.title,
                        "summary": getattr(entry, 'description', 'Cập nhật tự động từ nguồn ' + source_name),
                        "issueDate": get_vn_time().strftime('%Y-%m-%d'),
                        "effectiveDate": "Đang cập nhật",
                        "issuingBody": f"Nguồn: {source_name}",
                        "status": "active",
                        "purpose": "Cập nhật dữ liệu thời gian thực thông qua Crawler.",
                        "keyPoints": [f"Xem nội dung chi tiết tại bản gốc: {entry.link}"],
                        "content": f"{entry.title}\n\nĐọc toàn văn tại: {entry.link}",
                        "articles": [],
                        "tags": ["cập nhật tự động", "live", doc_type],
                        "relatedDocs": []
                    })
        except Exception as e:
            continue
            
    # Nguồn 2: Tổng cục Hải quan (Web scraping trực tiếp - Basic)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # Lấy trang tin tức hoặc điểm văn bản
        r = requests.get('https://www.customs.gov.vn/index.jsp?pageId=125', headers=headers, timeout=5)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Custom parsing based on customs.gov.vn structure can be added here
            pass
    except Exception:
        pass

    return live_docs


@st.cache_data(ttl=3600)
def load_documents(domain):
    """Load legal documents from JSON file and merge with live auto-updated data."""
    data_path = Path(__file__).parent / "data" / "legal-documents.json"
    docs = []
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            docs = json.load(f)
            # Lọc bớt dữ liệu tĩnh nếu đang ở mode Kế toán (Chỉ lấy văn bản chung)
            if domain == "Kế toán & Thuế nội địa":
                docs = [d for d in docs if any(kw in d.get('title','').lower() for kw in ['thuế', 'hóa đơn', 'nghị định', 'thông tư', 'doanh nghiệp'])]
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu nội bộ: {e}")
        
    # Thêm dữ liệu từ documents.json
    try:
        new_data_path = Path(__file__).parent / "data" / "documents.json"
        if new_data_path.exists():
            with open(new_data_path, "r", encoding="utf-8") as f:
                new_docs = json.load(f)
                existing_titles = {d.get('title', '') for d in docs}
                type_mapping = {
                    'Thông tư': 'thong-tu',
                    'Nghị định': 'nghi-dinh',
                    'Quyết định': 'quyet-dinh',
                    'Công văn': 'cong-van',
                    'Luật': 'luat',
                    'Nghị quyết': 'nghi-quyet'
                }
                for d in new_docs:
                    title = d.get('tieu_de', '')
                    if title in existing_titles: continue
                    doc_type = type_mapping.get(d.get('loai_van_ban', ''), 'other')
                    status = 'active' if d.get('trang_thai', '') == 'Còn hiệu lực' else 'expired'
                    docs.append({
                        'id': d.get('so_hieu', '').replace('/', '-'),
                        'type': doc_type,
                        'number': d.get('so_hieu', ''),
                        'title': title,
                        'summary': d.get('tom_tat', ''),
                        'issueDate': d.get('ngay_ban_hanh', ''),
                        'effectiveDate': d.get('ngay_hieu_luc', ''),
                        'issuingBody': d.get('co_quan_ban_hanh', ''),
                        'status': status,
                        'purpose': '',
                        'keyPoints': [],
                        'content': f"Tóm tắt: {d.get('tom_tat', '')}\nNguồn: {d.get('nguon', '')}\nURL: {d.get('url', '')}",
                        'articles': [],
                        'tags': d.get('tags', []),
                        'relatedDocs': []
                    })
    except Exception as e:
        pass

    # Lấy dữ liệu tự động mới nhất
    try:
        live_data = fetch_live_data(domain)
        if live_data:
            # Lọc bỏ các văn bản đã có trong DB nội bộ (tránh trùng lặp theo tiêu đề)
            existing_titles = {d.get('title', '').lower() for d in docs}
            new_live_docs = [d for d in live_data if d['title'].lower() not in existing_titles]
            
            # Đưa văn bản mới lên đầu
            docs = new_live_docs + docs
    except Exception as e:
        pass
        
    # Sắp xếp toàn bộ văn bản theo ngày ban hành mới nhất (giảm dần)
    # Văn bản nào không có ngày ban hành thì đẩy xuống cuối
    docs.sort(key=lambda x: x.get('issueDate') or '1900-01-01', reverse=True)
    
    return docs


@st.cache_resource
def get_system_stats():
    """Lưu trữ thống kê hệ thống (dùng chung cho mọi phiên truy cập)."""
    from datetime import datetime
    return {
        "active_sessions": {},
        "api_date": get_vn_time().date(),
        "api_calls": 0,
        "api_limit": 1500,
        "total_visitors": 18243
    }

def get_client_info():
    ip = "Không xác định"
    device = "Máy tính (Desktop)"
    try:
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers
            # Get IP
            ip = headers.get("X-Forwarded-For", headers.get("X-Real-IP", "Không xác định"))
            if "," in ip:
                ip = ip.split(",")[0].strip()
            
            # Get Device
            user_agent = headers.get("User-Agent", "").lower()
            if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
                device = "Điện thoại (Mobile)"
            elif "tablet" in user_agent or "ipad" in user_agent:
                device = "Máy tính bảng (Tablet)"
    except Exception:
        pass
    return ip, device

@st.cache_data(ttl=86400)
def get_location_from_ip(ip):
    if not ip or ip == "Không xác định" or ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10."):
        return None
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        if res.get("status") == "success":
            return {
                "lat": float(res.get("lat", 0)),
                "lon": float(res.get("lon", 0)),
                "city": res.get("city", "Unknown"),
                "country": res.get("country", "Unknown")
            }
    except Exception:
        pass
    return None


# ============================================
# CONSTANTS
# ============================================
TYPE_NAMES = {
    "thong-tu": "Thông tư",
    "nghi-dinh": "Nghị định",
    "nghi-quyet": "Nghị quyết",
    "luat": "Luật",
    "cong-van": "Công văn",
    "quyet-dinh": "Quyết định",
}

TYPE_BADGES = {
    "thong-tu": "badge-thong-tu",
    "nghi-dinh": "badge-nghi-dinh",
    "nghi-quyet": "badge-nghi-quyet",
    "luat": "badge-luat",
    "cong-van": "badge-cong-van",
    "quyet-dinh": "badge-quyet-dinh",
}

TYPE_ICONS = {
    "thong-tu": "📘",
    "nghi-dinh": "📗",
    "nghi-quyet": "📕",
    "luat": "📙",
    "cong-van": "📄",
    "quyet-dinh": "📋",
}

STATUS_NAMES = {
    "active": "Còn hiệu lực",
    "amended": "Đã sửa đổi",
    "expired": "Hết hiệu lực",
}

STATUS_CSS = {
    "active": "status-active",
    "amended": "status-amended",
    "expired": "status-expired",
}

FOLDER_MAP = {
    "thong-tu": "A",
    "nghi-dinh": "B",
    "nghi-quyet": "C",
    "luat": "D",
    "cong-van": "E",
    "quyet-dinh": "E",
}

STOP_WORDS = {
    'có', 'không', 'nào', 'là', 'về', 'của', 'cho', 'và', 'hay', 'hoặc',
    'bị', 'được', 'theo', 'tại', 'trong', 'những', 'các', 'một', 'này',
    'đó', 'thì', 'mà', 'để', 'với', 'từ', 'đến', 'khi', 'nếu', 'do',
    'vì', 'bằng', 'qua', 'trên', 'dưới', 'ra', 'vào', 'lên', 'xuống',
    'lại', 'đi', 'hơn', 'nhất', 'rất', 'quá', 'cũng', 'đã', 'đang',
    'sẽ', 'chưa', 'còn', 'ai', 'gì', 'đâu', 'sao', 'nên', 'phải',
    'cần', 'muốn', 'biết', 'hiểu', 'xin', 'hỏi', 'cho', 'tôi', 'mình',
    'ạ', 'nhé', 'nhỉ', 'vậy', 'thế', 'như', 'nữa', 'đều',
    'mọi', 'hết', 'toàn', 'bộ', 'riêng', 'chung', 'khác', 'giống',
}

DOC_TYPE_MAP = {
    'thông tư': 'thong-tu', 'tt': 'thong-tu',
    'nghị định': 'nghi-dinh', 'nđ': 'nghi-dinh', 'nd': 'nghi-dinh',
    'nghị quyết': 'nghi-quyet', 'nq': 'nghi-quyet',
    'luật': 'luat',
    'công văn': 'cong-van', 'cv': 'cong-van',
    'quyết định': 'quyet-dinh', 'qđ': 'quyet-dinh', 'qd': 'quyet-dinh',
}


# ============================================
# SEARCH ENGINE
# ============================================
def normalize_text(text: str) -> str:
    """Normalize Vietnamese text for comparison."""
    return unidecode(text).lower().strip()


def is_question(query: str) -> bool:
    """Detect if query is a question."""
    if '?' in query:
        return True
    patterns = [
        r'có.*không', r'là gì', r'bao nhiêu', r'thế nào', r'như thế nào',
        r'làm sao', r'tại sao', r'vì sao', r'ở đâu', r'khi nào', r'bao giờ',
        r'theo.*nào', r'quy định.*gì', r'hướng dẫn.*gì', r'áp dụng.*nào',
    ]
    q_lower = query.lower()
    return any(re.search(p, q_lower) for p in patterns)


def parse_query(query: str) -> dict:
    """Parse a Vietnamese natural language query."""
    result = {
        'keywords': [],
        'doc_type': None,
        'year_filter': None,
        'is_question': is_question(query),
        'sort_by': 'relevance',
        'original': query,
    }

    q = query.lower().strip()

    # Detect document type (multi-word first)
    for phrase in ['thông tư', 'nghị định', 'nghị quyết', 'công văn', 'quyết định']:
        if phrase in q:
            result['doc_type'] = DOC_TYPE_MAP[phrase]
            q = q.replace(phrase, '').strip()
            break

    if not result['doc_type']:
        words = q.split()
        for w in words:
            if w in DOC_TYPE_MAP and w not in ('tt',):
                result['doc_type'] = DOC_TYPE_MAP[w]
                q = q.replace(w, '', 1).strip()
                break

    # Detect year
    year_match = re.search(r'năm\s*(\d{4})', q)
    if year_match:
        result['year_filter'] = int(year_match.group(1))
        q = q.replace(year_match.group(0), '').strip()

    # Detect sort
    if re.search(r'mới\s*nhất|gần\s*đây|latest', q):
        result['sort_by'] = 'newest'
        q = re.sub(r'mới\s*nhất|gần\s*đây|latest', '', q).strip()

    # Extract keywords (remove stop words)
    tokens = [w for w in q.split() if len(w) > 1]
    keywords = [w for w in tokens if w not in STOP_WORDS]
    result['keywords'] = keywords if keywords else [w for w in tokens if len(w) > 1]

    return result


def search_documents(documents: list, query: str) -> list:
    """Smart search with fuzzy matching."""
    if not query or not query.strip():
        return documents

    parsed = parse_query(query)
    pool = documents

    # Filter by document type if detected
    if parsed['doc_type']:
        pool = [d for d in pool if d.get('type') == parsed['doc_type']]

    # Filter by year if detected
    if parsed['year_filter']:
        pool = [d for d in pool if str(parsed['year_filter']) in d.get('issueDate', '')]

    if not parsed['keywords']:
        if parsed['sort_by'] == 'newest':
            pool.sort(key=lambda d: d.get('issueDate', ''), reverse=True)
        return pool

    # Score each document
    search_text = ' '.join(parsed['keywords'])
    search_norm = normalize_text(search_text)
    scored = []

    for doc in pool:
        score = 0

        # Search in multiple fields with weights
        fields = [
            (doc.get('title', ''), 30),
            (doc.get('summary', ''), 20),
            (doc.get('purpose', ''), 15),
            (' '.join(doc.get('keyPoints', [])), 15),
            (doc.get('content', ''), 10),
            (' '.join(doc.get('tags', [])), 10),
            (doc.get('number', ''), 5),
        ]

        # Also search in articles
        for art in doc.get('articles', []):
            fields.append((art.get('content', ''), 8))
            fields.append((art.get('title', ''), 5))

        for field_text, weight in fields:
            if not field_text:
                continue
            field_norm = normalize_text(field_text)
            field_lower = field_text.lower()

            # Exact substring match (highest score)
            for kw in parsed['keywords']:
                if kw in field_lower:
                    score += weight * 3
                elif normalize_text(kw) in field_norm:
                    score += weight * 2

            # Fuzzy match
            ratio = fuzz.partial_ratio(search_norm, field_norm)
            if ratio > 50:
                score += (ratio / 100) * weight

        if score > 0:
            scored.append((doc, score))

    # Sort by score (highest first)
    scored.sort(key=lambda x: x[1], reverse=True)

    if parsed['sort_by'] == 'newest':
        scored.sort(key=lambda x: x[0].get('issueDate', ''), reverse=True)

    return [doc for doc, _ in scored]


def highlight_text(text: str, keywords: list) -> str:
    """Highlight matching keywords in text with red background."""
    if not text or not keywords:
        return text

    result = text
    for kw in keywords:
        if len(kw) < 2:
            continue
        # Case-insensitive replace, preserve original case
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        result = pattern.sub(
            lambda m: f'<span class="search-match">{m.group()}</span>',
            result
        )
    return result


def generate_answer(query: str, results: list, keywords: list) -> str:
    """Generate a structured answer panel for question queries."""
    if not results:
        return ""

    html = '<div class="answer-panel">'
    html += '<h3>📋 Kết quả tra cứu</h3>'
    html += f'<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:1rem;">Câu hỏi: <em>"{query}"</em></p>'

    for i, doc in enumerate(results[:5], 1):
        type_name = TYPE_NAMES.get(doc.get('type', ''), doc.get('type', ''))
        badge_class = TYPE_BADGES.get(doc.get('type', ''), '')

        html += '<div class="answer-item">'
        html += f'<div class="answer-item-title">'
        html += f'{i}/ Theo <span class="type-badge {badge_class}">{type_name}</span> '
        html += f'số <strong>{doc.get("number", "")}</strong>'

        issue_date = doc.get('issueDate', '')
        if issue_date:
            try:
                dt = datetime.strptime(issue_date, '%Y-%m-%d')
                html += f' ngày {dt.strftime("%d/%m/%Y")}'
            except:
                pass

        issuer = doc.get('issuingBody', '')
        if issuer:
            html += f' của <em>{issuer}</em>'
        html += ':</div>'

        # Show relevant key points
        key_points = doc.get('keyPoints', [])
        if key_points:
            html += '<div class="answer-item-content">'
            for point in key_points[:3]:
                highlighted = highlight_text(point, keywords)
                html += f'• {highlighted}<br>'
            html += '</div>'

        # Show relevant articles
        articles = doc.get('articles', [])
        if articles:
            html += '<div class="answer-item-content" style="margin-top:0.5rem;">'
            for art in articles[:2]:
                art_title = art.get('number', '') or art.get('title', '')
                art_content = art.get('content', '')[:300]
                highlighted_content = highlight_text(art_content, keywords)
                html += f'<strong style="color:#fbbf24;">{art_title}</strong>: {highlighted_content}<br><br>'
            html += '</div>'

        html += '</div>'

    html += '</div>'
    return html


def format_doc_for_download(doc: dict) -> str:
    """Format document as text for download."""
    type_name = TYPE_NAMES.get(doc.get('type', ''), doc.get('type', '')).upper()
    lines = [
        '=' * 80,
        type_name,
        f'Số: {doc.get("number", "")}',
        '=' * 80,
        '',
        f'TIÊU ĐỀ: {doc.get("title", "")}',
        '',
        f'Ngày ban hành: {doc.get("issueDate", "N/A")}',
        f'Ngày hiệu lực: {doc.get("effectiveDate", "N/A")}',
        f'Cơ quan ban hành: {doc.get("issuingBody", "N/A")}',
        f'Trạng thái: {STATUS_NAMES.get(doc.get("status", ""), "N/A")}',
        '',
        '-' * 80,
        'TÓM TẮT NỘI DUNG:',
        '-' * 80,
        doc.get('summary', ''),
        '',
        '-' * 80,
        'MỤC ĐÍCH BAN HÀNH:',
        '-' * 80,
        doc.get('purpose', ''),
        '',
        '-' * 80,
        'NỘI DUNG CHÍNH:',
        '-' * 80,
    ]

    for i, point in enumerate(doc.get('keyPoints', []), 1):
        lines.append(f'{i}. {point}')

    if doc.get('articles'):
        lines.extend(['', '-' * 80, 'CÁC ĐIỀU KHOẢN QUAN TRỌNG:', '-' * 80])
        for art in doc['articles']:
            num = art.get('number', '')
            title = art.get('title', '')
            lines.append(f'\n{num}{"." if title else ""} {title}')
            lines.append(art.get('content', ''))

    lines.extend([
        '', '=' * 80,
        'NỘI DUNG ĐẦY ĐỦ:',
        '=' * 80,
        doc.get('content', ''),
        '', '=' * 80,
        f'Tags: {", ".join(doc.get("tags", []))}',
        f'Văn bản liên quan: {", ".join(doc.get("relatedDocs", []))}',
        '=' * 80,
    ])

    return '\n'.join(lines)


# ============================================
# RENDER FUNCTIONS
# ============================================
def render_header(domain):
    title = "⚖️ CỔNG PHÁP LUẬT HẢI QUAN VIỆT NAM" if domain == "Hải quan & Xuất nhập khẩu" else "⚖️ CỔNG PHÁP LUẬT KẾ TOÁN & THUẾ"
    st.markdown(f"""
    <div class="main-header">
        <h1>{title} <span style="font-size: 1rem; color: #fbbf24; background: rgba(0,0,0,0.3); padding: 4px 10px; border-radius: 10px; margin-left: 10px; vertical-align: middle;">[V6886]</span></h1>
        <p style="margin-top:0.5rem; color:#fde047; font-weight:800; font-size: 1.4rem; text-transform: uppercase; text-shadow: 0 2px 5px rgba(0,0,0,0.5);">👨‍💻 Phát triển bởi tác giả: Vũ Việt Cường năm 2026</p>
        <p>Tra cứu Thông tư • Nghị định • Nghị quyết • Luật • Công văn • Quyết định</p>
    </div>
    <div style="background: linear-gradient(90deg, #10b981 0%, #059669 100%); padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); border: 1px solid #34d399;">
        <span style="color: white; font-weight: bold; font-size: 1.1rem;">
            🔄 HỆ THỐNG AUTO-UPDATE (VER V6886) ĐÃ CẬP NHẬT DỮ LIỆU LÚC: {get_vn_time().strftime('%H:%M - %d/%m/%Y')} (Giờ VN)
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_stats(documents):
    type_counts = {}
    for doc in documents:
        t = doc.get('type', 'other')
        type_counts[t] = type_counts.get(t, 0) + 1

    cols = st.columns(7)
    stats = [
        ("📚", len(documents), "Tổng văn bản", "all"),
        ("📘", type_counts.get('thong-tu', 0), "Thông tư", "thong-tu"),
        ("📗", type_counts.get('nghi-dinh', 0), "Nghị định", "nghi-dinh"),
        ("📕", type_counts.get('nghi-quyet', 0), "Nghị quyết", "nghi-quyet"),
        ("📙", type_counts.get('luat', 0), "Luật", "luat"),
        ("📄", type_counts.get('cong-van', 0), "Công văn", "cong-van"),
        ("📋", type_counts.get('quyet-dinh', 0), "Quyết định", "quyet-dinh"),
    ]

    for col, (icon, count, label, _) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size:1.5rem;">{icon}</div>
                <div class="stat-number">{count}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def render_doc_card(doc, keywords=None):
    """Render a document card."""
    doc_type = doc.get('type', '')
    badge_class = TYPE_BADGES.get(doc_type, '')
    type_name = TYPE_NAMES.get(doc_type, doc_type)
    status = doc.get('status', 'active')
    status_name = STATUS_NAMES.get(status, status)
    status_class = STATUS_CSS.get(status, '')

    title = doc.get('title', '')
    summary = doc.get('summary', '')[:200]

    if keywords:
        title = highlight_text(title, keywords)
        summary = highlight_text(summary, keywords)

    issue_date = doc.get('issueDate', '')
    formatted_date = ''
    if issue_date:
        try:
            dt = datetime.strptime(issue_date, '%Y-%m-%d')
            formatted_date = dt.strftime('%d/%m/%Y')
        except:
            formatted_date = issue_date

    st.markdown(f"""
    <div class="doc-card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
            <span class="type-badge {badge_class}">{type_name}</span>
            <span class="{status_class}">{status_name}</span>
        </div>
        <div class="doc-card-number">{doc.get('number', '')}</div>
        <div class="doc-card-title">{title}</div>
        <div class="doc-card-meta">📅 {formatted_date} • {doc.get('issuingBody', '')}</div>
        <div class="doc-card-summary">{summary}...</div>
    </div>
    """, unsafe_allow_html=True)


def render_doc_detail(doc, keywords=None):
    """Render full document detail."""
    doc_type = doc.get('type', '')
    badge_class = TYPE_BADGES.get(doc_type, '')
    type_name = TYPE_NAMES.get(doc_type, doc_type)
    type_icon = TYPE_ICONS.get(doc_type, '📄')
    status = doc.get('status', 'active')
    status_name = STATUS_NAMES.get(status, status)
    folder = FOLDER_MAP.get(doc_type, 'E')

    # Header
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;flex-wrap:wrap;">
        <span class="type-badge {badge_class}" style="font-size:0.9rem;padding:5px 15px;">
            {type_icon} {type_name}
        </span>
        <span style="color:#6366f1;font-weight:700;font-size:1.1rem;">{doc.get('number', '')}</span>
        <span class="{STATUS_CSS.get(status, '')}">{status_name}</span>
    </div>
    """, unsafe_allow_html=True)

    title = doc.get('title', '')
    if keywords:
        title = highlight_text(title, keywords)
    st.markdown(f'<h3 style="color:#e2e8f0;font-size:1.2rem;line-height:1.4;">{title}</h3>', unsafe_allow_html=True)

    # Metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        issue_date = doc.get('issueDate', '')
        if issue_date:
            try:
                dt = datetime.strptime(issue_date, '%Y-%m-%d')
                st.markdown(f"📅 **Ngày ban hành:** {dt.strftime('%d/%m/%Y')}")
            except:
                st.markdown(f"📅 **Ngày ban hành:** {issue_date}")
    with col2:
        eff_date = doc.get('effectiveDate', '')
        if eff_date:
            try:
                dt = datetime.strptime(eff_date, '%Y-%m-%d')
                st.markdown(f"📆 **Ngày hiệu lực:** {dt.strftime('%d/%m/%Y')}")
            except:
                st.markdown(f"📆 **Ngày hiệu lực:** {eff_date}")
    with col3:
        st.markdown(f"🏛️ **Cơ quan:** {doc.get('issuingBody', 'N/A')}")

    st.divider()

    # Summary
    summary = doc.get('summary', '')
    if keywords:
        summary = highlight_text(summary, keywords)
    st.markdown(f"""
    <div class="detail-section">
        <h4>📝 TÓM TẮT NỘI DUNG</h4>
        <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.7;">{summary}</div>
    </div>
    """, unsafe_allow_html=True)

    # Purpose
    purpose = doc.get('purpose', '')
    if purpose:
        if keywords:
            purpose = highlight_text(purpose, keywords)
        st.markdown(f"""
        <div class="detail-section">
            <h4>🎯 MỤC ĐÍCH BAN HÀNH</h4>
            <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.7;">{purpose}</div>
        </div>
        """, unsafe_allow_html=True)

    # Key Points
    key_points = doc.get('keyPoints', [])
    if key_points:
        points_html = '<div class="detail-section"><h4>📌 NỘI DUNG CHÍNH</h4><ul>'
        for point in key_points:
            p = highlight_text(point, keywords) if keywords else point
            points_html += f'<li style="color:#e2e8f0;font-size:0.88rem;margin-bottom:0.5rem;line-height:1.5;">{p}</li>'
        points_html += '</ul></div>'
        st.markdown(points_html, unsafe_allow_html=True)

    # Articles
    articles = doc.get('articles', [])
    if articles:
        st.markdown('<div class="detail-section"><h4>📖 CÁC ĐIỀU KHOẢN QUAN TRỌNG</h4></div>', unsafe_allow_html=True)
        for art in articles:
            art_num = art.get('number', '')
            art_title = art.get('title', '')
            art_content = art.get('content', '')
            if keywords:
                art_title = highlight_text(art_title, keywords)
                art_content = highlight_text(art_content, keywords)
            header = f"{art_num}" + (f". {art_title}" if art_title else "")
            with st.expander(f"📜 {art.get('number', '')} - {art.get('title', '')}", expanded=False):
                st.markdown(f"""
                <div class="article-content">{art_content}</div>
                """, unsafe_allow_html=True)

    # Full Content
    content = doc.get('content', '')
    if content:
        with st.expander("📄 XEM NỘI DUNG ĐẦY ĐỦ", expanded=False):
            if keywords:
                content = highlight_text(content, keywords)
            st.markdown(f'<div style="color:#cbd5e1;font-size:0.88rem;line-height:1.8;white-space:pre-wrap;">{content}</div>', unsafe_allow_html=True)

    # Download button
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        file_content = format_doc_for_download(doc)
        safe_number = re.sub(r'[/\\?%*:|"<>]', '-', doc.get('number', 'unknown'))
        filename = f"{safe_number}.txt"
        st.download_button(
            label=f"💾 Tải xuống (Folder {folder})",
            data=file_content.encode('utf-8-sig'),
            file_name=filename,
            mime='text/plain',
            use_container_width=True,
        )
    with col2:
        # Tags
        tags = doc.get('tags', [])
        if tags:
            tags_html = ' '.join([f'<span class="quick-tag">{t}</span>' for t in tags[:8]])
            st.markdown(f'<div style="margin-top:0.5rem;">{tags_html}</div>', unsafe_allow_html=True)


def render_footer(domain):
    portal_name = "Cổng Pháp Luật Hải Quan Việt Nam" if domain == "Hải quan & Xuất nhập khẩu" else "Cổng Pháp Luật Kế Toán & Thuế"
    stats = get_system_stats()
    st.markdown(f"""
    <div class="footer">
        <p>⚖️ <strong>{portal_name}</strong></p>
        <p>Dữ liệu tham khảo từ: thuvienphapluat.vn • customs.gov.vn • chinhphu.vn</p>
        <p>📧 tinnam888888_haiquan.streamlit.app</p>
        <p style="margin-top:0.8rem; color:#a5b4fc; font-weight:700; font-size: 0.95rem;">👨‍💻 Phát triển bởi tác giả: Vũ Việt Cường năm 2026</p>
        <p style="margin-top:0.2rem; font-weight:bold; color:#fde047;">👤 Số người truy cập: {stats["total_visitors"]:,}</p>
        <p style="margin-top:0.2rem;">© 2024-2026 | Cập nhật liên tục các văn bản mới nhất</p>
    </div>
    """, unsafe_allow_html=True)


def call_gemini_api(query, context_docs, api_key, domain):
    """Sử dụng Gemini API để trả lời câu hỏi pháp lý dựa trên ngữ cảnh."""
    

    # Bỏ qua dữ liệu cục bộ theo yêu cầu của người dùng, để AI tự tìm 100% trên Internet toàn cầu
    context_text = ""
        
    if domain == "Hải quan & Xuất nhập khẩu":
        role_desc = "một chuyên gia pháp lý và luật sư Hải quan Việt Nam cực kỳ am hiểu luật cập nhật đến năm 2026."
        special_instructions = """ĐẶC BIỆT LƯU Ý VỀ TRA CỨU HÀNG HÓA, MÃ HS VÀ THUẾ NĂM 2026:
- CẬP NHẬT KIẾN THỨC BẮT BUỘC (2026): Luật Quản lý thuế số 38/2019/QH14 ĐÃ BỊ THAY THẾ bởi Luật Quản lý thuế số 108/2025/QH15. Nghị định 125/2020/NĐ-CP đã bị sửa đổi, bổ sung bởi Nghị định 310/2025/NĐ-CP. Bắt buộc phải áp dụng các Luật, Nghị định năm 2025/2026 này, KHÔNG ĐƯỢC dùng Luật cũ!
- BẠN BẮT BUỘC SỬ DỤNG CÔNG CỤ TÌM KIẾM GOOGLE (Google Search) ĐỂ LẤY DỮ LIỆU TỪ INTERNET TOÀN CẦU (thuvienphapluat.vn, chinhphu.vn, luatvietnam.vn, haiquanonline...).
- TUYỆT ĐỐI KHÔNG DÙNG KIẾN THỨC CŨ. Mọi câu trả lời phải lấy dữ liệu thực tế ngay tại thời điểm tra cứu trên Internet. Bắt buộc ghi rõ Nguồn tra cứu.
- BẮT BUỘC TRÌNH BÀY thông tin Thuế, HS Code, mức phạt theo dạng danh sách gạch đầu dòng (Bullet points). TUYỆT ĐỐI KHÔNG SỬ DỤNG BẢNG (TABLE) VÌ SẼ BỊ LỖI HIỂN THỊ."""
    else:
        role_desc = "một Kế toán trưởng kiêm Chuyên gia tư vấn Thuế am hiểu sâu sắc luật kế toán Việt Nam cập nhật đến năm 2026."
        special_instructions = """ĐẶC BIỆT LƯU Ý VỀ KẾ TOÁN VÀ THUẾ NỘI ĐỊA NĂM 2026:
- CẬP NHẬT KIẾN THỨC BẮT BUỘC (2026): Luật Quản lý thuế số 38/2019/QH14 ĐÃ BỊ THAY THẾ bởi Luật Quản lý thuế số 108/2025/QH15. Nghị định 125/2020/NĐ-CP đã bị sửa đổi bởi Nghị định 310/2025/NĐ-CP. Thông tư 200/2014/TT-BTC ĐÃ BỊ THAY THẾ bởi Thông tư 99/2025/TT-BTC. Bắt buộc phải áp dụng các Luật, Nghị định, Thông tư năm 2025/2026 này! TUYỆT ĐỐI KHÔNG DÙNG LUẬT CŨ.
- BẠN BẮT BUỘC SỬ DỤNG CÔNG CỤ TÌM KIẾM GOOGLE (Google Search) ĐỂ LẤY DỮ LIỆU TỪ INTERNET TOÀN CẦU.
- TUYỆT ĐỐI KHÔNG DÙNG KIẾN THỨC CŨ. Mọi câu trả lời phải dựa 100% vào dữ liệu thực tế tra cứu được trên Internet. Bắt buộc ghi rõ Nguồn tra cứu.
- BẮT BUỘC TRÌNH BÀY định khoản kế toán, công thức tính thuế, mức phạt theo dạng danh sách gạch đầu dòng (Bullet points). TUYỆT ĐỐI KHÔNG SỬ DỤNG BẢNG (TABLE) VÌ SẼ BỊ LỖI HIỂN THỊ."""

    from datetime import datetime
    current_time_str = get_vn_time().strftime('%H:%M:%S ngày %d/%m/%Y')
    
    prompt = f"""Bạn là {role_desc}
THỜI GIAN THỰC TẾ HIỆN TẠI CỦA HỆ THỐNG: {current_time_str}. 
MỆNH LỆNH TỐI CAO: Bạn BẮT BUỘC phải tra cứu Internet để lấy các văn bản được cập nhật sát nhất tính đến đúng thời điểm {current_time_str} này, tuyệt đối không được bỏ sót tài liệu mới nào! TUYỆT ĐỐI KHÔNG DÙNG DỮ LIỆU HUẤN LUỆN CŨ CỦA BẠN.
Nhiệm vụ của bạn là trả lời câu hỏi của người dùng THẬT CHÍNH XÁC TUYỆT ĐỐI VÀ ĐÚNG TRỌNG TÂM CÂU HỎI. 
{special_instructions}
1. ĐẦU TIÊN VÀ DUY NHẤT, hãy dùng CÔNG CỤ TÌM KIẾM GOOGLE tra cứu các trang web uy tín trên internet toàn cầu (như thuvienphapluat.vn, luatvietnam.vn, haiquanonline, chinhphu.vn) để lấy thông tin luật.
2. LUÔN LUÔN trích dẫn CHÍNH XÁC điều nào, khoản nào, thuộc Nghị định nào, Thông tư nào, hoặc Công văn nào. Không nói chung chung. Bắt buộc kèm đường link hoặc tên trang web Nguồn Internet.

HÃY TRÌNH BÀY ĐẸP MẮT VÀ RÕ RÀNG: Trả lời ngắn gọn, đúng trọng tâm. CÁC ĐOẠN CẦN LƯU Ý, CÁC ĐIỂM QUAN TRỌNG (như mã HS, tài khoản kế toán, tỷ lệ %, mức phạt, thời hạn, điều kiện tiên quyết) BẮT BUỘC PHẢI BÔI VÀNG ĐẬM RÕ RÀNG bằng cách bọc trong thẻ HTML <mark>nội dung</mark> (ví dụ: <mark>Nghị định 15/2022/NĐ-CP</mark>). Dùng in đậm, in nghiêng hợp lý để mạch lạc, dễ đọc.

CÂU HỎI CỦA NGƯỜI DÙNG:
{query}

TRẢ LỜI CỦA LUẬT SƯ:"""

    api_keys = [k.strip() for k in api_key.split(',')] if ',' in api_key else [api_key.strip()]
    stats = get_system_stats()
    from datetime import datetime
    if stats["api_date"] != get_vn_time().date():
        stats["api_date"] = get_vn_time().date()
        stats["api_calls"] = 0
        
    last_error = ""
    # Giai đoạn 1: Trùm cuối Deep Research (CÓ Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('deep-research-max-preview-04-2026', tools='google_search_retrieval')
            response = model.generate_content(prompt)
            text = response.text + "\n\n---\n*💡 Đã trả lời bởi: Tầng 1 (Deep Research Max + Search)*"
            stats["api_calls"] += 1
            return text
        except Exception as e:
            last_error = str(e)
            continue

    # Giai đoạn 2: Trùm cuối 3.1 Pro (CÓ Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-3.1-pro-preview', tools='google_search_retrieval')
            response = model.generate_content(prompt)
            text = response.text + "\n\n---\n*💡 Đã trả lời bởi: Tầng 2 (Gemini 3.1 Pro + Search)*"
            stats["api_calls"] += 1
            return text
        except Exception as e:
            last_error = str(e)
            continue

    # Giai đoạn 3: Trùm cuối Pro Latest (CÓ Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-pro-latest', tools='google_search_retrieval')
            response = model.generate_content(prompt)
            text = response.text + "\n\n---\n*💡 Đã trả lời bởi: Tầng 3 (Gemini Pro Latest + Search)*"
            stats["api_calls"] += 1
            return text
        except Exception as e:
            last_error = str(e)
            continue

    # Giai đoạn 4: Mạnh nhất 3.5 Flash (CÓ Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-3.5-flash', tools='google_search_retrieval')
            response = model.generate_content(prompt)
            text = response.text + "\n\n---\n*💡 Đã trả lời bởi: Tầng 4 (Gemini 3.5 Flash + Search)*"
            stats["api_calls"] += 1
            return text
        except Exception as e:
            last_error = str(e)
            continue

    # Giai đoạn 5: Trùm cuối 3.1 Pro (KHÔNG Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-3.1-pro-preview')
            response = model.generate_content(prompt)
            text = response.text + "\n\n---\n*💡 Đã trả lời bởi: Tầng 5 (Gemini 3.1 Pro - Bản Offline Suy Luận Mạnh Nhất)*"
            stats["api_calls"] += 1
            return text
        except Exception as e:
            last_error = str(e)
            continue

    # Giai đoạn 6: Trùm cuối 2.5 Pro (KHÔNG Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-2.5-pro')
            response = model.generate_content(prompt)
            text = response.text + "\n\n---\n*💡 Đã trả lời bởi: Tầng 6 (Gemini 2.5 Pro - Bản Offline Thế Hệ Trị Giá Cao)*"
            stats["api_calls"] += 1
            return text
        except Exception as e:
            last_error = str(e)
            continue

    # Giai đoạn 7: Tốc độ cao 2.5 Flash (KHÔNG Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            text = response.text + "\n\n---\n*💡 Đã trả lời bởi: Tầng 7 (Gemini 2.5 Flash - Bản Offline Thông Minh Tốc Độ)*"
            stats["api_calls"] += 1
            return text
        except Exception as e:
            last_error = str(e)
            continue

    # Giai đoạn 8: Lớp bảo vệ (Gemini flash-lite-latest KHÔNG Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-flash-lite-latest')
            response = model.generate_content(prompt)
            text = response.text + "\n\n---\n*💡 Đã trả lời bởi: Tầng 8 (Gemini Flash Lite - Bản offline an toàn)*"
            stats["api_calls"] += 1
            return text
        except Exception as e:
            last_error = str(e)
            continue
            
    if "quota" in last_error.lower() or "429" in last_error:
        available_models = "Không lấy được"
        try:
            genai.configure(api_key=api_keys[0])
            available_models = ", ".join([m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods])
        except:
            pass
        return f"⚠️ **Hệ thống đã thử toàn bộ API Keys nhưng đều đã Quá tải hoặc Hết lượt AI miễn phí!**\n\n*(Lưu ý: Bạn có thể nhập nhiều API Key cùng lúc, cách nhau bằng dấu phẩy `,`)*\n\nGoogle giới hạn tài khoản miễn phí ở 2 mức:\n1. **Giới hạn tốc độ (15 câu / phút):** Bạn đang hỏi quá nhanh, vui lòng đợi khoảng 1 phút rồi thử lại.\n2. **Giới hạn ngày (1500 câu / ngày):** Vui lòng [vào đây](https://aistudio.google.com/app/apikey) bằng tài khoản Gmail khác để lấy Key mới và dán nối tiếp vào phần cài đặt theo dạng `KEY1, KEY2, KEY3`.\n\n**🤖 CÁC MODEL KHẢ DỤNG CHO API NÀY:**\n`{available_models}`\n\n**🔍 CHI TIẾT LỖI GỐC CỦA GOOGLE:**\n`{last_error}`"
    else:
        return f"Lỗi khi kết nối với AI Trợ lý: {last_error}. Vui lòng kiểm tra lại cấu hình API Key."


def classify_solder_product(product_type, silver_pct, flux_pct, solvent_pct=0):
    """
    Phân loại mã HS tự động cho sản phẩm hàn (Kem hàn / Dây hàn)
    Dựa trên quy tắc hải quan Việt Nam và Chú giải chi tiết HS (WCO Explanatory Notes).
    """
    reasoning = []
    hs_code = ""
    
    if product_type == "Kem hàn (Solder Paste)":
        hs_code = "3810.10.00"
        reasoning.append("Sản phẩm là chế phẩm dạng bột nhão (paste) chứa bột kim loại phối trộn với các chất phi kim (chất trợ dung và dung môi).")
        reasoning.append(f"Thành phần chi tiết: Bạc (Ag) chiếm <mark>{silver_pct}%</mark>, Chất trợ dung chiếm <mark>{flux_pct}%</mark>, Dung môi chiếm <mark>{solvent_pct}%</mark>.")
        reasoning.append("Theo Chú giải chi tiết nhóm 38.10 (WCO Explanatory Notes), các bột và bột nhão dùng để hàn gồm bột kim loại (kể cả kim loại quý như Bạc) phối trộn với các chất khác (như flux, dung môi...) được phân loại vào nhóm 38.10 <strong>bất kể hàm lượng kim loại quý là bao nhiêu</strong>.")
        reasoning.append("Kết luận: Mã HS phù hợp nhất là <mark>3810.10.00</mark> (Chế phẩm bột và bột nhão gồm kim loại và các vật liệu khác dùng để hàn).")

    elif product_type == "Dây hàn (Solder Wire)":
        alloy_weight = 100 - flux_pct
        if alloy_weight <= 0:
            return "Lỗi dữ liệu", ["Vui lòng kiểm tra lại tỷ lệ chất trợ dung (< 100%)."]
            
        silver_in_alloy = (silver_pct / alloy_weight) * 100
        
        reasoning.append(f"Sản phẩm là dây hàn lõi thuốc (chứa chất trợ dung <mark>{flux_pct}%</mark> và hợp kim kim loại chiếm <mark>{alloy_weight}%</mark>).")
        reasoning.append(f"Quy đổi hàm lượng Bạc (Ag) riêng trong phần hợp kim kim loại: ({silver_pct}% / {alloy_weight}%) × 100 = <strong>{silver_in_alloy:.2f}%</strong>.")
        
        if silver_in_alloy >= 2.0:
            hs_code = "7106.92.00"
            reasoning.append(f"<strong>Chú giải 5 Chương 71:</strong> Vì hàm lượng Bạc trong hợp kim đạt <strong>{silver_in_alloy:.2f}%</strong> (từ 2% trở lên), sản phẩm được coi là 'Hợp kim của kim loại quý (bạc)'.")
            reasoning.append("<strong>Chú giải loại trừ nhóm 83.11:</strong> Dây hàn có phần hợp kim chứa từ 2% trở lên theo trọng lượng của bất kỳ kim loại quý nào bị LOẠI TRỪ khỏi nhóm 83.11 và bắt buộc phải phân loại vào Chương 71.")
            reasoning.append("Kết luận: Mã HS phù hợp nhất là <mark>7106.92.00</mark> (Bạc ở dạng bán thành phẩm - dạng dây hợp kim).")
        else:
            hs_code = "8311.30.00"
            reasoning.append(f"<strong>Chú giải 5 Chương 71:</strong> Vì hàm lượng Bạc trong hợp kim chỉ đạt <strong>{silver_in_alloy:.2f}%</strong> (< 2%), sản phẩm KHÔNG được coi là hợp kim của kim loại quý.")
            reasoning.append("<strong>Chú giải nhóm 83.11:</strong> Sản phẩm là dây từ kim loại cơ bản có lõi chất trợ dung dùng để hàn bằng ngọn lửa, thuộc nhóm 83.11.")
            reasoning.append("Kết luận: Mã HS phù hợp nhất là <mark>8311.30.00</mark> (Dây có lõi bằng kim loại cơ bản dùng để hàn).")
            
    return hs_code, reasoning


def call_hs_classifier_api(product_desc, api_key):
    """Sử dụng Gemini API kết nối Internet để phân loại mã HS 2022 chuẩn xác nhất."""
    import google.generativeai as genai
    
    prompt = f"""Bạn là một chuyên gia phân tích phân loại hải quan cấp cao của Tổng cục Hải quan Việt Nam, cực kỳ am hiểu Danh mục hàng hóa xuất nhập khẩu Việt Nam ban hành kèm theo Thông tư 31/2022/TT-BTC (phiên bản HS 2022) và 6 quy tắc tổng quát giải thích mã HS.

Nhiệm vụ của bạn là phân loại mã HS và giải thích cơ sở pháp lý cho sản phẩm sau đây:
TÊN/MÔ TẢ SẢN PHẨM: "{product_desc}"

MỆNH LỆNH BẮT BUỘC:
1. Bạn phải sử dụng CÔNG CỤ TÌM KIẾM GOOGLE (Search tool) để tìm kiếm chính xác mã HS 8 chữ số của sản phẩm này trong Biểu thuế XNK Việt Nam 2022 (Thông tư 31/2022/TT-BTC).
2. Trả lời cực kỳ chuyên nghiệp theo mẫu giải trình hải quan, bao gồm:
   - MÃ HS CODE ĐỀ XUẤT (8 chữ số theo HS 2022).
   - THUẾ SUẤT THAM KHẢO (Thuế nhập khẩu ưu đãi MFN, Thuế GTGT VAT).
   - CƠ SỞ PHÁP LÝ (Trích dẫn cụ thể Quy tắc tổng quát nào từ 1 đến 6, Chú giải pháp lý của Phần nào, Chương nào, hoặc Chú giải chi tiết nhóm nào).
   - LẬP LUẬN PHÂN TÍCH (Giải thích tại sao sản phẩm lại thuộc nhóm đó, phân tích các thành phần cấu tạo hoặc công dụng để loại trừ các chương khác).

ĐỊNH DẠNG TRÌNH BÀY BẮT BUỘC:
- Các thông tin quan trọng như MÃ HS, THUẾ SUẤT, QUY TẮC, ĐIỀU LUẬT bắt buộc phải bọc trong thẻ HTML <mark>nội dung</mark> để bôi vàng nổi bật (Ví dụ: <mark>3810.10.00</mark>, <mark>Quy tắc 1</mark>, <mark>Thông tư 31/2022/TT-BTC</mark>).
- Sử dụng danh sách gạch đầu dòng (bullet points) để mạch lạc. TUYỆT ĐỐI KHÔNG DÙNG BẢNG (TABLE) vì sẽ bị lỗi hiển thị.
- Trình bày rõ ràng, chuyên nghiệp, khiêm tốn nhưng cực kỳ chắc chắn về mặt pháp lý.

TRẢ LỜI CỦA CHUYÊN GIA HẢI QUAN:"""

    api_keys = [k.strip() for k in api_key.split(',')] if ',' in api_key else [api_key.strip()]
    last_error = ""
    
    # 1. Trùm cuối 3.1 Pro (CÓ Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-3.1-pro-preview', tools='google_search_retrieval')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue

    # 2. Trùm cuối Pro Latest (CÓ Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-pro-latest', tools='google_search_retrieval')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue

    # 3. Mạnh nhất 3.5 Flash (CÓ Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-3.5-flash', tools='google_search_retrieval')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue

    # 4. Trùm cuối 3.1 Pro (KHÔNG Search)
    for current_key in api_keys:
        if not current_key: continue
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-3.1-pro-preview')
            response = model.generate_content(prompt)
            return response.text + "\n\n*(Lưu ý: Phản hồi này được tạo bởi Trợ lý Offline do API Search tạm thời gián đoạn)*"
        except Exception as e:
            last_error = str(e)
            continue
            
    return f"⚠️ **Lỗi kết nối AI:** {last_error}. Vui lòng kiểm tra lại cấu hình API Key ở sidebar."


def render_hs_tool(api_key):
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 2rem; border-radius: 16px; margin-bottom: 2rem; border: 1px solid #4338ca; box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);">
        <h2 style="color: #fff; font-size: 1.6rem; font-weight: 800; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
            🔬 TRỢ LÝ PHÂN LOẠI MÃ HS CODE VIỆT NAM (HS 2022)
        </h2>
        <p style="color: #c7d2fe; margin-top: 0.5rem; font-size: 0.95rem;">
            Giải pháp tra cứu và áp mã HS tự động theo Danh mục XNK Việt Nam (Thông tư 31/2022/TT-BTC) kết hợp Chú giải pháp lý của Tổ chức Hải quan Thế giới (WCO).
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_universal, tab_quick_solder = st.tabs([
        "🔍 Tra cứu & Phân loại HS Toàn Diện (Trí tuệ nhân tạo AI)", 
        "⚙️ Công cụ Phân loại nhanh Kem/Dây Hàn"
    ])

    with tab_universal:
        st.markdown("""
        <div style="background: #1e293b; padding: 1.2rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1.5rem;">
            <h3 style="color: #a5b4fc; font-size: 1.1rem; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                🤖 AI Phân Loại & Giải Trình Mã HS Toàn Diện (HS 2022)
            </h3>
            <p style="color: #94a3b8; font-size: 0.82rem; margin-top: 0.3rem; margin-bottom: 0;">
                Nhập tên hàng hóa chi tiết (kèm cấu tạo, công dụng hoặc vật liệu cấu thành) để AI tự động tra cứu, áp mã 8 chữ số và lập luận pháp lý theo Thông tư 31/2022/TT-BTC.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        prod_desc = st.text_area(
            "Mô tả chi tiết sản phẩm / hàng hóa cần áp mã HS:", 
            placeholder="Ví dụ: Máy pha cà phê Espresso dùng cho văn phòng, công suất 1450W, có vòi đánh sữa bằng thép không gỉ...",
            key="universal_prod_desc",
            height=100
        )
        
        btn_ai_analyze = st.button("🚀 Bắt đầu Phân Tích & Xác Định Mã HS bằng AI", use_container_width=True, type="primary")
        
        if btn_ai_analyze:
            if not api_key:
                st.warning("⚠️ **Vui lòng nhập Google Gemini API Key ở sidebar bên trái để kích hoạt Trợ lý AI phân loại HS.**")
            elif not prod_desc.strip():
                st.error("❌ Vui lòng nhập mô tả hàng hóa trước khi tiến hành phân tích.")
            else:
                with st.spinner("AI đang tiến hành quét dữ liệu Biểu thuế Việt Nam 2022, Chú giải chương và lập luận giải trình..."):
                    ai_result = call_hs_classifier_api(prod_desc, api_key)
                    st.markdown(f'<div class="ai-response-box">\n\n{ai_result}\n\n</div>', unsafe_allow_html=True)
                    st.success("✅ Phân tích hoàn tất! Bạn có thể lưu lại lập luận trên để bổ sung vào bộ hồ sơ kiểm tra sau thông quan.")

    with tab_quick_solder:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("""
            <div style="background: #1e293b; padding: 1.2rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1rem;">
                <h3 style="color: #a5b4fc; font-size: 1.1rem; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                    📝 Nhập Thông Tin Thành Phần
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            prod_type = st.selectbox(
                "1. Chọn loại sản phẩm", 
                ["Kem hàn (Solder Paste)", "Dây hàn (Solder Wire)"],
                key="hs_prod_type"
            )
            
            silver = st.number_input(
                "2. Hàm lượng Bạc - Ag (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=2.3, 
                step=0.1,
                key="hs_silver"
            )
            
            flux = st.number_input(
                "3. Hàm lượng Chất trợ dung - Flux (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=12.0, 
                step=0.1,
                key="hs_flux"
            )
            
            solvent = 0.0
            if prod_type == "Kem hàn (Solder Paste)":
                solvent = st.number_input(
                    "4. Hàm lượng Dung môi - Solvent (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=2.5, 
                    step=0.1,
                    key="hs_solvent"
                )
                
            st.markdown("<br>", unsafe_allow_html=True)
            btn_analyze = st.button("🚀 Bắt đầu Phân Tích & Đối Chiếu Luật", use_container_width=True, type="primary")

        with col2:
            if btn_analyze:
                hs, steps = classify_solder_product(prod_type, silver, flux, solvent)
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #064e3b 0%, #022c22 100%); padding: 1.8rem; border-radius: 12px; border: 2px solid #059669; box-shadow: 0 8px 25px rgba(5, 150, 105, 0.2); text-align: center;">
                    <div style="font-size: 1rem; color: #a7f3d0; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">MÃ HS CODE ĐỀ XUẤT</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #fff; margin-top: 0.5rem; text-shadow: 0 2px 10px rgba(0,0,0,0.5);">{hs}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("""
                <div style="background: #0f172a; padding: 1.2rem; border-radius: 12px; border: 1px solid #1e293b; margin-bottom: 1rem;">
                    <h3 style="color: #fbbf24; font-size: 1.1rem; margin: 0;">⚖️ Lập Luận Giải Trình Pháp Lý</h3>
                </div>
                """, unsafe_allow_html=True)
                
                for i, step in enumerate(steps, 1):
                    st.markdown(f"""
                    <div class="answer-item" style="border-left-color: #fbbf24; margin-bottom: 0.8rem; font-size: 0.95rem; line-height: 1.6; color: #e2e8f0; background: rgba(255, 255, 255, 0.02); padding: 0.8rem 1.2rem; border-radius: 8px;">
                        <span style="color: #fbbf24; font-weight: bold; font-size: 1.05rem;">{i}.</span> {step}
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.success("✅ Bạn có thể copy phần giải trình pháp lý này để dán vào hồ sơ hải quan hoặc công văn giải trình kiểm tra sau thông quan.")
            else:
                st.markdown("""
                <div style="background: rgba(30, 41, 59, 0.3); border: 2px dashed #475569; border-radius: 12px; height: 350px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 2rem; color: #94a3b8;">
                    <div style="font-size: 3.5rem; margin-bottom: 1rem;">🔬</div>
                    <h3 style="color: #cbd5e1; font-size: 1.2rem; font-weight: 600; margin: 0;">Sẵn sàng Phân Tích</h3>
                    <p style="margin-top: 0.5rem; max-width: 320px; font-size: 0.85rem; line-height: 1.5;">Hãy nhập đầy đủ thông số thành phần và bấm nút "Bắt đầu Phân Tích" ở bên trái để xem kết quả mã HS và lập luận giải trình.</p>
                </div>
                """, unsafe_allow_html=True)


# ============================================
# MAIN APP
# ============================================
def main():
    if "domain" not in st.session_state:
        st.session_state.domain = "Hải quan & Xuất nhập khẩu"
        
    stats = get_system_stats()
    if "has_visited" not in st.session_state:
        st.session_state.has_visited = True
        stats["total_visitors"] += 1

    # Thử lấy API Key từ cấu hình ẩn (Secrets) của Streamlit
    try:
        api_key_secret = st.secrets.get("GEMINI_API_KEY", "")
    except:
        api_key_secret = ""

    with st.sidebar:
        st.markdown("### 🏢 Lĩnh vực tra cứu")
        selected_domain = st.selectbox(
            "Chọn chuyên ngành", 
            ["Hải quan & Xuất nhập khẩu", "Kế toán & Thuế nội địa"],
            index=0 if st.session_state.domain == "Hải quan & Xuất nhập khẩu" else 1,
            label_visibility="collapsed"
        )
        if selected_domain != st.session_state.domain:
            st.session_state.domain = selected_domain
            st.rerun()

        st.markdown("---")
        st.markdown("### 🛠️ Chức năng")
        app_mode = st.selectbox(
            "Chọn chức năng",
            ["📚 Tra cứu Luật & Văn bản", "🔬 Trợ lý Phân loại Mã HS 2022 (AI)"],
            key="app_mode"
        )

        st.markdown("---")
        st.markdown("### 🤖 Cài đặt AI Luật Sư")
        if api_key_secret:
            st.success("Đã kích hoạt AI Luật Sư (Cấu hình tự động)!")
            api_key = api_key_secret
        else:
            st.markdown("Để AI có thể tự động đọc luật và trả lời chính xác, hãy nhập Google Gemini API Key vào đây. Hỗ trợ nhập nhiều Key cùng lúc để tránh hết lượt (cách nhau bởi dấu phẩy `,`). [Lấy key miễn phí tại đây](https://aistudio.google.com/app/apikey).")
            api_key = st.text_input("Gemini API Key (Hỗ trợ nhiều Key)", type="password")
            if not api_key:
                st.warning("Vui lòng nhập API Key để kích hoạt AI.")
            else:
                st.success("Đã kích hoạt AI Luật Sư!")
                
        st.markdown("---")
        st.markdown("### 🔄 Dữ liệu trực tuyến")
        if st.button("Làm mới dữ liệu ngay", use_container_width=True, type="secondary"):
            fetch_live_data.clear()
            load_documents.clear()
            st.success("Đã xóa cache và tải dữ liệu mới nhất!")
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 📊 Thống kê hệ thống")
        stats = get_system_stats()
        
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid4())
            
        current_time = time.time()
        ip, device = get_client_info()
        location_data = get_location_from_ip(ip)

        stats["active_sessions"][st.session_state.session_id] = {
            "last_seen": current_time,
            "ip": ip,
            "device": device,
            "location": location_data
        }
        
        # Dọn dẹp session quá 5 phút (300 giây) không tương tác
        active = {}
        for sid, data in stats["active_sessions"].items():
            try:
                if isinstance(data, dict):
                    last_seen = data.get("last_seen", current_time)
                    if current_time - last_seen < 300:
                        active[sid] = data
                else:
                    # Dữ liệu cũ bị lưu đè trong cache dưới dạng float
                    last_seen = float(data)
                    if current_time - last_seen < 300:
                        active[sid] = {
                            "last_seen": last_seen,
                            "ip": "Không xác định",
                            "device": "Máy tính (Desktop)",
                            "location": None
                        }
            except Exception:
                pass
        stats["active_sessions"] = active
        
        from datetime import datetime
        if stats["api_date"] != get_vn_time().date():
            stats["api_date"] = get_vn_time().date()
            stats["api_calls"] = 0
            
        active_users = len(stats["active_sessions"])
        remaining_api = max(0, stats["api_limit"] - stats["api_calls"])
        
        st.info(f"👥 Đang online: **{active_users}** người")
        st.info(f"⚡ Lượt hỏi AI còn lại: **{remaining_api}** / {stats['api_limit']}")
        
        with st.expander("🕵️ Chi tiết người đang truy cập"):
            for sid, data in stats["active_sessions"].items():
                loc_str = f"{data['location']['city']}, {data['location']['country']}" if data.get('location') else "Không rõ (hoặc Localhost)"
                st.markdown(f"**IP:** `{data['ip']}`\n- 📱 **Máy:** {data['device']}\n- 🌍 **Vị trí:** {loc_str}")
            
            # Vẽ bản đồ nếu có dữ liệu vị trí
            locations = [d["location"] for d in stats["active_sessions"].values() if d.get("location")]
            if locations:
                df_map = pd.DataFrame(locations)
                if not df_map.empty and 'lat' in df_map.columns and 'lon' in df_map.columns:
                    st.map(df_map, zoom=2)
            
    documents = load_documents(st.session_state.domain)

    # Header
    render_header(st.session_state.domain)

    # Stop rendering the main page if the user is in HS Tool mode
    if app_mode == "🔬 Trợ lý Phân loại Mã HS 2022 (AI)":
        render_hs_tool(api_key)
        render_footer(st.session_state.domain)
        st.stop()

    # Search
    col_search, col_btn = st.columns([6, 1])
    with col_search:
        query = st.text_input(
            "🔍 Tìm kiếm",
            placeholder="Nhập câu hỏi hoặc từ khóa...",
            label_visibility="collapsed",
            key="search_input",
        )
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        search_clicked = st.button("🔍 Tìm", use_container_width=True, type="primary")

    # Quick search tags
    if st.session_state.domain == "Hải quan & Xuất nhập khẩu":
        tags_html = (
            '<span class="quick-tag">Tạm nhập tái xuất</span>\n'
            '<span class="quick-tag">Thuế xuất khẩu</span>\n'
            '<span class="quick-tag">Thủ tục thông quan</span>\n'
            '<span class="quick-tag">Quy tắc xuất xứ C/O</span>\n'
            '<span class="quick-tag">Kho ngoại quan</span>\n'
            '<span class="quick-tag">Mã loại hình G13</span>'
        )
    else:
        tags_html = (
            '<span class="quick-tag">Thuế TNDN</span>\n'
            '<span class="quick-tag">Thuế TNCN</span>\n'
            '<span class="quick-tag">Hóa đơn điện tử</span>\n'
            '<span class="quick-tag">Khấu trừ thuế GTGT</span>\n'
            '<span class="quick-tag">Chuẩn mực kế toán VAS</span>\n'
            '<span class="quick-tag">Định khoản chi phí</span>'
        )

    st.markdown(f"""
    <div style="text-align:center;margin-bottom:1.5rem;">
        <span style="color:#64748b;font-size:0.8rem;">Gợi ý: </span>
        {tags_html}
    </div>
    """, unsafe_allow_html=True)

    # Stats
    render_stats(documents)
    st.markdown("<br>", unsafe_allow_html=True)

    # Filters
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1, 1, 1])
    with filter_col1:
        type_options = ["Tất cả"] + [TYPE_NAMES[t] for t in TYPE_NAMES]
        selected_type = st.selectbox("📂 Loại văn bản", type_options, label_visibility="visible")
    with filter_col2:
        status_options = ["Tất cả", "Còn hiệu lực", "Đã sửa đổi", "Hết hiệu lực"]
        selected_status = st.selectbox("📌 Trạng thái", status_options)
    with filter_col3:
        years = sorted(set(d.get('issueDate', '')[:4] for d in documents if d.get('issueDate')), reverse=True)
        year_options = ["Tất cả"] + years
        selected_year = st.selectbox("📅 Năm", year_options)
    with filter_col4:
        sort_options = {"Mới nhất": "newest", "Cũ nhất": "oldest", "Liên quan nhất": "relevance"}
        selected_sort = st.selectbox("🔃 Sắp xếp", list(sort_options.keys()))

    st.divider()

    # Apply search and filters
    filtered_docs = documents

    # Parse search keywords for highlighting
    keywords = []
    parsed = None

    if query:
        parsed = parse_query(query)
        keywords = parsed['keywords']
        filtered_docs = search_documents(documents, query)

    # Apply type filter
    if selected_type != "Tất cả":
        type_key = [k for k, v in TYPE_NAMES.items() if v == selected_type]
        if type_key:
            filtered_docs = [d for d in filtered_docs if d.get('type') == type_key[0]]

    # Apply status filter
    status_map = {"Còn hiệu lực": "active", "Đã sửa đổi": "amended", "Hết hiệu lực": "expired"}
    if selected_status != "Tất cả":
        s = status_map.get(selected_status)
        if s:
            filtered_docs = [d for d in filtered_docs if d.get('status') == s]

    # Apply year filter
    if selected_year != "Tất cả":
        filtered_docs = [d for d in filtered_docs if d.get('issueDate', '').startswith(selected_year)]

    # Apply sort (only if not search-relevance)
    sort_key = sort_options[selected_sort]
    if sort_key == 'newest':
        filtered_docs.sort(key=lambda d: d.get('issueDate', ''), reverse=True)
    elif sort_key == 'oldest':
        filtered_docs.sort(key=lambda d: d.get('issueDate', ''))

    # Smart Answer Panel
    if query and parsed:
        if api_key:
            st.markdown("### 🤖 AI Luật Sư Trả Lời")
            with st.spinner("AI đang đọc các bộ luật, thông tư để tìm câu trả lời chính xác..."):
                ai_answer = call_gemini_api(query, filtered_docs, api_key, st.session_state.domain)
                st.markdown(f'<div class="ai-response-box">\n\n{ai_answer}\n\n</div>', unsafe_allow_html=True)
        elif filtered_docs:
            st.markdown("### 📋 Kết quả trích xuất tự động (Chưa dùng AI)")
            answer_html = generate_answer(query, filtered_docs, keywords)
            st.markdown(answer_html, unsafe_allow_html=True)

    # Results count
    if query:
        st.markdown(
            f'<p style="color:#94a3b8;font-size:0.9rem;">🔍 Tìm thấy <strong style="color:#6366f1;">'
            f'{len(filtered_docs)}</strong> kết quả cho "<em>{query}</em>"</p>',
            unsafe_allow_html=True
        )

    # Document list & detail
    if not filtered_docs:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#64748b;">
            <div style="font-size:3rem;">📭</div>
            <h3 style="color:#94a3b8;">Không tìm thấy văn bản nào</h3>
            <p>Thử thay đổi từ khóa hoặc bộ lọc</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Two-column layout: list + detail
        col_list, col_detail = st.columns([2, 3])

        with col_list:
            st.markdown(f"**📚 Danh sách ({len(filtered_docs)} văn bản)**")

            # Pagination
            page_size = 10
            total_pages = max(1, (len(filtered_docs) + page_size - 1) // page_size)

            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1

            start_idx = (st.session_state.current_page - 1) * page_size
            end_idx = start_idx + page_size
            page_docs = filtered_docs[start_idx:end_idx]

            for doc in page_docs:
                render_doc_card(doc, keywords)
                if st.button(f"📖 Xem chi tiết", key=f"btn_{doc['id']}", use_container_width=True):
                    st.session_state.selected_doc = doc['id']
                    st.rerun()

            # Pagination controls
            if total_pages > 1:
                pg_cols = st.columns([1, 2, 1])
                with pg_cols[0]:
                    if st.button("◀ Trước", disabled=st.session_state.current_page <= 1):
                        st.session_state.current_page -= 1
                        st.rerun()
                with pg_cols[1]:
                    st.markdown(
                        f'<p style="text-align:center;color:#94a3b8;">Trang {st.session_state.current_page}/{total_pages}</p>',
                        unsafe_allow_html=True
                    )
                with pg_cols[2]:
                    if st.button("Sau ▶", disabled=st.session_state.current_page >= total_pages):
                        st.session_state.current_page += 1
                        st.rerun()

        with col_detail:
            selected_id = st.session_state.get('selected_doc')

            if selected_id:
                doc = next((d for d in documents if d['id'] == selected_id), None)
                if doc:
                    st.markdown("**📄 Chi tiết văn bản**")
                    render_doc_detail(doc, keywords)
                else:
                    st.info("Chọn một văn bản từ danh sách bên trái để xem chi tiết.")
            else:
                # Show first document by default
                if filtered_docs:
                    st.markdown("**📄 Chi tiết văn bản**")
                    st.info("👈 Nhấn **Xem chi tiết** ở danh sách bên trái để xem nội dung văn bản.")

    # Footer
    render_footer(st.session_state.domain)


if __name__ == "__main__":
    main()
