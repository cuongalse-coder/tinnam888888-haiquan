import os
import json
import logging
from duckduckgo_search import DDGS

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.prompts import ChatPromptTemplate
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False

logger = logging.getLogger(__name__)

def perform_ai_search(query: str, api_key: str) -> list:
    """
    Tìm kiếm văn bản mới nhất trên Internet và trích xuất dưới dạng JSON để giao diện cũ hiển thị.
    """
    if not HAS_LANGCHAIN:
        raise ImportError("Chưa cài đặt đủ thư viện langchain. Vui lòng kiểm tra requirements.txt")
        
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        try:
            import streamlit as st
            if "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except Exception:
            pass
            
    if not api_key:
        raise ValueError("Chưa cấu hình API Key cho Google Gemini.")

    # 1. Tìm kiếm Internet thực tế bằng DuckDuckGo
    search_context = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query + " thông tư nghị định mới nhất thuvienphapluat vbpl", max_results=5))
            if results:
                search_context = "\n".join([f"Tiêu đề: {r['title']}\nNội dung: {r['body']}\nLink: {r['href']}" for r in results])
            else:
                search_context = "Không tìm thấy kết quả phù hợp trên Internet."
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm DuckDuckGo: {e}")
        search_context = "Lỗi kết nối khi tìm kiếm trên Internet."

    # 2. Sử dụng LLM để đọc, lọc thông tin và xuất ra JSON đúng format cũ
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", # Dùng bản Pro để trích xuất chuẩn và đọc hiểu nội dung pháp luật tốt nhất
        google_api_key=api_key,
        temperature=0.1
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Bạn là trợ lý AI siêu việt chuyên về pháp luật Việt Nam. 
Nhiệm vụ của bạn là đọc các kết quả tìm kiếm từ Internet, tìm câu trả lời chính xác nhất và các văn bản pháp luật (thông tư, nghị định, luật...) mới nhất liên quan đến câu hỏi của người dùng.
Sau đó, hãy trích xuất thông tin chi tiết của văn bản đó và trả về DUY NHẤT một mảng JSON hợp lệ. Không kèm theo bất kỳ lời giải thích nào ngoài mảng JSON.

Định dạng JSON yêu cầu:
[
  {{
    "so_hieu": "Số hiệu văn bản (ví dụ: 15/2022/NĐ-CP). Nếu không có ghi là 'Không rõ'",
    "tieu_de": "Tiêu đề đầy đủ của văn bản",
    "loai_van_ban": "Loại (Nghị định, Thông tư, Quyết định, Luật, Công văn...)",
    "co_quan_ban_hanh": "Cơ quan ban hành (Chính phủ, Bộ Tài chính, Tổng cục Hải quan...)",
    "ngay_ban_hanh": "YYYY-MM-DD (nếu không rõ, để 'N/A')",
    "trang_thai": "Còn hiệu lực / Sắp có hiệu lực / Hết hiệu lực",
    "linh_vuc": "Hải quan / Thuế - Phí - Lệ phí / Xuất nhập khẩu / Kế toán - Kiểm toán / Thương mại quốc tế / Doanh nghiệp / Khác",
    "tom_tat": "Đây là phần cực kỳ quan trọng. Bạn phải ghi TÓM TẮT CHI TIẾT nội dung nghị định/thông tư, đồng thời trả lời trực tiếp và rõ ràng câu hỏi của người dùng dựa trên thông tin thực tế vừa tìm được.",
    "url": "Link nguồn gốc văn bản (từ kết quả tìm kiếm)"
  }}
]
"""),
        ("human", "Câu hỏi của người dùng: {query}\n\nKết quả tìm kiếm Internet hiện tại:\n{search_context}\n\nHãy trả về JSON mảng các văn bản liên quan.")
    ])

    try:
        chain = prompt | llm
        response = chain.invoke({"query": query, "search_context": search_context})
        
        # Parse JSON
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        docs = json.loads(content.strip())
        
        # Đảm bảo có ít nhất 1 kết quả nếu AI ko bắt được JSON
        if not docs and search_context:
            return [{
                "so_hieu": "AI-Tìm-Kiếm",
                "tieu_de": "Kết quả tổng hợp từ AI dựa trên câu hỏi",
                "loai_van_ban": "Tổng hợp",
                "co_quan_ban_hanh": "Trợ lý AI",
                "ngay_ban_hanh": "N/A",
                "trang_thai": "Tham khảo",
                "linh_vuc": "Tổng hợp",
                "tom_tat": "Tôi đã tìm kiếm trên Internet nhưng không thể trích xuất chính xác cấu trúc văn bản. Dưới đây là các thông tin tôi tìm được:\n" + search_context[:500],
                "url": ""
            }]
            
        return docs
        
    except Exception as e:
        logger.error(f"Lỗi khi parse AI JSON: {e}")
        return [{
            "so_hieu": "Lỗi",
            "tieu_de": "Đã xảy ra lỗi trong quá trình phân tích dữ liệu AI",
            "loai_van_ban": "Lỗi hệ thống",
            "co_quan_ban_hanh": "Hệ thống",
            "ngay_ban_hanh": "N/A",
            "trang_thai": "Lỗi",
            "linh_vuc": "Khác",
            "tom_tat": f"Chi tiết lỗi: {str(e)}\n\nKết quả tìm kiếm thô:\n{search_context}",
            "url": ""
        }]
