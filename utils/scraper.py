"""
Web Scraper Module - Thu thập văn bản pháp luật từ nhiều nguồn
Hỗ trợ: customs.gov.vn, thuvienphapluat.vn, vbpl.vn
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================
# CONSTANTS
# =============================================

CATEGORIES = [
    "Hải quan",
    "Kế toán - Kiểm toán",
    "Xuất nhập khẩu",
    "Thuế - Phí - Lệ phí",
    "Thương mại quốc tế",
    "Doanh nghiệp",
    "Lao động - Tiền lương",
    "Tài chính - Ngân hàng",
    "Đầu tư",
    "Ngoại hối",
    "Bảo hiểm",
    "Công nghệ thông tin",
    "An toàn thực phẩm",
    "Nông nghiệp",
    "Thương mại điện tử",
]

DOCUMENT_TYPES = [
    "Luật",
    "Nghị định",
    "Thông tư",
    "Quyết định",
    "Công văn",
    "Nghị quyết",
    "Pháp lệnh",
    "Chỉ thị",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
]


def _get_headers() -> dict:
    """Get randomized request headers to avoid blocking."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }


def _generate_id(so_hieu: str, tieu_de: str) -> str:
    """Generate a unique document ID based on document number and title."""
    raw = f"{so_hieu}_{tieu_de}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]


def _safe_request(url: str, timeout: int = 15, retries: int = 3) -> Optional[requests.Response]:
    """Make a safe HTTP request with retries and error handling."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=_get_headers(), timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request attempt {attempt + 1}/{retries} failed for {url}: {e}")
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 2 + random.uniform(0.5, 1.5)
                time.sleep(wait_time)
    logger.error(f"All {retries} attempts failed for {url}")
    return None


def _detect_category(title: str, summary: str = "") -> str:
    """Detect document category based on title and summary keywords."""
    text = (title + " " + summary).lower()

    category_keywords = {
        "Hải quan": ["hải quan", "customs", "thông quan", "xuất cảnh", "nhập cảnh", "cửa khẩu", "container", "soi chiếu"],
        "Kế toán - Kiểm toán": ["kế toán", "kiểm toán", "sổ sách", "báo cáo tài chính", "chuẩn mực kế toán", "hóa đơn", "chứng từ"],
        "Xuất nhập khẩu": ["xuất nhập khẩu", "xuất khẩu", "nhập khẩu", "xnk", "gia công", "tạm nhập", "tái xuất", "mã hs", "biểu thuế"],
        "Thuế - Phí - Lệ phí": ["thuế", "phí", "lệ phí", "tax", "vat", "gtgt", "tndn", "tncn", "thuế suất"],
        "Thương mại quốc tế": ["thương mại", "fta", "cptpp", "rcep", "evfta", "wto", "incoterm", "xuất xứ", "c/o"],
        "Doanh nghiệp": ["doanh nghiệp", "công ty", "giấy phép kinh doanh", "đăng ký doanh nghiệp"],
        "Lao động - Tiền lương": ["lao động", "tiền lương", "bảo hiểm xã hội", "bhxh", "lương tối thiểu", "hợp đồng lao động"],
        "Tài chính - Ngân hàng": ["ngân hàng", "tài chính", "tín dụng", "lãi suất", "ngoại hối", "thanh toán quốc tế"],
        "Đầu tư": ["đầu tư", "fdi", "khu công nghiệp", "khu chế xuất", "đặc khu kinh tế"],
        "Thương mại điện tử": ["thương mại điện tử", "tmđt", "sàn", "online", "ecommerce"],
    }

    for category, keywords in category_keywords.items():
        if any(kw in text for kw in keywords):
            return category

    return "Hải quan"


def _detect_doc_type(title: str) -> str:
    """Detect document type from title."""
    title_lower = title.lower()
    type_keywords = {
        "Luật": ["luật số", "luật sửa đổi"],
        "Nghị định": ["nghị định"],
        "Thông tư": ["thông tư"],
        "Quyết định": ["quyết định"],
        "Công văn": ["công văn", "v/v"],
        "Nghị quyết": ["nghị quyết"],
        "Pháp lệnh": ["pháp lệnh"],
        "Chỉ thị": ["chỉ thị"],
    }

    for doc_type, keywords in type_keywords.items():
        if any(kw in title_lower for kw in keywords):
            return doc_type

    # Try to detect from document number pattern
    so_hieu_patterns = {
        "Nghị định": r"\d+/\d{4}/NĐ-CP",
        "Thông tư": r"\d+/\d{4}/TT-",
        "Quyết định": r"\d+/QĐ-",
        "Công văn": r"\d+/[A-ZĐƯÀÁẢÃẠ]+-",
    }

    for doc_type, pattern in so_hieu_patterns.items():
        if re.search(pattern, title):
            return doc_type

    return "Công văn"


# =============================================
# SCRAPER: customs.gov.vn
# =============================================

def scrape_customs_gov(max_pages: int = 3) -> List[Dict]:
    """
    Crawl documents from customs.gov.vn.
    Note: This site has Cloudflare protection, so we use careful request handling.
    """
    documents = []
    base_url = "https://www.customs.gov.vn"

    target_urls = [
        f"{base_url}/index.jsp?pageId=3&cid=37",  # Văn bản QPPL
        f"{base_url}/index.jsp?pageId=3&cid=38",  # Tin tức
    ]

    for url in target_urls:
        for page in range(1, max_pages + 1):
            page_url = f"{url}&page={page}" if page > 1 else url
            logger.info(f"[customs.gov.vn] Fetching: {page_url}")

            response = _safe_request(page_url)
            if not response:
                continue

            try:
                soup = BeautifulSoup(response.content, "lxml")

                # Try multiple CSS selectors since CMS may change
                selectors = [
                    "div.list-item",
                    "div.news-item",
                    "li.item",
                    "div.row-item",
                    "tr.item-row",
                    "div.content-item",
                ]

                items = []
                for selector in selectors:
                    items = soup.select(selector)
                    if items:
                        break

                if not items:
                    # Fallback: look for links within content area
                    content_area = soup.select_one("div.content, div.main-content, div#content")
                    if content_area:
                        items = content_area.find_all("a", href=True)

                for item in items:
                    try:
                        # Extract title
                        title_el = item.select_one("a, h3, h4, .title")
                        if not title_el:
                            continue

                        title = title_el.get_text(strip=True)
                        if len(title) < 10:
                            continue

                        # Extract URL
                        link = title_el.get("href", "") if title_el.name == "a" else ""
                        if not link:
                            link_el = item.find("a", href=True)
                            link = link_el.get("href", "") if link_el else ""
                        if link and not link.startswith("http"):
                            link = base_url + link

                        # Extract date
                        date_el = item.select_one(".date, .time, span.ngay, .publish-date")
                        date_str = date_el.get_text(strip=True) if date_el else ""
                        ngay_ban_hanh = _parse_date(date_str)

                        # Extract summary
                        desc_el = item.select_one(".desc, .description, .summary, p")
                        tom_tat = desc_el.get_text(strip=True) if desc_el else ""

                        # Extract document number from title
                        so_hieu = _extract_so_hieu(title)

                        doc = {
                            "id": _generate_id(so_hieu, title),
                            "so_hieu": so_hieu,
                            "tieu_de": title,
                            "loai_van_ban": _detect_doc_type(title),
                            "co_quan_ban_hanh": "Tổng cục Hải quan",
                            "ngay_ban_hanh": ngay_ban_hanh,
                            "ngay_hieu_luc": ngay_ban_hanh,
                            "trang_thai": "Còn hiệu lực",
                            "linh_vuc": _detect_category(title, tom_tat),
                            "tom_tat": tom_tat[:500] if tom_tat else title,
                            "url": link,
                            "nguon": "customs.gov.vn",
                            "tags": _extract_tags(title, tom_tat),
                        }
                        documents.append(doc)
                    except Exception as e:
                        logger.warning(f"Error parsing item from customs.gov.vn: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error processing customs.gov.vn page: {e}")

            # Rate limiting
            time.sleep(random.uniform(2, 4))

    logger.info(f"[customs.gov.vn] Scraped {len(documents)} documents")
    return documents


# =============================================
# SCRAPER: thuvienphapluat.vn
# =============================================

def scrape_thuvienphapluat(max_pages: int = 3) -> List[Dict]:
    """
    Crawl documents from thuvienphapluat.vn.
    Targets customs, accounting, import-export, tax sections.
    """
    documents = []
    base_url = "https://thuvienphapluat.vn"

    # Multiple sections to crawl
    sections = [
        "/page/tim-van-ban.aspx?keyword=h%E1%BA%A3i+quan&area=0&type=0&status=0",
        "/page/tim-van-ban.aspx?keyword=k%E1%BA%BF+to%C3%A1n&area=0&type=0&status=0",
        "/page/tim-van-ban.aspx?keyword=xu%E1%BA%A5t+nh%E1%BA%ADp+kh%E1%BA%A9u&area=0&type=0&status=0",
        "/page/tim-van-ban.aspx?keyword=thu%E1%BA%BF&area=0&type=0&status=0",
        "/page/tim-van-ban.aspx?keyword=bi%E1%BB%83u+thu%E1%BA%BF&area=0&type=0&status=0",
    ]

    for section_url in sections:
        for page in range(1, max_pages + 1):
            full_url = f"{base_url}{section_url}&page={page}"
            logger.info(f"[thuvienphapluat.vn] Fetching: {full_url}")

            response = _safe_request(full_url)
            if not response:
                continue

            try:
                soup = BeautifulSoup(response.content, "lxml")

                # Search result items
                selectors = [
                    "div.search-result-item",
                    "div.nq-item",
                    "div.content-item",
                    "li.item",
                    "div.document-item",
                ]

                items = []
                for selector in selectors:
                    items = soup.select(selector)
                    if items:
                        break

                for item in items:
                    try:
                        title_el = item.select_one("a.title, h3 a, a.nq-name, .doc-title a")
                        if not title_el:
                            continue

                        title = title_el.get_text(strip=True)
                        if len(title) < 10:
                            continue

                        link = title_el.get("href", "")
                        if link and not link.startswith("http"):
                            link = base_url + link

                        # Extract metadata spans
                        meta_els = item.select("span.info, span.meta, div.nq-info span")
                        meta_text = " ".join(el.get_text(strip=True) for el in meta_els)

                        # Extract date
                        date_str = ""
                        date_el = item.select_one(".date, .ngay-ban-hanh, span.nq-date")
                        if date_el:
                            date_str = date_el.get_text(strip=True)

                        # Extract status
                        status_el = item.select_one(".status, .trang-thai, span.nq-status")
                        trang_thai = "Còn hiệu lực"
                        if status_el:
                            status_text = status_el.get_text(strip=True).lower()
                            if "hết" in status_text:
                                trang_thai = "Hết hiệu lực"
                            elif "sắp" in status_text:
                                trang_thai = "Sắp có hiệu lực"

                        so_hieu = _extract_so_hieu(title)
                        ngay_ban_hanh = _parse_date(date_str)

                        # Extract issuing authority
                        co_quan = _extract_co_quan(title, meta_text)

                        desc_el = item.select_one(".desc, .summary, .nq-desc, p.description")
                        tom_tat = desc_el.get_text(strip=True) if desc_el else title

                        doc = {
                            "id": _generate_id(so_hieu, title),
                            "so_hieu": so_hieu,
                            "tieu_de": title,
                            "loai_van_ban": _detect_doc_type(title),
                            "co_quan_ban_hanh": co_quan,
                            "ngay_ban_hanh": ngay_ban_hanh,
                            "ngay_hieu_luc": ngay_ban_hanh,
                            "trang_thai": trang_thai,
                            "linh_vuc": _detect_category(title, tom_tat),
                            "tom_tat": tom_tat[:500],
                            "url": link,
                            "nguon": "thuvienphapluat.vn",
                            "tags": _extract_tags(title, tom_tat),
                        }
                        documents.append(doc)
                    except Exception as e:
                        logger.warning(f"Error parsing item from thuvienphapluat.vn: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error processing thuvienphapluat.vn page: {e}")

            time.sleep(random.uniform(2, 4))

    logger.info(f"[thuvienphapluat.vn] Scraped {len(documents)} documents")
    return documents


# =============================================
# SCRAPER: vbpl.vn
# =============================================

def scrape_vbpl(max_pages: int = 3) -> List[Dict]:
    """
    Crawl documents from vbpl.vn (National Legal Document Database).
    """
    documents = []
    base_url = "https://vbpl.vn"

    # Target different categories
    category_params = [
        "ItemID=1",   # Hải quan related
        "ItemID=2",   # Thuế
        "ItemID=3",   # Thương mại
    ]

    for params in category_params:
        for page in range(1, max_pages + 1):
            url = f"{base_url}/TW/Pages/vbpq-thuoctinh.aspx?{params}&page={page}"
            logger.info(f"[vbpl.vn] Fetching: {url}")

            response = _safe_request(url)
            if not response:
                continue

            try:
                soup = BeautifulSoup(response.content, "lxml")

                # VBPL uses table-based layouts
                selectors = [
                    "table.listVB tr",
                    "div.content-item",
                    "li.item",
                    "div.result-item",
                ]

                items = []
                for selector in selectors:
                    items = soup.select(selector)
                    if items:
                        break

                for item in items:
                    try:
                        title_el = item.select_one("a, td.title a")
                        if not title_el:
                            continue

                        title = title_el.get_text(strip=True)
                        if len(title) < 10:
                            continue

                        link = title_el.get("href", "")
                        if link and not link.startswith("http"):
                            link = base_url + link

                        # Extract from table cells if present
                        cells = item.select("td")
                        so_hieu = ""
                        date_str = ""
                        co_quan = ""

                        if len(cells) >= 3:
                            so_hieu = cells[0].get_text(strip=True) if cells[0] else ""
                            date_str = cells[-1].get_text(strip=True) if cells[-1] else ""

                        if not so_hieu:
                            so_hieu = _extract_so_hieu(title)

                        ngay_ban_hanh = _parse_date(date_str)
                        co_quan = _extract_co_quan(title, "")

                        doc = {
                            "id": _generate_id(so_hieu, title),
                            "so_hieu": so_hieu,
                            "tieu_de": title,
                            "loai_van_ban": _detect_doc_type(title),
                            "co_quan_ban_hanh": co_quan,
                            "ngay_ban_hanh": ngay_ban_hanh,
                            "ngay_hieu_luc": ngay_ban_hanh,
                            "trang_thai": "Còn hiệu lực",
                            "linh_vuc": _detect_category(title),
                            "tom_tat": title,
                            "url": link,
                            "nguon": "vbpl.vn",
                            "tags": _extract_tags(title),
                        }
                        documents.append(doc)
                    except Exception as e:
                        logger.warning(f"Error parsing item from vbpl.vn: {e}")
                        continue

            except Exception as e:
                logger.error(f"Error processing vbpl.vn page: {e}")

            time.sleep(random.uniform(2, 4))

    logger.info(f"[vbpl.vn] Scraped {len(documents)} documents")
    return documents


# =============================================
# HELPER FUNCTIONS
# =============================================

def _extract_so_hieu(text: str) -> str:
    """Extract document number from text."""
    patterns = [
        r"(\d+/\d{4}/(?:NĐ|QĐ|TT|NQ|PL|CT)-[A-ZĐa-zđ]+)",
        r"(\d+/(?:NĐ|QĐ|TT|NQ|PL|CT)-[A-ZĐa-zđ]+)",
        r"(\d+/[A-ZĐƯÀÁẢÃẠ]+-[A-ZĐƯÀÁẢÃẠ]+)",
        r"(\d+/\d{4}/[A-ZĐ]+-[A-ZĐ]+(?:-[A-ZĐ]+)*)",
        r"(Luật\s+số\s+\d+/\d{4}/QH\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""


def _extract_co_quan(title: str, meta_text: str) -> str:
    """Extract issuing authority from title and metadata."""
    text = (title + " " + meta_text).lower()

    authorities = {
        "Quốc hội": ["quốc hội", "qh1"],
        "Chính phủ": ["chính phủ", "nđ-cp", "cp"],
        "Bộ Tài chính": ["bộ tài chính", "tt-btc", "btc"],
        "Bộ Công Thương": ["bộ công thương", "tt-bct", "bct"],
        "Bộ Y tế": ["bộ y tế", "tt-byt"],
        "Bộ Nông nghiệp và PTNT": ["bộ nông nghiệp", "bnnptnt"],
        "Bộ Lao động - TB&XH": ["bộ lao động", "blđtbxh"],
        "Tổng cục Hải quan": ["tổng cục hải quan", "tchq"],
        "Tổng cục Thuế": ["tổng cục thuế", "tct"],
        "Ngân hàng Nhà nước": ["ngân hàng nhà nước", "nhnn"],
    }

    for authority, keywords in authorities.items():
        if any(kw in text for kw in keywords):
            return authority

    return "Chính phủ"


def _parse_date(date_str: str) -> str:
    """Parse various date formats to YYYY-MM-DD."""
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")

    date_str = date_str.strip()

    # Common Vietnamese date formats
    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%d.%m.%Y",
        "Ngày %d/%m/%Y",
        "Ngày %d tháng %m năm %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Try regex extraction
    match = re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{2,4})", date_str)
    if match:
        day, month, year = match.groups()
        if len(year) == 2:
            year = "20" + year
        try:
            return datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
        except ValueError:
            pass

    return datetime.now().strftime("%Y-%m-%d")


def _extract_tags(title: str, summary: str = "") -> List[str]:
    """Extract relevant tags from title and summary."""
    text = (title + " " + summary).lower()
    all_tags = {
        "hải quan": "hải quan",
        "thuế": "thuế",
        "xuất khẩu": "xuất khẩu",
        "nhập khẩu": "nhập khẩu",
        "kế toán": "kế toán",
        "kiểm toán": "kiểm toán",
        "incoterm": "incoterms",
        "fta": "FTA",
        "cptpp": "CPTPP",
        "rcep": "RCEP",
        "evfta": "EVFTA",
        "biểu thuế": "biểu thuế",
        "mã hs": "mã HS",
        "vnaccs": "VNACCS",
        "thương mại điện tử": "TMĐT",
        "xuất xứ": "xuất xứ",
        "c/o": "C/O",
        "gia công": "gia công",
        "tạm nhập": "tạm nhập tái xuất",
        "chống bán phá giá": "chống bán phá giá",
        "phân luồng": "phân luồng",
        "thông quan": "thông quan",
        "doanh nghiệp": "doanh nghiệp",
        "lao động": "lao động",
        "bảo hiểm": "bảo hiểm",
        "ngân hàng": "ngân hàng",
        "hóa đơn": "hóa đơn",
        "chứng từ": "chứng từ",
        "báo cáo tài chính": "báo cáo tài chính",
        "gtgt": "thuế GTGT",
        "tndn": "thuế TNDN",
        "tncn": "thuế TNCN",
    }

    tags = []
    for keyword, tag in all_tags.items():
        if keyword in text and tag not in tags:
            tags.append(tag)

    return tags[:8]  # Limit to 8 tags


# =============================================
# MAIN SCRAPING ORCHESTRATOR
# =============================================

def scrape_all_sources(max_pages: int = 2) -> List[Dict]:
    """
    Scrape all sources and return combined, deduplicated results.
    """
    all_documents = []

    # Scrape each source
    scrapers = [
        ("customs.gov.vn", scrape_customs_gov),
        ("thuvienphapluat.vn", scrape_thuvienphapluat),
        ("vbpl.vn", scrape_vbpl),
    ]

    for source_name, scraper_fn in scrapers:
        try:
            logger.info(f"Starting scrape: {source_name}")
            docs = scraper_fn(max_pages=max_pages)
            all_documents.extend(docs)
            logger.info(f"Completed {source_name}: {len(docs)} documents")
        except Exception as e:
            logger.error(f"Failed to scrape {source_name}: {e}")
            continue

    # Deduplicate by document ID
    seen_ids = set()
    unique_docs = []
    for doc in all_documents:
        if doc["id"] not in seen_ids:
            seen_ids.add(doc["id"])
            unique_docs.append(doc)

    logger.info(f"Total unique documents: {len(unique_docs)}")
    return unique_docs


if __name__ == "__main__":
    # Test scraping
    docs = scrape_all_sources(max_pages=1)
    print(f"Scraped {len(docs)} documents")
    for doc in docs[:5]:
        print(f"  - [{doc['loai_van_ban']}] {doc['tieu_de'][:80]}...")
