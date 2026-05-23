"""
🏛️ HỆ THỐNG TRA CỨU VĂN BẢN PHÁP LUẬT
Hải quan | Kế toán | Xuất nhập khẩu | Thuế | Incoterms
===================================================
Tự động cập nhật từ: customs.gov.vn, thuvienphapluat.vn, vbpl.vn
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json
import math

# Local imports
from utils.data_manager import load_documents, get_statistics, get_incoterms
from utils.search_engine import (
    search_documents,
    highlight_text,
    get_unique_values,
    get_all_tags,
)
from utils.ai_search import perform_ai_search

# =============================================
# PAGE CONFIG
# =============================================

st.set_page_config(
    page_title="Tra Cứu Văn Bản Pháp Luật | Hải Quan - Kế Toán - XNK",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Hệ thống tra cứu văn bản pháp luật tự động - Hải quan, Kế toán, Xuất nhập khẩu, Thuế, Incoterms",
    },
)

# =============================================
# LOAD CSS
# =============================================

def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()


# =============================================
# LOAD DATA WITH CACHE
# =============================================

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_data():
    """Load and cache document data."""
    data = load_documents()
    return data


@st.cache_data(ttl=1800)
def load_stats(documents_json: str):
    """Load and cache statistics (uses JSON string for hashing)."""
    documents = json.loads(documents_json)
    return get_statistics(documents)


# =============================================
# HELPER FUNCTIONS
# =============================================

def get_badge_class(doc_type: str) -> str:
    """Get CSS badge class for document type."""
    mapping = {
        "Nghị định": "badge-nghi-dinh",
        "Thông tư": "badge-thong-tu",
        "Quyết định": "badge-quyet-dinh",
        "Công văn": "badge-cong-van",
        "Luật": "badge-luat",
        "Nghị quyết": "badge-nghi-quyet",
    }
    return mapping.get(doc_type, "badge-default")


def get_status_icon(status: str) -> str:
    """Get status icon and color."""
    mapping = {
        "Còn hiệu lực": "🟢",
        "Sắp có hiệu lực": "🟡",
        "Hết hiệu lực": "🔴",
    }
    return mapping.get(status, "⚪")


def format_date_vi(date_str: str) -> str:
    """Format date string to Vietnamese format."""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return date_str


def get_category_icon(category: str) -> str:
    """Get icon for document category."""
    mapping = {
        "Hải quan": "🛃",
        "Kế toán - Kiểm toán": "📊",
        "Xuất nhập khẩu": "🚢",
        "Thuế - Phí - Lệ phí": "💰",
        "Thương mại quốc tế": "🌍",
        "Doanh nghiệp": "🏢",
        "Lao động - Tiền lương": "👷",
        "Tài chính - Ngân hàng": "🏦",
        "Đầu tư": "📈",
        "Ngoại hối": "💱",
        "Bảo hiểm": "🛡️",
        "Công nghệ thông tin": "💻",
        "An toàn thực phẩm": "🍎",
        "Nông nghiệp": "🌾",
        "Thương mại điện tử": "🛒",
    }
    return mapping.get(category, "📄")


# =============================================
# RENDER HEADER
# =============================================

def render_header():
    """Render the premium header banner."""
    with st.container(key="header_banner"):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            # 🏛️ Tra Cứu Văn Bản Pháp Luật
            **Hải Quan** · **Kế Toán** · **Xuất Nhập Khẩu** · **Thuế** · **Incoterms**
            """)
        with col2:
            # Last updated info
            data = load_data()
            last_updated = data.get("last_updated", "N/A")
            if last_updated != "N/A":
                try:
                    dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                    last_updated = dt.strftime("%d/%m/%Y %H:%M")
                except (ValueError, AttributeError):
                    pass
            st.markdown(f"""
            <div style="text-align: right; padding-top: 1rem;">
                <span style="color: #2ED573; font-size: 0.7rem;">● TRỰC TUYẾN</span><br>
                <span style="color: #A0AEC0; font-size: 0.75rem;">Cập nhật: {last_updated}</span><br>
                <span style="color: #636E80; font-size: 0.7rem;">{data.get('total_documents', 0)} văn bản</span>
            </div>
            """, unsafe_allow_html=True)


# =============================================
# RENDER METRICS
# =============================================

def render_metrics(stats: dict):
    """Render metric cards."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        with st.container(key="metric_card"):
            st.metric(
                label="📚 TỔNG VĂN BẢN",
                value=f"{stats['total']:,}",
            )

    with col2:
        with st.container(key="metric_card"):
            st.metric(
                label="📅 TUẦN NÀY",
                value=f"{stats['this_week']:,}",
                delta=f"+{stats['this_week']}" if stats['this_week'] > 0 else None,
            )

    with col3:
        with st.container(key="metric_card"):
            st.metric(
                label="📆 THÁNG NÀY",
                value=f"{stats['this_month']:,}",
            )

    with col4:
        with st.container(key="metric_card"):
            active = stats["by_status"].get("Còn hiệu lực", 0)
            st.metric(
                label="✅ CÒN HIỆU LỰC",
                value=f"{active:,}",
            )

    with col5:
        with st.container(key="metric_card"):
            upcoming = stats["by_status"].get("Sắp có hiệu lực", 0)
            st.metric(
                label="⏳ SẮP HIỆU LỰC",
                value=f"{upcoming:,}",
            )


# =============================================
# RENDER DOCUMENT CARD
# =============================================

def render_document_card(doc: dict, query: str = ""):
    """Render a single document card."""
    badge_class = get_badge_class(doc.get("loai_van_ban", ""))
    status_icon = get_status_icon(doc.get("trang_thai", ""))
    category_icon = get_category_icon(doc.get("linh_vuc", ""))

    # Highlight summary if query
    summary = doc.get("tom_tat", "")
    if query:
        summary = highlight_text(summary, query, 250)
    else:
        summary = summary[:250] + ("..." if len(summary) > 250 else "")

    # Tags HTML
    tags_html = ""
    for tag in doc.get("tags", [])[:5]:
        tags_html += f'<span class="category-tag">{tag}</span>'

    # Card HTML
    card_html = f"""
    <div style="
        background: rgba(26, 31, 46, 0.7);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
            <div>
                <span class="badge {badge_class}">{doc.get('loai_van_ban', '')}</span>
                <span style="color: #636E80; font-size: 0.8rem; margin-left: 0.5rem;">
                    {doc.get('so_hieu', '')}
                </span>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.75rem;">{status_icon} {doc.get('trang_thai', '')}</span>
            </div>
        </div>
        <h4 style="color: #FAFAFA; font-size: 0.95rem; font-weight: 600; margin: 0.5rem 0; line-height: 1.5;">
            {doc.get('tieu_de', '')}
        </h4>
        <p style="color: #A0AEC0; font-size: 0.82rem; line-height: 1.6; margin: 0.5rem 0;">
            {summary}
        </p>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.8rem; flex-wrap: wrap; gap: 0.3rem;">
            <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
                <span style="color: #636E80; font-size: 0.75rem;">
                    {category_icon} {doc.get('linh_vuc', '')}
                </span>
                <span style="color: #636E80; font-size: 0.75rem;">
                    🏛️ {doc.get('co_quan_ban_hanh', '')}
                </span>
                <span style="color: #636E80; font-size: 0.75rem;">
                    📅 {format_date_vi(doc.get('ngay_ban_hanh', ''))}
                </span>
            </div>
            <div>{tags_html}</div>
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    # Expandable detail
    with st.expander(f"📖 Xem chi tiết - {doc.get('so_hieu', '')}", expanded=False):
        detail_cols = st.columns(2)
        with detail_cols[0]:
            st.markdown(f"**Số hiệu:** {doc.get('so_hieu', 'N/A')}")
            st.markdown(f"**Loại:** {doc.get('loai_van_ban', 'N/A')}")
            st.markdown(f"**Lĩnh vực:** {doc.get('linh_vuc', 'N/A')}")
            st.markdown(f"**Cơ quan:** {doc.get('co_quan_ban_hanh', 'N/A')}")
        with detail_cols[1]:
            st.markdown(f"**Ngày ban hành:** {format_date_vi(doc.get('ngay_ban_hanh', ''))}")
            st.markdown(f"**Ngày hiệu lực:** {format_date_vi(doc.get('ngay_hieu_luc', ''))}")
            st.markdown(f"**Trạng thái:** {get_status_icon(doc.get('trang_thai', ''))} {doc.get('trang_thai', '')}")
            st.markdown(f"**Nguồn:** {doc.get('nguon', 'N/A')}")

        st.markdown("---")
        st.markdown(f"**Tóm tắt:** {doc.get('tom_tat', '')}")

        if doc.get("url"):
            st.link_button("🔗 Xem văn bản gốc", doc["url"], use_container_width=True)


# =============================================
# RENDER SIDEBAR
# =============================================

def render_sidebar():
    """Render sidebar navigation and filters."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="margin: 0; font-size: 1.3rem;">🏛️ VĂN BẢN PL</h2>
            <p style="color: #A0AEC0; font-size: 0.8rem; margin: 0.3rem 0 0 0;">
                Hệ thống tra cứu toàn diện
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        page = st.radio(
            "📌 CHỨC NĂNG",
            options=[
                "🔍 Tra cứu văn bản",
                "📊 Thống kê & Phân tích",
                "🌍 Incoterms 2020",
                "💰 Biểu thuế XNK",
                "📋 Tra cứu mã HS",
                "ℹ️ Giới thiệu",
            ],
            index=0,
            label_visibility="visible",
        )

        st.markdown("---")

        # Quick links
        st.markdown("##### 🔗 Nguồn chính thức")
        st.markdown("""
        - [🏛️ Tổng cục Hải quan](https://customs.gov.vn)
        - [📜 VBPL Chính phủ](https://vbpl.vn)
        - [📚 Thư viện PL](https://thuvienphapluat.vn)
        - [💰 Tổng cục Thuế](https://www.gdt.gov.vn)
        - [📊 Bộ Tài chính](https://www.mof.gov.vn)
        """)

        st.markdown("---")

        # Auto-update status
        st.markdown("""
        <div style="padding: 0.8rem; background: rgba(46, 213, 115, 0.08); border-radius: 8px; border: 1px solid rgba(46, 213, 115, 0.2);">
            <span style="color: #2ED573; font-size: 0.75rem; font-weight: 600;">● TỰ ĐỘNG CẬP NHẬT</span>
            <p style="color: #A0AEC0; font-size: 0.7rem; margin: 0.3rem 0 0 0;">
                Dữ liệu được cập nhật mỗi 6 giờ<br>
                từ 3 nguồn chính thức
            </p>
        </div>
        """, unsafe_allow_html=True)

        return page


# =============================================
# PAGE: SEARCH
# =============================================

def page_search():
    """Main search page."""
    data = load_data()
    documents = data.get("documents", [])
    stats_json = json.dumps(documents)
    stats = load_stats(stats_json)

    # Render metrics
    render_metrics(stats)

    st.markdown("")

    # === Search Bar ===
    with st.container(key="search_container"):
        search_col1, search_col2 = st.columns([4, 1])
        with search_col1:
            query = st.text_input(
                "🔍 Tìm kiếm",
                placeholder="Nhập từ khóa: số hiệu, tiêu đề, nội dung, mã HS, thuế suất...",
                key="search_input",
                label_visibility="collapsed",
            )
        with search_col2:
            sort_by = st.selectbox(
                "Sắp xếp",
                options=["Mới nhất", "Liên quan nhất", "Theo loại", "Theo tên"],
                index=0,
                label_visibility="collapsed",
            )

    sort_mapping = {
        "Mới nhất": "date",
        "Liên quan nhất": "relevance",
        "Theo loại": "type",
        "Theo tên": "title",
    }

    # === Filters ===
    with st.expander("⚙️ Bộ lọc nâng cao", expanded=False):
        filter_cols = st.columns(4)

        with filter_cols[0]:
            doc_types = ["Tất cả"] + sorted(get_unique_values(documents, "loai_van_ban"))
            selected_type = st.selectbox("📋 Loại văn bản", doc_types)

        with filter_cols[1]:
            categories = ["Tất cả"] + sorted(get_unique_values(documents, "linh_vuc"))
            selected_category = st.selectbox("📁 Lĩnh vực", categories)

        with filter_cols[2]:
            statuses = ["Tất cả", "Còn hiệu lực", "Sắp có hiệu lực", "Hết hiệu lực"]
            selected_status = st.selectbox("📊 Trạng thái", statuses)

        with filter_cols[3]:
            authorities = ["Tất cả"] + sorted(get_unique_values(documents, "co_quan_ban_hanh"))
            selected_authority = st.selectbox("🏛️ Cơ quan ban hành", authorities)

        # Date range
        date_cols = st.columns(2)
        with date_cols[0]:
            date_from = st.date_input(
                "📅 Từ ngày",
                value=None,
                format="DD/MM/YYYY",
            )
        with date_cols[1]:
            date_to = st.date_input(
                "📅 Đến ngày",
                value=None,
                format="DD/MM/YYYY",
            )

    # === Category Quick Filter Pills ===
    st.markdown("##### 📁 Lọc nhanh theo lĩnh vực")
    category_pills = [
        "Tất cả", "🛃 Hải quan", "📊 Kế toán", "🚢 XNK",
        "💰 Thuế", "🌍 Thương mại QT", "🏢 Doanh nghiệp", "👷 Lao động"
    ]

    pill_cols = st.columns(len(category_pills))
    quick_category = None
    for i, pill in enumerate(category_pills):
        with pill_cols[i]:
            if st.button(pill, key=f"pill_{i}", use_container_width=True):
                quick_filter_map = {
                    "🛃 Hải quan": "Hải quan",
                    "📊 Kế toán": "Kế toán - Kiểm toán",
                    "🚢 XNK": "Xuất nhập khẩu",
                    "💰 Thuế": "Thuế - Phí - Lệ phí",
                    "🌍 Thương mại QT": "Thương mại quốc tế",
                    "🏢 Doanh nghiệp": "Doanh nghiệp",
                    "👷 Lao động": "Lao động - Tiền lương",
                }
                quick_category = quick_filter_map.get(pill, None)

    # Determine effective category filter
    effective_category = quick_category if quick_category else selected_category

    # === Perform Search ===
    page_num = st.session_state.get("page_num", 1)
    page_size = 15

    if query:
        # AI SEARCH MODE
        with st.spinner("🤖 Trợ lý AI đang tìm kiếm và đọc các thông tư, nghị định mới nhất trên Internet..."):
            ai_results = perform_ai_search(query, api_key="")
            if ai_results:
                results = ai_results
                total_count = len(results)
            else:
                # Fallback to local DB if AI fails to return JSON
                results, total_count = search_documents(
                    documents=documents,
                    query=query,
                    doc_type=selected_type,
                    category=effective_category,
                    status=selected_status,
                    authority=selected_authority,
                    date_from=date_from.strftime("%Y-%m-%d") if date_from else None,
                    date_to=date_to.strftime("%Y-%m-%d") if date_to else None,
                    sort_by=sort_mapping.get(sort_by, "date"),
                    page=page_num,
                    page_size=page_size,
                )
    else:
        # LOCAL MODE (NO QUERY)
        results, total_count = search_documents(
            documents=documents,
            query=query,
            doc_type=selected_type,
            category=effective_category,
            status=selected_status,
            authority=selected_authority,
            date_from=date_from.strftime("%Y-%m-%d") if date_from else None,
            date_to=date_to.strftime("%Y-%m-%d") if date_to else None,
            sort_by=sort_mapping.get(sort_by, "date"),
            page=page_num,
            page_size=page_size,
        )

    # === Results Header ===
    st.markdown("")

    with st.container(key="status_bar"):
        result_col1, result_col2 = st.columns([3, 1])
        with result_col1:
            if query:
                st.markdown(f"🔍 Tìm thấy **{total_count}** kết quả cho \"**{query}**\"")
            else:
                st.markdown(f"📚 Hiển thị **{total_count}** văn bản")
        with result_col2:
            total_pages = max(1, math.ceil(total_count / page_size))
            st.markdown(f"📄 Trang **{page_num}** / **{total_pages}**")

    # === Render Results ===
    if results:
        for doc in results:
            render_document_card(doc, query)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #636E80;">
            <h3 style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</h3>
            <p style="font-size: 1rem;">Không tìm thấy kết quả phù hợp</p>
            <p style="font-size: 0.85rem;">Thử thay đổi từ khóa hoặc bộ lọc</p>
        </div>
        """, unsafe_allow_html=True)

    # === Pagination ===
    if total_count > page_size:
        total_pages = math.ceil(total_count / page_size)
        pag_cols = st.columns([1, 1, 2, 1, 1])

        with pag_cols[0]:
            if st.button("⏮ Đầu", disabled=page_num <= 1):
                st.session_state.page_num = 1
                st.rerun()
        with pag_cols[1]:
            if st.button("◀ Trước", disabled=page_num <= 1):
                st.session_state.page_num = page_num - 1
                st.rerun()
        with pag_cols[2]:
            new_page = st.number_input(
                "Trang", min_value=1, max_value=total_pages,
                value=page_num, step=1, label_visibility="collapsed"
            )
            if new_page != page_num:
                st.session_state.page_num = new_page
                st.rerun()
        with pag_cols[3]:
            if st.button("Sau ▶", disabled=page_num >= total_pages):
                st.session_state.page_num = page_num + 1
                st.rerun()
        with pag_cols[4]:
            if st.button("Cuối ⏭", disabled=page_num >= total_pages):
                st.session_state.page_num = total_pages
                st.rerun()

    # === Export ===
    st.markdown("---")
    export_cols = st.columns([2, 1, 1])
    with export_cols[0]:
        st.markdown("##### 📥 Xuất dữ liệu")
    with export_cols[1]:
        if documents:
            df = pd.DataFrame(documents)
            export_cols_list = ["so_hieu", "tieu_de", "loai_van_ban", "co_quan_ban_hanh",
                               "ngay_ban_hanh", "trang_thai", "linh_vuc", "tom_tat"]
            df_export = df[[c for c in export_cols_list if c in df.columns]]
            csv = df_export.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📊 Tải Excel/CSV",
                data=csv,
                file_name=f"van_ban_phap_luat_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
    with export_cols[2]:
        if documents:
            json_export = json.dumps(documents, ensure_ascii=False, indent=2)
            st.download_button(
                "📋 Tải JSON",
                data=json_export,
                file_name=f"van_ban_phap_luat_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
            )


# =============================================
# PAGE: STATISTICS
# =============================================

def page_statistics():
    """Statistics and analytics page."""
    data = load_data()
    documents = data.get("documents", [])
    stats_json = json.dumps(documents)
    stats = load_stats(stats_json)

    st.markdown("## 📊 Thống Kê & Phân Tích")
    st.markdown("Phân tích dữ liệu văn bản pháp luật theo nhiều chiều")
    st.markdown("")

    # === Render metrics ===
    render_metrics(stats)
    st.markdown("")

    # === Charts Row 1 ===
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(key="chart_container"):
            st.markdown("##### 📋 Phân bổ theo loại văn bản")
            if stats["by_type"]:
                fig = go.Figure(data=[go.Pie(
                    labels=list(stats["by_type"].keys()),
                    values=list(stats["by_type"].values()),
                    hole=0.45,
                    marker=dict(colors=[
                        "#6C63FF", "#00D4AA", "#FFB020", "#1E90FF",
                        "#FF4757", "#2ED573", "#A0AEC0", "#8B85FF"
                    ]),
                    textinfo="label+percent",
                    textfont=dict(size=12, color="#FAFAFA"),
                    hovertemplate="<b>%{label}</b><br>Số lượng: %{value}<br>Tỷ lệ: %{percent}<extra></extra>",
                )])
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#FAFAFA", family="Inter"),
                    showlegend=True,
                    legend=dict(
                        font=dict(size=11, color="#A0AEC0"),
                        bgcolor="rgba(0,0,0,0)",
                    ),
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=350,
                )
                st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        with st.container(key="chart_container"):
            st.markdown("##### 📁 Phân bổ theo lĩnh vực")
            if stats["by_category"]:
                sorted_cats = sorted(stats["by_category"].items(), key=lambda x: x[1], reverse=True)
                fig = go.Figure(data=[go.Bar(
                    x=[v for _, v in sorted_cats],
                    y=[k for k, _ in sorted_cats],
                    orientation="h",
                    marker=dict(
                        color=[v for _, v in sorted_cats],
                        colorscale=[[0, "#1A1F2E"], [0.5, "#00D4AA"], [1, "#6C63FF"]],
                        line=dict(width=0),
                    ),
                    hovertemplate="<b>%{y}</b><br>Số lượng: %{x}<extra></extra>",
                )])
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#FAFAFA", family="Inter"),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title=""),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title=""),
                    margin=dict(t=10, b=20, l=10, r=10),
                    height=350,
                )
                st.plotly_chart(fig, use_container_width=True)

    # === Charts Row 2 ===
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        with st.container(key="chart_container"):
            st.markdown("##### 📊 Trạng thái hiệu lực")
            if stats["by_status"]:
                status_colors = {
                    "Còn hiệu lực": "#2ED573",
                    "Sắp có hiệu lực": "#FFB020",
                    "Hết hiệu lực": "#FF4757",
                }
                fig = go.Figure(data=[go.Pie(
                    labels=list(stats["by_status"].keys()),
                    values=list(stats["by_status"].values()),
                    hole=0.5,
                    marker=dict(colors=[
                        status_colors.get(k, "#A0AEC0") for k in stats["by_status"].keys()
                    ]),
                    textinfo="label+value",
                    textfont=dict(size=12, color="#FAFAFA"),
                )])
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#FAFAFA", family="Inter"),
                    showlegend=False,
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=300,
                )
                st.plotly_chart(fig, use_container_width=True)

    with chart_col4:
        with st.container(key="chart_container"):
            st.markdown("##### 🏛️ Top cơ quan ban hành")
            if stats["by_authority"]:
                sorted_auth = sorted(stats["by_authority"].items(), key=lambda x: x[1], reverse=True)[:8]
                fig = go.Figure(data=[go.Bar(
                    x=[k for k, _ in sorted_auth],
                    y=[v for _, v in sorted_auth],
                    marker=dict(
                        color="#00D4AA",
                        line=dict(width=0),
                    ),
                    hovertemplate="<b>%{x}</b><br>Số lượng: %{y}<extra></extra>",
                )])
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#FAFAFA", family="Inter", size=10),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickangle=-45),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Số văn bản"),
                    margin=dict(t=10, b=80, l=40, r=10),
                    height=300,
                )
                st.plotly_chart(fig, use_container_width=True)

    # === Monthly trend ===
    with st.container(key="chart_container"):
        st.markdown("##### 📈 Xu hướng ban hành theo tháng")
        if stats["by_month"]:
            sorted_months = sorted(stats["by_month"].items())
            fig = go.Figure(data=[go.Scatter(
                x=[k for k, _ in sorted_months],
                y=[v for _, v in sorted_months],
                mode="lines+markers",
                line=dict(color="#00D4AA", width=3),
                marker=dict(size=8, color="#00D4AA", line=dict(width=2, color="#0E1117")),
                fill="tozeroy",
                fillcolor="rgba(0, 212, 170, 0.1)",
                hovertemplate="<b>%{x}</b><br>Số văn bản: %{y}<extra></extra>",
            )])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FAFAFA", family="Inter"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Tháng"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Số văn bản"),
                margin=dict(t=10, b=40, l=40, r=10),
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True)

    # === Popular Tags ===
    st.markdown("##### 🏷️ Tags phổ biến")
    all_tags = get_all_tags(documents)
    if all_tags:
        tags_html = ""
        for tag, count in all_tags[:30]:
            size = max(0.75, min(1.3, 0.7 + count * 0.08))
            opacity = max(0.5, min(1.0, 0.4 + count * 0.06))
            tags_html += f'<span style="display:inline-block; padding:0.3rem 0.8rem; margin:0.2rem; border-radius:20px; background:rgba(0,212,170,{opacity*0.15}); color:rgba(0,212,170,{opacity}); border:1px solid rgba(0,212,170,{opacity*0.3}); font-size:{size}rem; font-weight:500;">{tag} ({count})</span>'

        st.markdown(f'<div style="line-height: 2.5;">{tags_html}</div>', unsafe_allow_html=True)


# =============================================
# PAGE: INCOTERMS
# =============================================

def page_incoterms():
    """Incoterms 2020 reference page."""
    st.markdown("## 🌍 Incoterms® 2020")
    st.markdown("Các điều kiện thương mại quốc tế do Phòng Thương mại Quốc tế (ICC) ban hành")
    st.markdown("")

    incoterms = get_incoterms()

    # Group tabs
    tab_all, tab_any, tab_sea = st.tabs([
        "📋 Tất cả Incoterms",
        "🚛 Mọi phương thức vận tải",
        "🚢 Đường biển / Thủy nội địa",
    ])

    def render_incoterm_card(term: dict):
        """Render a single Incoterm card."""
        group_colors = {"E": "#FF4757", "F": "#FFB020", "C": "#1E90FF", "D": "#2ED573"}
        color = group_colors.get(term["group"], "#A0AEC0")

        card_html = f"""
        <div style="
            background: rgba(26, 31, 46, 0.7);
            border: 1px solid rgba(255,255,255,0.08);
            border-left: 4px solid {color};
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.8rem 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                <div>
                    <span style="font-size: 1.5rem; font-weight: 800; color: {color};">{term['code']}</span>
                    <span style="color: #A0AEC0; font-size: 0.85rem; margin-left: 0.8rem;">{term['name']}</span>
                </div>
                <span style="padding: 0.25rem 0.75rem; border-radius: 20px; background: rgba(255,255,255,0.05); color: #A0AEC0; font-size: 0.75rem; border: 1px solid rgba(255,255,255,0.1);">
                    Nhóm {term['group']} · {term['transport']}
                </span>
            </div>
            <h4 style="color: #FAFAFA; font-size: 1rem; font-weight: 600; margin: 0.3rem 0;">
                {term['name_vi']}
            </h4>
            <p style="color: #A0AEC0; font-size: 0.85rem; line-height: 1.6; margin: 0.8rem 0;">
                {term['description']}
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                <div style="padding: 0.8rem; background: rgba(0, 212, 170, 0.06); border-radius: 8px; border: 1px solid rgba(0, 212, 170, 0.15);">
                    <span style="color: #00D4AA; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">👤 Người bán chịu</span>
                    <p style="color: #FAFAFA; font-size: 0.82rem; margin: 0.3rem 0 0 0; line-height: 1.5;">
                        {term['seller_responsibility']}
                    </p>
                </div>
                <div style="padding: 0.8rem; background: rgba(108, 99, 255, 0.06); border-radius: 8px; border: 1px solid rgba(108, 99, 255, 0.15);">
                    <span style="color: #8B85FF; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">🏪 Người mua chịu</span>
                    <p style="color: #FAFAFA; font-size: 0.82rem; margin: 0.3rem 0 0 0; line-height: 1.5;">
                        {term['buyer_responsibility']}
                    </p>
                </div>
            </div>
            <div style="margin-top: 0.8rem; padding: 0.5rem 0.8rem; background: rgba(255, 176, 32, 0.06); border-radius: 8px; border: 1px solid rgba(255, 176, 32, 0.15);">
                <span style="color: #FFB020; font-size: 0.75rem; font-weight: 600;">⚡ Chuyển rủi ro:</span>
                <span style="color: #FAFAFA; font-size: 0.82rem; margin-left: 0.3rem;">{term['risk_transfer']}</span>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    with tab_all:
        for term in incoterms:
            render_incoterm_card(term)

    with tab_any:
        any_transport = [t for t in incoterms if t["transport"] == "Mọi phương thức"]
        for term in any_transport:
            render_incoterm_card(term)

    with tab_sea:
        sea_transport = [t for t in incoterms if "biển" in t["transport"].lower()]
        for term in sea_transport:
            render_incoterm_card(term)

    # === Comparison table ===
    st.markdown("---")
    st.markdown("### 📊 Bảng so sánh tổng hợp")

    df_incoterms = pd.DataFrame(incoterms)
    df_display = df_incoterms[["code", "name_vi", "group", "transport", "risk_transfer"]].copy()
    df_display.columns = ["Mã", "Tên tiếng Việt", "Nhóm", "Phương thức VT", "Chuyển rủi ro"]
    st.dataframe(df_display, use_container_width=True, hide_index=True)


# =============================================
# PAGE: TAX SCHEDULE
# =============================================

def page_tax_schedule():
    """Tax schedule reference page."""
    st.markdown("## 💰 Biểu Thuế Xuất Nhập Khẩu")
    st.markdown("Tổng hợp các biểu thuế và thuế suất áp dụng cho hàng hóa xuất nhập khẩu")
    st.markdown("")

    # Tax types overview
    tax_tabs = st.tabs([
        "📊 Tổng quan thuế XNK",
        "🌐 Thuế suất FTA",
        "💎 Thuế tiêu thụ đặc biệt",
        "📝 Thuế GTGT hàng NK",
    ])

    with tax_tabs[0]:
        st.markdown("### Các loại thuế áp dụng cho hàng hóa XNK")

        tax_overview = [
            {
                "loai": "Thuế nhập khẩu MFN",
                "muc_thue": "0% - 150%",
                "ap_dung": "Hàng hóa NK từ các nước WTO",
                "co_so": "Biểu thuế NK ưu đãi theo NĐ Chính phủ",
                "color": "#00D4AA",
            },
            {
                "loai": "Thuế nhập khẩu ưu đãi đặc biệt",
                "muc_thue": "0% - 50%",
                "ap_dung": "Hàng hóa NK từ các nước có FTA",
                "co_so": "Theo cam kết FTA (CPTPP, RCEP, EVFTA...)",
                "color": "#6C63FF",
            },
            {
                "loai": "Thuế xuất khẩu",
                "muc_thue": "0% - 45%",
                "ap_dung": "Tài nguyên, khoáng sản, phế liệu XK",
                "co_so": "Biểu thuế XK theo NĐ Chính phủ",
                "color": "#FFB020",
            },
            {
                "loai": "Thuế GTGT hàng NK",
                "muc_thue": "0%, 5%, 8%, 10%",
                "ap_dung": "Hầu hết hàng hóa NK",
                "co_so": "Luật Thuế GTGT",
                "color": "#1E90FF",
            },
            {
                "loai": "Thuế TTĐB hàng NK",
                "muc_thue": "5% - 150%",
                "ap_dung": "Ô tô, rượu, bia, thuốc lá, xăng...",
                "co_so": "Luật Thuế TTĐB",
                "color": "#FF4757",
            },
            {
                "loai": "Thuế bảo vệ môi trường",
                "muc_thue": "300 - 4.000 đ/lít, kg",
                "ap_dung": "Xăng dầu, túi ni-lon, thuốc BVTV...",
                "co_so": "Luật Thuế BVMT",
                "color": "#2ED573",
            },
            {
                "loai": "Thuế chống bán phá giá",
                "muc_thue": "Theo QĐ của BCT",
                "ap_dung": "Hàng hóa bị điều tra CBPG",
                "co_so": "Luật Quản lý ngoại thương",
                "color": "#E056A0",
            },
        ]

        for tax in tax_overview:
            st.markdown(f"""
            <div style="
                background: rgba(26, 31, 46, 0.7);
                border-left: 4px solid {tax['color']};
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
                padding: 1.2rem 1.5rem;
                margin: 0.5rem 0;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="color: {tax['color']}; margin: 0; font-size: 1rem;">{tax['loai']}</h4>
                    <span style="color: #FAFAFA; font-weight: 700; font-size: 1.1rem;">{tax['muc_thue']}</span>
                </div>
                <p style="color: #A0AEC0; font-size: 0.82rem; margin: 0.3rem 0 0 0;">
                    <strong>Áp dụng:</strong> {tax['ap_dung']}<br>
                    <strong>Cơ sở pháp lý:</strong> {tax['co_so']}
                </p>
            </div>
            """, unsafe_allow_html=True)

    with tax_tabs[1]:
        st.markdown("### 🌐 Thuế suất ưu đãi theo FTA")
        st.markdown("Các Hiệp định thương mại tự do mà Việt Nam đang tham gia")

        fta_data = [
            {"fta": "ATIGA (ASEAN)", "thanh_vien": "10 nước ASEAN", "nam": "2010", "thue_suat": "0% - 5%", "form": "D"},
            {"fta": "ACFTA (ASEAN-TQ)", "thanh_vien": "ASEAN + Trung Quốc", "nam": "2010", "thue_suat": "0% - 40%", "form": "E"},
            {"fta": "AKFTA (ASEAN-HQ)", "thanh_vien": "ASEAN + Hàn Quốc", "nam": "2010", "thue_suat": "0% - 50%", "form": "AK"},
            {"fta": "AJCEP (ASEAN-NB)", "thanh_vien": "ASEAN + Nhật Bản", "nam": "2008", "thue_suat": "0% - 50%", "form": "AJ"},
            {"fta": "VJEPA (VN-NB)", "thanh_vien": "Việt Nam + Nhật Bản", "nam": "2009", "thue_suat": "0% - 50%", "form": "VJ"},
            {"fta": "VKFTA (VN-HQ)", "thanh_vien": "Việt Nam + Hàn Quốc", "nam": "2015", "thue_suat": "0% - 50%", "form": "VK"},
            {"fta": "CPTPP", "thanh_vien": "11 nước TP", "nam": "2019", "thue_suat": "0% - 50%", "form": "CPTPP"},
            {"fta": "EVFTA (VN-EU)", "thanh_vien": "Việt Nam + EU 27", "nam": "2020", "thue_suat": "0% - 50%", "form": "EUR.1"},
            {"fta": "UKVFTA (VN-UK)", "thanh_vien": "Việt Nam + Anh", "nam": "2021", "thue_suat": "0% - 50%", "form": "UK"},
            {"fta": "RCEP", "thanh_vien": "15 nước CA-TBD", "nam": "2022", "thue_suat": "0% - 50%", "form": "RCEP"},
        ]

        df_fta = pd.DataFrame(fta_data)
        df_fta.columns = ["Hiệp định", "Thành viên", "Năm", "Thuế suất", "C/O Form"]
        st.dataframe(df_fta, use_container_width=True, hide_index=True)

        st.info("💡 **Lưu ý:** Để được hưởng thuế suất ưu đãi FTA, hàng hóa phải đáp ứng quy tắc xuất xứ và có chứng nhận xuất xứ (C/O) phù hợp.")

    with tax_tabs[2]:
        st.markdown("### 💎 Thuế Tiêu Thụ Đặc Biệt (TTĐB)")
        st.markdown("Áp dụng đối với một số hàng hóa nhập khẩu")

        ttdb_data = [
            {"mat_hang": "Ô tô dưới 9 chỗ (≤1500cc)", "thue_suat": "35%"},
            {"mat_hang": "Ô tô dưới 9 chỗ (1500-2000cc)", "thue_suat": "40%"},
            {"mat_hang": "Ô tô dưới 9 chỗ (2000-2500cc)", "thue_suat": "50%"},
            {"mat_hang": "Ô tô dưới 9 chỗ (2500-3000cc)", "thue_suat": "60%"},
            {"mat_hang": "Ô tô dưới 9 chỗ (>3000cc)", "thue_suat": "150%"},
            {"mat_hang": "Rượu từ 20 độ trở lên", "thue_suat": "65%"},
            {"mat_hang": "Rượu dưới 20 độ", "thue_suat": "35%"},
            {"mat_hang": "Bia", "thue_suat": "65%"},
            {"mat_hang": "Thuốc lá điếu", "thue_suat": "75%"},
            {"mat_hang": "Xì gà", "thue_suat": "75%"},
            {"mat_hang": "Xăng RON 95", "thue_suat": "10%"},
            {"mat_hang": "Điều hòa nhiệt độ ≤90.000 BTU", "thue_suat": "10%"},
        ]

        df_ttdb = pd.DataFrame(ttdb_data)
        df_ttdb.columns = ["Mặt hàng", "Thuế suất TTĐB"]
        st.dataframe(df_ttdb, use_container_width=True, hide_index=True)

    with tax_tabs[3]:
        st.markdown("### 📝 Thuế GTGT đối với hàng hóa nhập khẩu")

        gtgt_data = [
            {"nhom": "Nhóm thuế suất 0%", "hang_hoa": "Hàng hóa XK, hàng gia công XK, hàng XK tại chỗ, hàng vào khu phi thuế quan", "ghi_chu": "Theo Điều 9 Luật Thuế GTGT"},
            {"nhom": "Nhóm thuế suất 5%", "hang_hoa": "Nước sạch, phân bón, thức ăn chăn nuôi, thiết bị y tế, SGK, đồ chơi trẻ em, dịch vụ khoa học công nghệ", "ghi_chu": "Theo Điều 10 Luật Thuế GTGT"},
            {"nhom": "Nhóm thuế suất 8%", "hang_hoa": "Nhiều mặt hàng công nghiệp, dịch vụ (áp dụng trong giai đoạn giảm thuế)", "ghi_chu": "Theo Nghị quyết Quốc hội (nếu có)"},
            {"nhom": "Nhóm thuế suất 10%", "hang_hoa": "Hầu hết hàng hóa, dịch vụ không thuộc diện 0%, 5%, không chịu thuế", "ghi_chu": "Thuế suất phổ thông"},
        ]

        for item in gtgt_data:
            st.markdown(f"""
            <div style="background: rgba(26, 31, 46, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;">
                <h4 style="color: #00D4AA; margin: 0 0 0.5rem 0;">{item['nhom']}</h4>
                <p style="color: #FAFAFA; font-size: 0.85rem; margin: 0;">{item['hang_hoa']}</p>
                <p style="color: #636E80; font-size: 0.75rem; margin: 0.3rem 0 0 0; font-style: italic;">{item['ghi_chu']}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        st.warning("⚠️ **Công thức tính thuế GTGT hàng NK:** Thuế GTGT = (Trị giá tính thuế NK + Thuế NK + Thuế TTĐB) × Thuế suất GTGT")


# =============================================
# PAGE: HS CODE LOOKUP
# =============================================

def page_hs_code():
    """HS Code lookup page."""
    st.markdown("## 📋 Tra Cứu Mã HS")
    st.markdown("Hệ thống hài hòa mô tả và mã hóa hàng hóa (HS - Harmonized System)")
    st.markdown("")

    # HS Code Structure explanation
    st.markdown("""
    <div style="background: rgba(26, 31, 46, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
        <h4 style="color: #00D4AA; margin: 0 0 1rem 0;">📖 Cấu trúc mã HS</h4>
        <div style="display: flex; gap: 0; margin: 0.5rem 0; font-family: 'JetBrains Mono', monospace;">
            <span style="background: #FF4757; color: white; padding: 0.8rem 1rem; font-size: 1.2rem; font-weight: 700; border-radius: 8px 0 0 8px;">XX</span>
            <span style="background: #FFB020; color: #0E1117; padding: 0.8rem 1rem; font-size: 1.2rem; font-weight: 700;">XX</span>
            <span style="background: #1E90FF; color: white; padding: 0.8rem 1rem; font-size: 1.2rem; font-weight: 700;">XX</span>
            <span style="background: #2ED573; color: #0E1117; padding: 0.8rem 1rem; font-size: 1.2rem; font-weight: 700;">.</span>
            <span style="background: #6C63FF; color: white; padding: 0.8rem 1rem; font-size: 1.2rem; font-weight: 700; border-radius: 0 8px 8px 0;">XX</span>
        </div>
        <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">
            <span style="color: #FF4757; font-size: 0.8rem; flex:1; text-align: center;">Chương<br>(2 số)</span>
            <span style="color: #FFB020; font-size: 0.8rem; flex:1; text-align: center;">Nhóm<br>(4 số)</span>
            <span style="color: #1E90FF; font-size: 0.8rem; flex:1; text-align: center;">Phân nhóm<br>(6 số - WCO)</span>
            <span style="color: #6C63FF; font-size: 0.8rem; flex:1; text-align: center;">Chi tiết VN<br>(8 số)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sample HS chapters
    st.markdown("### 📑 Các phần của Biểu thuế (97 chương)")

    hs_sections = [
        {"phan": "I", "chuong": "01-05", "mo_ta": "Động vật sống và sản phẩm từ động vật", "icon": "🐄"},
        {"phan": "II", "chuong": "06-14", "mo_ta": "Sản phẩm thực vật", "icon": "🌿"},
        {"phan": "III", "chuong": "15", "mo_ta": "Chất béo, dầu động/thực vật", "icon": "🫒"},
        {"phan": "IV", "chuong": "16-24", "mo_ta": "Thực phẩm chế biến, đồ uống, thuốc lá", "icon": "🍕"},
        {"phan": "V", "chuong": "25-27", "mo_ta": "Khoáng sản", "icon": "⛏️"},
        {"phan": "VI", "chuong": "28-38", "mo_ta": "Sản phẩm hóa chất", "icon": "🧪"},
        {"phan": "VII", "chuong": "39-40", "mo_ta": "Plastic, cao su và sản phẩm", "icon": "♻️"},
        {"phan": "VIII", "chuong": "41-43", "mo_ta": "Da, lông thú và sản phẩm", "icon": "👜"},
        {"phan": "IX", "chuong": "44-46", "mo_ta": "Gỗ, than gỗ, lie và sản phẩm", "icon": "🪵"},
        {"phan": "X", "chuong": "47-49", "mo_ta": "Bột giấy, giấy và sản phẩm", "icon": "📰"},
        {"phan": "XI", "chuong": "50-63", "mo_ta": "Hàng dệt may", "icon": "👕"},
        {"phan": "XII", "chuong": "64-67", "mo_ta": "Giày dép, mũ nón, ô dù", "icon": "👟"},
        {"phan": "XIII", "chuong": "68-70", "mo_ta": "Sản phẩm từ đá, gốm sứ, thủy tinh", "icon": "🏺"},
        {"phan": "XIV", "chuong": "71", "mo_ta": "Ngọc trai, đá quý, kim loại quý", "icon": "💎"},
        {"phan": "XV", "chuong": "72-83", "mo_ta": "Kim loại cơ bản và sản phẩm", "icon": "⚙️"},
        {"phan": "XVI", "chuong": "84-85", "mo_ta": "Máy móc, thiết bị điện, điện tử", "icon": "💻"},
        {"phan": "XVII", "chuong": "86-89", "mo_ta": "Phương tiện vận tải", "icon": "🚗"},
        {"phan": "XVIII", "chuong": "90-92", "mo_ta": "Dụng cụ quang học, y tế, nhạc cụ", "icon": "🔬"},
        {"phan": "XIX", "chuong": "93", "mo_ta": "Vũ khí, đạn dược", "icon": "🔫"},
        {"phan": "XX", "chuong": "94-96", "mo_ta": "Hàng hóa khác (nội thất, đồ chơi...)", "icon": "🪑"},
        {"phan": "XXI", "chuong": "97", "mo_ta": "Các tác phẩm nghệ thuật, đồ sưu tầm, đồ cổ", "icon": "🎨"},
    ]

    cols_per_row = 3
    for i in range(0, len(hs_sections), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(hs_sections):
                section = hs_sections[idx]
                with col:
                    st.markdown(f"""
                    <div style="
                        background: rgba(26, 31, 46, 0.7);
                        border: 1px solid rgba(255,255,255,0.08);
                        border-radius: 12px;
                        padding: 1rem;
                        margin: 0.3rem 0;
                        min-height: 100px;
                    ">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
                            <span style="font-size: 1.3rem;">{section['icon']}</span>
                            <span style="color: #00D4AA; font-weight: 700; font-size: 0.85rem;">Phần {section['phan']}</span>
                            <span style="color: #636E80; font-size: 0.75rem;">Ch. {section['chuong']}</span>
                        </div>
                        <p style="color: #FAFAFA; font-size: 0.8rem; margin: 0; line-height: 1.4;">{section['mo_ta']}</p>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **Tra cứu chi tiết mã HS:** Truy cập [Biểu thuế XNK - Tổng cục Hải quan](https://www.customs.gov.vn/index.jsp?pageId=24) hoặc [Danh mục HS - Thư viện Pháp luật](https://thuvienphapluat.vn/page/ma-hs.aspx)")


# =============================================
# PAGE: ABOUT
# =============================================

def page_about():
    """About page."""
    st.markdown("## ℹ️ Giới Thiệu Hệ Thống")
    st.markdown("")

    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(0, 212, 170, 0.08), rgba(108, 99, 255, 0.08)); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 2rem; margin: 1rem 0;">
        <h3 style="color: #FAFAFA; margin: 0 0 1rem 0;">🏛️ Hệ Thống Tra Cứu Văn Bản Pháp Luật Toàn Diện</h3>
        <p style="color: #A0AEC0; font-size: 0.9rem; line-height: 1.8;">
            Ứng dụng được xây dựng nhằm hỗ trợ doanh nghiệp xuất nhập khẩu, kế toán viên, nhân viên hải quan
            và các chuyên gia thương mại quốc tế tra cứu nhanh chóng và chính xác các văn bản pháp luật mới nhất.
        </p>
    </div>
    """, unsafe_allow_html=True)

    feature_col1, feature_col2 = st.columns(2)

    with feature_col1:
        st.markdown("""
        ### ✨ Tính năng chính

        - 🔍 **Tra cứu thông minh** - Full-text search + fuzzy matching
        - 📊 **Thống kê trực quan** - Charts phân tích đa chiều
        - 🌍 **Incoterms 2020** - Tra cứu đầy đủ 11 điều kiện
        - 💰 **Biểu thuế XNK** - Tổng hợp thuế suất & FTA
        - 📋 **Mã HS** - Cấu trúc 97 chương biểu thuế
        - 📥 **Xuất dữ liệu** - Export CSV/JSON
        - 🔄 **Tự động cập nhật** - Mỗi 6 giờ qua GitHub Actions
        """)

    with feature_col2:
        st.markdown("""
        ### 📚 Phạm vi bao phủ

        - 🛃 Hải quan & Thông quan
        - 📊 Kế toán & Kiểm toán
        - 🚢 Xuất nhập khẩu
        - 💰 Thuế (GTGT, TNDN, TNCN, XNK)
        - 🌍 Thương mại quốc tế & FTA
        - 🏢 Doanh nghiệp & Đầu tư
        - 👷 Lao động & Bảo hiểm
        - 🏦 Tài chính & Ngân hàng
        """)

    st.markdown("---")

    st.markdown("""
    ### 🔄 Quy trình cập nhật tự động

    ```
    GitHub Actions (mỗi 6 giờ)
    ├── 1. Khởi động crawler
    │   ├── customs.gov.vn     → Văn bản Hải quan
    │   ├── thuvienphapluat.vn → Văn bản đa lĩnh vực
    │   └── vbpl.vn            → CSDL VBPL quốc gia
    ├── 2. Xử lý dữ liệu
    │   ├── Phân loại tự động (AI)
    │   ├── Trích xuất metadata
    │   └── Loại bỏ trùng lặp
    ├── 3. Lưu trữ
    │   └── Commit → GitHub repo
    └── 4. Triển khai
        └── Streamlit Cloud auto-redeploy
    ```
    """)

    st.markdown("---")

    st.markdown("""
    ### ⚠️ Lưu ý quan trọng

    > Hệ thống này được xây dựng với mục đích **hỗ trợ tra cứu tham khảo**.
    > Mọi thông tin cần được đối chiếu với **nguồn chính thức** trước khi áp dụng:
    > - [customs.gov.vn](https://customs.gov.vn) - Tổng cục Hải quan
    > - [vbpl.vn](https://vbpl.vn) - Cơ sở dữ liệu VBPL quốc gia
    > - [thuvienphapluat.vn](https://thuvienphapluat.vn) - Thư viện Pháp luật
    """)


# =============================================
# MAIN APP
# =============================================

def main():
    """Main application entry point."""
    # Initialize session state
    if "page_num" not in st.session_state:
        st.session_state.page_num = 1

    # Render header
    render_header()

    # Render sidebar and get selected page
    selected_page = render_sidebar()

    # Route to selected page
    if "Tra cứu" in selected_page:
        page_search()
    elif "Thống kê" in selected_page:
        page_statistics()
    elif "Incoterms" in selected_page:
        page_incoterms()
    elif "Biểu thuế" in selected_page:
        page_tax_schedule()
    elif "Mã HS" in selected_page:
        page_hs_code()
    elif "Giới thiệu" in selected_page:
        page_about()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; color: #636E80; font-size: 0.75rem;">
        <p>🏛️ Hệ Thống Tra Cứu Văn Bản Pháp Luật | Phiên bản 2.0</p>
        <p>Dữ liệu từ: customs.gov.vn · thuvienphapluat.vn · vbpl.vn</p>
        <p>⚠️ Chỉ mang tính chất tham khảo. Vui lòng đối chiếu nguồn chính thức.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
