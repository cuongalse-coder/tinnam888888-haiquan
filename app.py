"""
C沼봏G PH횁P LU梳촖 H梳줚 QUAN VI沼냊 NAM
Tra c沼쯷 Th척ng t튼 - Ngh沼?휃沼땙h - Ngh沼?quy梳퓍 - Lu梳춗 - C척ng v훱n - Quy梳퓍 휃沼땙h
URL: tinnam888888_haiquan.streamlit.app
"""

import streamlit as st
import json
import os
import re
from datetime import datetime
from pathlib import Path
from unidecode import unidecode
from thefuzz import fuzz
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="C沼븂g Ph찼p Lu梳춗 H梳즜 Quan Vi沼뇍 Nam - Tra c沼쯷 Th척ng t튼, Ngh沼?휃沼땙h, Lu梳춗 XNK",
    page_icon="?뽳툘",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "## ?뽳툘 C沼븂g Ph찼p Lu梳춗 H梳즜 Quan Vi沼뇍 Nam\n"
                 "H沼?th沼몁g tra c沼쯷 v훱n b梳즢 ph찼p lu梳춗 v沼?H梳즜 quan & Xu梳쩿 nh梳춑 kh梳쯷.\n\n"
                 "**Li챗n h沼?** tinnam888888_haiquan.streamlit.app"
    }
)

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

/* ===== SEARCH HIGHLIGHT (B횚I 휂沼? ===== */
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
</style>
""", unsafe_allow_html=True)


# ============================================
# DATA LOADING
# ============================================
@st.cache_data
def load_documents():
    """Load legal documents from JSON file."""
    data_path = Path(__file__).parent / "data" / "documents.json"
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            docs = data.get("documents", [])
            
            type_mapping = {
                "Thông tư": "thong-tu",
                "Nghị định": "nghi-dinh",
                "Nghị quyết": "nghi-quyet",
                "Luật": "luat",
                "Công văn": "cong-van",
                "Quyết định": "quyet-dinh"
            }
            
            mapped_docs = []
            for d in docs:
                t = d.get("loai_van_ban", "")
                mapped_doc = {
                    "id": d.get("id", ""),
                    "type": type_mapping.get(t, "other"),
                    "typeName": t,
                    "number": d.get("so_hieu", ""),
                    "title": d.get("tieu_de", ""),
                    "issueDate": d.get("ngay_ban_hanh", ""),
                    "effectiveDate": d.get("ngay_hieu_luc", ""),
                    "issuingBody": d.get("co_quan_ban_hanh", ""),
                    "summary": d.get("tom_tat", ""),
                    "purpose": d.get("tom_tat", ""),
                    "keyPoints": [d.get("tom_tat", "")],
                    "articles": [],
                    "content": f"URL: {d.get('url', '')}\nNguồn: {d.get('nguon', '')}\nLĩnh vực: {d.get('linh_vuc', '')}",
                    "status": "active" if d.get("trang_thai") == "Còn hiệu lực" else ("amended" if d.get("trang_thai") == "Sắp có hiệu lực" else "expired"),
                    "folder": "A",
                    "tags": d.get("tags", []),
                    "relatedDocs": []
                }
                mapped_docs.append(mapped_doc)
            return mapped_docs
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu: {e}")
        return []


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
    "thong-tu": "📄",
    "nghi-dinh": "📜",
    "nghi-quyet": "📝",
    "luat": "⚖️",
    "cong-van": "✉️",
    "quyet-dinh": "🎯",
}

STATUS_NAMES = {
    "active": "Còn hiệu lực",
    "amended": "Sửa đổi",
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
    'cơ', 'không', 'nào', 'là', 'với', 'của', 'cho', 'và', 'hay', 'hoặc',
    'bị', 'được', 'theo', 'từ', 'trong', 'những', 'các', 'một', 'này',
    'đó', 'thì', 'mà', 'để', 'về', 'tới', 'đến', 'khi', 'nếu', 'do',
    'vậy', 'bằng', 'qua', 'trên', 'dưới', 'ra', 'vào', 'lên', 'xuống',
    'lại', 'đi', 'hên', 'như', 'rất', 'quá', 'cũng', 'đã', 'đang',
    'sẽ', 'chưa', 'còn', 'ai', 'gì', 'đâu', 'sao', 'nên', 'phải',
    'có', 'muốn', 'biết', 'hiểu', 'xin', 'hãy', 'cho', 'tôi', 'mình',
    'nhà', 'năm', 'tháng', 'ngày', 'nội', 'dung', 'quy', 'định',
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
        r'cơ.*không', r'là gì', r'bao nhiêu', r'thế nào', r'như thế nào',
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
    if re.search(r'mới nhất|gần đây|latest', q):
        result['sort_by'] = 'newest'
        q = re.sub(r'mới nhất|gần đây|latest', '', q).strip()

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


def internet_search(query: str, max_results=3) -> list:
    """Search internet for real-time legal updates from reputable sources."""
    if DDGS is None:
        return []
    try:
        ddgs = DDGS()
        # Focus on reputable Vietnam legal sites
        search_query = f"{query} site:thuvienphapluat.vn OR site:customs.gov.vn OR site:luatvietnam.vn OR site:chinhphu.vn OR site:moj.gov.vn OR site:moit.gov.vn OR site:baohaiquan.vn"
        results = list(ddgs.text(search_query, region='vn-vi', max_results=max_results))
        return results
    except Exception as e:
        print(f"Internet search error: {e}")
        return []

def generate_answer(query: str, results: list, keywords: list) -> str:
    """Generate a structured answer panel for question queries with live internet search."""
    internet_results = internet_search(query, max_results=3)
    
    if not results and not internet_results:
        return ""

    html = '<div class="answer-panel" style="background: linear-gradient(135deg, rgba(108, 99, 255, 0.15) 0%, rgba(0, 212, 170, 0.08) 100%); border: 1px solid rgba(108, 99, 255, 0.4); box-shadow: 0 8px 32px rgba(108, 99, 255, 0.2);">'
    html += '<div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1.2rem;">'
    html += '<div style="font-size: 2.2rem;">🤖</div>'
    html += '<div>'
    html += '<h3 style="color: #8B85FF !important; margin: 0 !important; font-size: 1.3rem !important; font-weight: 700 !important;">AI TRỢ LÝ PHÁP LUẬT</h3>'
    html += f'<p style="color: #A0AEC0; margin: 0; font-size: 0.85rem; font-style: italic;">Phân tích thời gian thực từ Internet & Dữ liệu nội bộ</p>'
    html += '</div></div>'
    html += f'<div style="background: rgba(14, 17, 23, 0.6); padding: 1rem; border-radius: 12px; border-left: 4px solid #00D4AA; margin-bottom: 1.5rem;">'
    html += f'<strong style="color: #00D4AA;">Câu hỏi của bạn:</strong> <span style="color: #FAFAFA;">"{query}"</span></div>'

    if internet_results:
        html += '<h4 style="color: #00D4AA; margin-bottom: 1rem; border-bottom: 1px solid rgba(0,212,170,0.3); padding-bottom: 0.5rem;">🌐 Cập nhật trực tuyến mới nhất</h4>'
        for i, res in enumerate(internet_results, 1):
            title = res.get('title', '')
            body = res.get('body', '')
            href = res.get('href', '#')
            html += '<div class="answer-item" style="background: rgba(0,212,170,0.05); border-left: 3px solid #00D4AA;">'
            html += f'<div class="answer-item-title" style="margin-bottom: 0.5rem;">'
            html += f'<span style="color: #A0AEC0; font-weight: 600; margin-right: 0.5rem;">{i}.</span>'
            html += f'<a href="{href}" target="_blank" style="color: #00D4AA; text-decoration: none; font-weight: 600;">{title}</a></div>'
            html += f'<div class="answer-item-content" style="padding-left: 1.5rem; color: #cbd5e1; font-size: 0.95rem;">💡 {body}</div>'
            html += '</div>'

    if results:
        html += '<h4 style="color: #8B85FF; margin-top: 1.5rem; margin-bottom: 1rem; border-bottom: 1px solid rgba(139,133,255,0.3); padding-bottom: 0.5rem;">📂 Dữ liệu nội bộ phù hợp nhất</h4>'
        for i, doc in enumerate(results[:3], 1):
            type_name = TYPE_NAMES.get(doc.get('type', ''), doc.get('type', ''))
            badge_class = TYPE_BADGES.get(doc.get('type', ''), '')

            html += '<div class="answer-item" style="background: rgba(255,255,255,0.03); border-left: 3px solid #8B85FF;">'
            html += f'<div class="answer-item-title" style="margin-bottom: 0.5rem;">'
            html += f'<span style="color: #A0AEC0; font-weight: 600; margin-right: 0.5rem;">{i}.</span>'
            html += f'Theo <span class="type-badge {badge_class}">{type_name}</span> '
            html += f'<strong style="color: #FAFAFA;">{doc.get("number", "")}</strong>'

            issue_date = doc.get('issueDate', '')
            if issue_date:
                try:
                    dt = datetime.strptime(issue_date, '%Y-%m-%d')
                    html += f' ({dt.strftime("%d/%m/%Y")})'
                except:
                    pass

            html += ':</div>'

            # Show relevant key points
            key_points = doc.get('keyPoints', [])
            if key_points:
                html += '<div class="answer-item-content" style="padding-left: 1.5rem; color: #cbd5e1; font-size: 0.95rem;">'
                for point in key_points[:3]:
                    highlighted = highlight_text(point, keywords)
                    html += f'💡 {highlighted}<br>'
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

    html += '<div style="text-align: right; margin-top: 1.5rem;">'
    html += '<span style="color: #636E80; font-size: 0.8rem; font-weight: 600;">⚡ Trả lời tự động kết hợp Internet và Dữ liệu nội bộ</span>'
    html += '</div></div>'
    return html


def format_doc_for_download(doc: dict) -> str:
    """Format document as text for download."""
    type_name = TYPE_NAMES.get(doc.get('type', ''), doc.get('type', '')).upper()
    lines = [
        '=' * 80,
        type_name,
        f'S沼? {doc.get("number", "")}',
        '=' * 80,
        '',
        f'TI횎U 휂沼: {doc.get("title", "")}',
        '',
        f'Ng횪y ban h횪nh: {doc.get("issueDate", "N/A")}',
        f'Ng횪y hi沼뇎 l沼켧: {doc.get("effectiveDate", "N/A")}',
        f'C퉤 quan ban h횪nh: {doc.get("issuingBody", "N/A")}',
        f'Tr梳죒g th찼i: {STATUS_NAMES.get(doc.get("status", ""), "N/A")}',
        '',
        '-' * 80,
        'T횙M T梳췛 N沼쁈 DUNG:',
        '-' * 80,
        doc.get('summary', ''),
        '',
        '-' * 80,
        'M沼짡 휂횒CH BAN H?NH:',
        '-' * 80,
        doc.get('purpose', ''),
        '',
        '-' * 80,
        'N沼쁈 DUNG CH횒NH:',
        '-' * 80,
    ]

    for i, point in enumerate(doc.get('keyPoints', []), 1):
        lines.append(f'{i}. {point}')

    if doc.get('articles'):
        lines.extend(['', '-' * 80, 'C횁C 휂I沼U KHO梳줟 QUAN TR沼똍G:', '-' * 80])
        for art in doc['articles']:
            num = art.get('number', '')
            title = art.get('title', '')
            lines.append(f'\n{num}{"." if title else ""} {title}')
            lines.append(art.get('content', ''))

    lines.extend([
        '', '=' * 80,
        'N沼쁈 DUNG 휂梳쫃 휂沼?',
        '=' * 80,
        doc.get('content', ''),
        '', '=' * 80,
        f'Tags: {", ".join(doc.get("tags", []))}',
        f'V훱n b梳즢 li챗n quan: {", ".join(doc.get("relatedDocs", []))}',
        '=' * 80,
    ])

    return '\n'.join(lines)


# ============================================
# RENDER FUNCTIONS
# ============================================
def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>?뽳툘 C沼봏G PH횁P LU梳촖 H梳줚 QUAN VI沼냊 NAM</h1>
        <p>Tra c沼쯷 Th척ng t튼 ??Ngh沼?휃沼땙h ??Ngh沼?quy梳퓍 ??Lu梳춗 ??C척ng v훱n ??Quy梳퓍 휃沼땙h</p>
    </div>
    """, unsafe_allow_html=True)


def render_stats(documents):
    type_counts = {}
    for doc in documents:
        t = doc.get('type', 'other')
        type_counts[t] = type_counts.get(t, 0) + 1

    cols = st.columns(7)
    stats = [
        ("?뱴", len(documents), "T沼븂g v훱n b梳즢", "all"),
        ("?뱲", type_counts.get('thong-tu', 0), "Th척ng t튼", "thong-tu"),
        ("?뱱", type_counts.get('nghi-dinh', 0), "Ngh沼?휃沼땙h", "nghi-dinh"),
        ("?뱯", type_counts.get('nghi-quyet', 0), "Ngh沼?quy梳퓍", "nghi-quyet"),
        ("?뱳", type_counts.get('luat', 0), "Lu梳춗", "luat"),
        ("?뱞", type_counts.get('cong-van', 0), "C척ng v훱n", "cong-van"),
        ("?뱥", type_counts.get('quyet-dinh', 0), "Quy梳퓍 휃沼땙h", "quyet-dinh"),
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
        <div class="doc-card-meta">?뱟 {formatted_date} ??{doc.get('issuingBody', '')}</div>
        <div class="doc-card-summary">{summary}...</div>
    </div>
    """, unsafe_allow_html=True)


def render_doc_detail(doc, keywords=None):
    """Render full document detail."""
    doc_type = doc.get('type', '')
    badge_class = TYPE_BADGES.get(doc_type, '')
    type_name = TYPE_NAMES.get(doc_type, doc_type)
    type_icon = TYPE_ICONS.get(doc_type, '?뱞')
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
                st.markdown(f"?뱟 **Ng횪y ban h횪nh:** {dt.strftime('%d/%m/%Y')}")
            except:
                st.markdown(f"?뱟 **Ng횪y ban h횪nh:** {issue_date}")
    with col2:
        eff_date = doc.get('effectiveDate', '')
        if eff_date:
            try:
                dt = datetime.strptime(eff_date, '%Y-%m-%d')
                st.markdown(f"?뱠 **Ng횪y hi沼뇎 l沼켧:** {dt.strftime('%d/%m/%Y')}")
            except:
                st.markdown(f"?뱠 **Ng횪y hi沼뇎 l沼켧:** {eff_date}")
    with col3:
        st.markdown(f"?룢截?**C퉤 quan:** {doc.get('issuingBody', 'N/A')}")

    st.divider()

    # Summary
    summary = doc.get('summary', '')
    if keywords:
        summary = highlight_text(summary, keywords)
    st.markdown(f"""
    <div class="detail-section">
        <h4>?뱷 T횙M T梳췛 N沼쁈 DUNG</h4>
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
            <h4>?렞 M沼짡 휂횒CH BAN H?NH</h4>
            <div style="color:#e2e8f0;font-size:0.9rem;line-height:1.7;">{purpose}</div>
        </div>
        """, unsafe_allow_html=True)

    # Key Points
    key_points = doc.get('keyPoints', [])
    if key_points:
        points_html = '<div class="detail-section"><h4>?뱦 N沼쁈 DUNG CH횒NH</h4><ul>'
        for point in key_points:
            p = highlight_text(point, keywords) if keywords else point
            points_html += f'<li style="color:#e2e8f0;font-size:0.88rem;margin-bottom:0.5rem;line-height:1.5;">{p}</li>'
        points_html += '</ul></div>'
        st.markdown(points_html, unsafe_allow_html=True)

    # Articles
    articles = doc.get('articles', [])
    if articles:
        st.markdown('<div class="detail-section"><h4>?뱰 C횁C 휂I沼U KHO梳줟 QUAN TR沼똍G</h4></div>', unsafe_allow_html=True)
        for art in articles:
            art_num = art.get('number', '')
            art_title = art.get('title', '')
            art_content = art.get('content', '')
            if keywords:
                art_title = highlight_text(art_title, keywords)
                art_content = highlight_text(art_content, keywords)
            header = f"{art_num}" + (f". {art_title}" if art_title else "")
            with st.expander(f"?뱶 {art.get('number', '')} - {art.get('title', '')}", expanded=False):
                st.markdown(f"""
                <div class="article-content">{art_content}</div>
                """, unsafe_allow_html=True)

    # Full Content
    content = doc.get('content', '')
    if content:
        with st.expander("?뱞 XEM N沼쁈 DUNG 휂梳쫃 휂沼?, expanded=False):
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
            label=f"?뮶 T梳즜 xu沼몁g (Folder {folder})",
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


def render_footer():
    st.markdown("""
    <div class="footer">
        <p>?뽳툘 <strong>C沼븂g Ph찼p Lu梳춗 H梳즜 Quan Vi沼뇍 Nam</strong></p>
        <p>D沼?li沼뇎 tham kh梳즣 t沼? thuvienphapluat.vn ??customs.gov.vn ??chinhphu.vn</p>
        <p>?벁 tinnam888888_haiquan.streamlit.app</p>
        <p style="margin-top:0.5rem;">짤 2024-2026 | C梳춑 nh梳춗 li챗n t沼쩭 c찼c v훱n b梳즢 m沼쌻 nh梳쩿</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# MAIN APP
# ============================================
def main():
    documents = load_documents()

    # Header
    render_header()

    # Search
    col_search, col_btn = st.columns([6, 1])
    with col_search:
        query = st.text_input(
            "?뵇 T챙m ki梳퓅",
            placeholder="Nh梳춑 c창u h沼뢩 ho梳톍 t沼?kh처a, VD: t梳죑 nh梳춑 t찼i xu梳쩿 c처 b沼?n沼셮 thu梳?kh척ng...",
            label_visibility="collapsed",
            key="search_input",
        )
    with col_btn:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        search_clicked = st.button("?뵇 T챙m", use_container_width=True, type="primary")

    # Quick search tags
    st.markdown("""
    <div style="text-align:center;margin-bottom:1.5rem;">
        <span style="color:#64748b;font-size:0.8rem;">G沼즜 첵: </span>
        <span class="quick-tag">T梳죑 nh梳춑 t찼i xu梳쩿</span>
        <span class="quick-tag">Thu梳?xu梳쩿 kh梳쯷</span>
        <span class="quick-tag">Th沼?t沼쩭 th척ng quan</span>
        <span class="quick-tag">Quy t梳칌 xu梳쩿 x沼?C/O</span>
        <span class="quick-tag">Kho ngo梳죍 quan</span>
        <span class="quick-tag">Gia c척ng xu梳쩿 kh梳쯷</span>
        <span class="quick-tag">M찾 lo梳죍 h챙nh G13</span>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    render_stats(documents)
    st.markdown("<br>", unsafe_allow_html=True)

    # Filters
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 1, 1, 1])
    with filter_col1:
        type_options = ["T梳쩿 c梳?] + [TYPE_NAMES[t] for t in TYPE_NAMES]
        selected_type = st.selectbox("?뱛 Lo梳죍 v훱n b梳즢", type_options, label_visibility="visible")
    with filter_col2:
        status_options = ["T梳쩿 c梳?, "C챵n hi沼뇎 l沼켧", "휂찾 s沼춁 휃沼뷼", "H梳퓍 hi沼뇎 l沼켧"]
        selected_status = st.selectbox("?뱦 Tr梳죒g th찼i", status_options)
    with filter_col3:
        years = sorted(set(d.get('issueDate', '')[:4] for d in documents if d.get('issueDate')), reverse=True)
        year_options = ["T梳쩿 c梳?] + years
        selected_year = st.selectbox("?뱟 N훱m", year_options)
    with filter_col4:
        sort_options = {"M沼쌻 nh梳쩿": "newest", "C크 nh梳쩿": "oldest", "Li챗n quan nh梳쩿": "relevance"}
        selected_sort = st.selectbox("?봼 S梳칛 x梳퓈", list(sort_options.keys()))

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
    if selected_type != "T梳쩿 c梳?:
        type_key = [k for k, v in TYPE_NAMES.items() if v == selected_type]
        if type_key:
            filtered_docs = [d for d in filtered_docs if d.get('type') == type_key[0]]

    # Apply status filter
    status_map = {"C챵n hi沼뇎 l沼켧": "active", "휂찾 s沼춁 휃沼뷼": "amended", "H梳퓍 hi沼뇎 l沼켧": "expired"}
    if selected_status != "T梳쩿 c梳?:
        s = status_map.get(selected_status)
        if s:
            filtered_docs = [d for d in filtered_docs if d.get('status') == s]

    # Apply year filter
    if selected_year != "T梳쩿 c梳?:
        filtered_docs = [d for d in filtered_docs if d.get('issueDate', '').startswith(selected_year)]

    # Apply sort (only if not search-relevance)
    sort_key = sort_options[selected_sort]
    if sort_key == 'newest':
        filtered_docs.sort(key=lambda d: d.get('issueDate', ''), reverse=True)
    elif sort_key == 'oldest':
        filtered_docs.sort(key=lambda d: d.get('issueDate', ''))

    # Smart Answer Panel (for questions)
    if query and parsed and parsed['is_question'] and filtered_docs:
        answer_html = generate_answer(query, filtered_docs, keywords)
        st.markdown(answer_html, unsafe_allow_html=True)

    # Results count
    if query:
        st.markdown(
            f'<p style="color:#94a3b8;font-size:0.9rem;">?뵇 T챙m th梳쪅 <strong style="color:#6366f1;">'
            f'{len(filtered_docs)}</strong> k梳퓍 qu梳?cho "<em>{query}</em>"</p>',
            unsafe_allow_html=True
        )

    # Document list & detail
    if not filtered_docs:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#64748b;">
            <div style="font-size:3rem;">?벊</div>
            <h3 style="color:#94a3b8;">Kh척ng t챙m th梳쪅 v훱n b梳즢 n횪o</h3>
            <p>Th沼?thay 휃沼뷼 t沼?kh처a ho梳톍 b沼?l沼뛠</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Two-column layout: list + detail
        col_list, col_detail = st.columns([2, 3])

        with col_list:
            st.markdown(f"**?뱴 Danh s찼ch ({len(filtered_docs)} v훱n b梳즢)**")

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
                if st.button(f"?뱰 Xem chi ti梳퓍", key=f"btn_{doc['id']}", use_container_width=True):
                    st.session_state.selected_doc = doc['id']
                    st.rerun()

            # Pagination controls
            if total_pages > 1:
                pg_cols = st.columns([1, 2, 1])
                with pg_cols[0]:
                    if st.button("? Tr튼沼쌵", disabled=st.session_state.current_page <= 1):
                        st.session_state.current_page -= 1
                        st.rerun()
                with pg_cols[1]:
                    st.markdown(
                        f'<p style="text-align:center;color:#94a3b8;">Trang {st.session_state.current_page}/{total_pages}</p>',
                        unsafe_allow_html=True
                    )
                with pg_cols[2]:
                    if st.button("Sau ??, disabled=st.session_state.current_page >= total_pages):
                        st.session_state.current_page += 1
                        st.rerun()

        with col_detail:
            selected_id = st.session_state.get('selected_doc')

            if selected_id:
                doc = next((d for d in documents if d['id'] == selected_id), None)
                if doc:
                    st.markdown("**?뱞 Chi ti梳퓍 v훱n b梳즢**")
                    render_doc_detail(doc, keywords)
                else:
                    st.info("Ch沼뛫 m沼셳 v훱n b梳즢 t沼?danh s찼ch b챗n tr찼i 휃沼?xem chi ti梳퓍.")
            else:
                # Show first document by default
                if filtered_docs:
                    st.markdown("**?뱞 Chi ti梳퓍 v훱n b梳즢**")
                    st.info("?몚 Nh梳쩸 **Xem chi ti梳퓍** 沼?danh s찼ch b챗n tr찼i 휃沼?xem n沼셢 dung v훱n b梳즢.")

    # Footer
    render_footer()


if __name__ == "__main__":
    main()
