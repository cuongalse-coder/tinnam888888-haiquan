import streamlit as st
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import time
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# ==========================================
# PHẦN 1: CƠ SỞ DỮ LIỆU (DATABASE)
# ==========================================
# Đặt DB vào thư mục data của dự án
os.makedirs("data", exist_ok=True)
DB_PATH = 'data/documents.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS downloaded_documents (
            url TEXT PRIMARY KEY,
            title TEXT,
            source_website TEXT,
            download_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def is_downloaded(url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 1 FROM downloaded_documents WHERE url = ?', (url,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_as_downloaded(url, title, source_website):
    from datetime import datetime
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT OR IGNORE INTO downloaded_documents (url, title, source_website, download_date)
        VALUES (?, ?, ?, ?)
    ''', (url, title, source_website, now))
    conn.commit()
    conn.close()

# ==========================================
# PHẦN 2: SCRAPER (CÀO DỮ LIỆU)
# ==========================================
os.makedirs("data/raw_text", exist_ok=True)

class BaseScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def save_document(self, url, title, source_name, text_content):
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        if len(safe_title) > 100: safe_title = safe_title[:100]
        file_path = os.path.join("data/raw_text", f"[{source_name}] {safe_title}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Nguồn: {url}\n\n{text_content}")
        mark_as_downloaded(url, title, source_name)

class ThuvienphapluatScraper(BaseScraper):
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        
    def sync_new_documents(self, list_url, keywords=[], progress_callback=None):
        added_count = 0
        try:
            res = self.session.get(list_url)
            soup = BeautifulSoup(res.text, 'html.parser')
            doc_links = soup.select('a.doc-title') 
            for a_tag in doc_links:
                doc_url = a_tag.get('href')
                if not doc_url: continue
                if not doc_url.startswith('http'): doc_url = 'https://thuvienphapluat.vn' + doc_url
                title = a_tag.text.strip()
                
                # BỘ LỌC TỪ KHÓA
                if keywords:
                    if not any(k.strip().lower() in title.lower() for k in keywords):
                        continue
                        
                if progress_callback: progress_callback(f"[TVPL] Kiểm tra: {title}")
                if is_downloaded(doc_url): continue
                doc_res = self.session.get(doc_url)
                doc_soup = BeautifulSoup(doc_res.text, 'html.parser')
                content_div = doc_soup.select_one('.content1') or doc_soup.select_one('#doc-content')
                if content_div:
                    self.save_document(doc_url, title, "thuvienphapluat.vn", content_div.get_text(separator="\n", strip=True))
                    added_count += 1
                time.sleep(1)
            return True, f"Đã tải {added_count} bài mới từ ThuVienPhapLuat."
        except Exception as e:
            return False, f"Lỗi TVPL: {str(e)}"

class CustomsScraper(BaseScraper):
    def sync_new_documents(self, list_url, keywords=[], progress_callback=None):
        added_count = 0
        try:
            res = self.session.get(list_url, verify=False)
            soup = BeautifulSoup(res.text, 'html.parser')
            doc_links = soup.select('.item-list a, .news-title a') 
            for a_tag in doc_links:
                doc_url = a_tag.get('href')
                if not doc_url: continue
                if not doc_url.startswith('http'): doc_url = 'https://customs.gov.vn' + doc_url
                title = a_tag.text.strip()
                if not title or len(title) < 10: continue
                
                # BỘ LỌC TỪ KHÓA
                if keywords:
                    if not any(k.strip().lower() in title.lower() for k in keywords):
                        continue
                        
                if progress_callback: progress_callback(f"[Hải Quan] Kiểm tra: {title}")
                if is_downloaded(doc_url): continue
                doc_res = self.session.get(doc_url, verify=False)
                doc_soup = BeautifulSoup(doc_res.text, 'html.parser')
                content_div = doc_soup.select_one('.article-content') or doc_soup.select_one('.detail-content')
                if content_div:
                    self.save_document(doc_url, title, "customs.gov.vn", content_div.get_text(separator="\n", strip=True))
                    added_count += 1
                time.sleep(1)
            return True, f"Đã tải {added_count} bài mới từ Hải Quan."
        except Exception as e:
            return False, f"Lỗi Hải Quan: {str(e)}"

class ChinhphuScraper(BaseScraper):
    def sync_new_documents(self, list_url, keywords=[], progress_callback=None):
        added_count = 0
        try:
            res = self.session.get(list_url, verify=False)
            soup = BeautifulSoup(res.text, 'html.parser')
            doc_links = soup.select('.story__title a, .list-vb a')
            for a_tag in doc_links:
                doc_url = a_tag.get('href')
                if not doc_url: continue
                if not doc_url.startswith('http'): doc_url = 'https://xaydungchinhsach.chinhphu.vn' + doc_url
                title = a_tag.text.strip()
                if not title: continue
                
                # BỘ LỌC TỪ KHÓA
                if keywords:
                    if not any(k.strip().lower() in title.lower() for k in keywords):
                        continue
                        
                if progress_callback: progress_callback(f"[Chính Phủ] Kiểm tra: {title}")
                if is_downloaded(doc_url): continue
                doc_res = self.session.get(doc_url, verify=False)
                doc_soup = BeautifulSoup(doc_res.text, 'html.parser')
                content_div = doc_soup.select_one('.detail-content') or doc_soup.select_one('.article-body')
                if content_div:
                    self.save_document(doc_url, title, "chinhphu.vn", content_div.get_text(separator="\n", strip=True))
                    added_count += 1
                time.sleep(1)
            return True, f"Đã tải {added_count} bài mới từ Chính Phủ."
        except Exception as e:
            return False, f"Lỗi Chính Phủ: {str(e)}"


# ==========================================
# PHẦN 3: GIAO DIỆN STREAMLIT (UI)
# ==========================================
init_db()

st.set_page_config(page_title="Đồng bộ Dữ liệu Pháp Luật", page_icon="🔄", layout="wide")
st.title("🔄 Công Cụ Đồng Bộ Tài Liệu Tự Động")
st.markdown("Trang này giúp hệ thống tự động cào dữ liệu mới từ 3 nguồn: **ThuVienPhapLuat, Hải Quan, và Chính Phủ**.")

with st.sidebar:
    st.header("Cài đặt Nguồn cào (Scraper)")
    source_option = st.selectbox("Chọn nguồn muốn đồng bộ", [
        "Tất cả 3 nguồn", "ThuVienPhapLuat.vn", "Customs.gov.vn", "Chinhphu.vn"
    ])
    st.divider()
    tvpl_user = st.text_input("Tài khoản TVPL", value="cuong8791")
    tvpl_pass = st.text_input("Mật khẩu TVPL", type="password", value="02052016")
    url_tvpl = st.text_input("Link TVPL", value="https://thuvienphapluat.vn/page/van-ban-moi.aspx")
    url_customs = st.text_input("Link Hải Quan", value="https://www.customs.gov.vn/index.jsp?pageId=127")
    url_chinhphu = st.text_input("Link Chính Phủ", value="https://xaydungchinhsach.chinhphu.vn/toan-van.htm")
    
    st.divider()
    st.subheader("Bộ Lọc Từ Khóa")
    st.info("Hệ thống sẽ chỉ tải các văn bản có chứa ít nhất một trong các từ khóa này trong tiêu đề.")
    keyword_input = st.text_input("Từ khóa (cách nhau bằng dấu phẩy):", value="kế toán, hải quan, c/o, biểu thuế, xuất nhập khẩu")
    keyword_list = [k.strip() for k in keyword_input.split(",") if k.strip()]

if st.button("🔄 Bắt đầu Đồng bộ dữ liệu", type="primary"):
    status_text = st.empty()
    progress_bar = st.progress(0)
    def update_progress(msg): status_text.info(f"⏳ {msg}")
    results = []
    
    if source_option in ["Tất cả 3 nguồn", "ThuVienPhapLuat.vn"]:
        success, msg = ThuvienphapluatScraper(tvpl_user, tvpl_pass).sync_new_documents(url_tvpl, keyword_list, update_progress)
        results.append(msg)
    if source_option in ["Tất cả 3 nguồn", "Customs.gov.vn"]:
        success, msg = CustomsScraper().sync_new_documents(url_customs, keyword_list, update_progress)
        results.append(msg)
    if source_option in ["Tất cả 3 nguồn", "Chinhphu.vn"]:
        success, msg = ChinhphuScraper().sync_new_documents(url_chinhphu, keyword_list, update_progress)
        results.append(msg)

    progress_bar.progress(100)
    for r in results: st.success(r)

st.divider()
st.subheader("Lịch sử các văn bản đã tải")
try:
    conn = sqlite3.connect('data/documents.db')
    df = pd.read_sql_query("SELECT source_website, title, download_date, url FROM downloaded_documents ORDER BY download_date DESC", conn)
    conn.close()
    if not df.empty: st.dataframe(df, use_container_width=True)
    else: st.info("Chưa có văn bản nào trong cơ sở dữ liệu.")
except:
    st.error("Chưa thể tải dữ liệu lịch sử.")
