# 🏛️ Hệ Thống Tra Cứu Văn Bản Pháp Luật

> **Hải Quan · Kế Toán · Xuất Nhập Khẩu · Thuế · Incoterms**

Ứng dụng Streamlit chuyên nghiệp để tra cứu văn bản pháp luật Việt Nam, tự động cập nhật từ các nguồn chính thức.

## ✨ Tính năng

- 🔍 **Tra cứu thông minh** - Full-text search + fuzzy matching (RapidFuzz)
- 📊 **Thống kê trực quan** - Plotly charts phân tích đa chiều
- 🌍 **Incoterms 2020** - Đầy đủ 11 điều kiện thương mại quốc tế
- 💰 **Biểu thuế XNK** - FTA, TTĐB, GTGT, thuế suất ưu đãi
- 📋 **Mã HS** - Cấu trúc 97 chương biểu thuế Việt Nam
- 📥 **Export** - Xuất CSV/JSON
- 🔄 **Auto-update** - GitHub Actions cập nhật mỗi 6 giờ

## 📚 Phạm vi bao phủ

| Lĩnh vực | Nội dung |
|-----------|----------|
| 🛃 Hải quan | Thủ tục, giám sát, thông quan, AEO |
| 📊 Kế toán | VAS, IFRS, hóa đơn, BCTC, kiểm toán |
| 🚢 XNK | Thủ tục XNK, logistics, C/O, HS |
| 💰 Thuế | GTGT, TNDN, TNCN, XNK, TTĐB |
| 🌍 TMQT | FTA (CPTPP, RCEP, EVFTA), Incoterms |
| 🏢 Doanh nghiệp | Đăng ký, giấy phép, đầu tư |
| 👷 Lao động | Lương, BHXH, lao động nước ngoài |

## 🚀 Cài đặt & Chạy

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/haiquan-app.git
cd haiquan-app

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy app
streamlit run app.py
```

## 🔄 Tự động cập nhật

Dữ liệu được cập nhật tự động qua GitHub Actions:
- **Tần suất:** Mỗi 6 giờ (0h, 6h, 12h, 18h UTC)
- **Nguồn:** customs.gov.vn, thuvienphapluat.vn, vbpl.vn
- **Cơ chế:** Scrape → Merge → Deduplicate → Git Push → Auto-deploy

## 📁 Cấu trúc dự án

```
haiquan-app/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Dependencies
├── .streamlit/config.toml    # Theme configuration
├── assets/style.css          # Custom CSS
├── utils/
│   ├── scraper.py            # Web scraping engine
│   ├── data_manager.py       # Data management + Incoterms
│   └── search_engine.py      # Full-text search + fuzzy
├── scripts/fetch_data.py     # Auto-update script
├── data/documents.json       # Document database
└── .github/workflows/        # GitHub Actions
```

## 🛠️ Tech Stack

- **Frontend:** Streamlit + Custom CSS (Glassmorphism)
- **Charts:** Plotly
- **Search:** RapidFuzz (fuzzy matching)
- **Scraping:** BeautifulSoup + lxml
- **CI/CD:** GitHub Actions
- **Hosting:** Streamlit Cloud

## ⚠️ Disclaimer

Hệ thống này chỉ mang tính chất **tham khảo**. Vui lòng đối chiếu với nguồn chính thức:
- [customs.gov.vn](https://customs.gov.vn) - Tổng cục Hải quan
- [vbpl.vn](https://vbpl.vn) - CSDL VBPL quốc gia
- [thuvienphapluat.vn](https://thuvienphapluat.vn) - Thư viện Pháp luật

## 📄 License

MIT License
