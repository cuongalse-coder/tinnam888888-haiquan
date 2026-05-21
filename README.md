# Cổng Pháp Luật Hải Quan Việt Nam ⚖️

Hệ thống tra cứu văn bản pháp luật về Hải quan & Xuất nhập khẩu.

**URL:** [tinnam888888_haiquan.streamlit.app](https://tinnam888888_haiquan.streamlit.app)

## 🚀 Tính năng chính

- 🔍 **Tìm kiếm thông minh** - Gõ câu hỏi tự nhiên, VD: "tạm nhập tái xuất có bị nộp thuế không"
- 🔴 **Bôi đỏ** phần text khớp với từ khóa tìm kiếm
- 📋 **Trả lời câu hỏi** - Tự động liệt kê Điều, Luật, Thông tư liên quan
- 📂 **37+ văn bản pháp luật** - Luật, Nghị định, Thông tư, Công văn, Quyết định
- 💾 **Tải xuống** văn bản dưới dạng file .txt
- 📱 **Responsive** - Hoạt động tốt trên mọi thiết bị (WiFi & 4G)

## 📂 Cấu trúc Folders lưu file

| Folder | Loại văn bản |
|--------|-------------|
| A | Thông tư |
| B | Nghị định |
| C | Nghị quyết |
| D | Luật |
| E | Công văn & Quyết định |

## 🛠️ Cài đặt & Chạy

### Chạy local:
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Deploy lên Streamlit Cloud:
1. Push code lên GitHub repository
2. Vào [share.streamlit.io](https://share.streamlit.io)
3. Kết nối GitHub repo
4. Đặt tên app: `tinnam888888_haiquan`
5. Main file: `app.py`
6. Click Deploy!

## 📝 Hướng dẫn Deploy chi tiết

### Bước 1: Tạo GitHub Repository
1. Vào [github.com](https://github.com) → đăng nhập/đăng ký
2. Click **"New repository"**
3. Đặt tên: `customs-law-portal`
4. Chọn **Public**
5. Click **Create repository**

### Bước 2: Upload code
Upload các file sau lên GitHub:
- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `data/legal-documents.json`

### Bước 3: Deploy trên Streamlit Cloud
1. Vào [share.streamlit.io](https://share.streamlit.io)
2. Đăng nhập bằng GitHub
3. Click **"New app"**
4. Chọn repository vừa tạo
5. Branch: `main`
6. Main file path: `app.py`
7. App URL: `tinnam888888_haiquan`
8. Click **"Deploy!"**

Sau 2-3 phút, app sẽ live tại: **tinnam888888_haiquan.streamlit.app** 🎉
