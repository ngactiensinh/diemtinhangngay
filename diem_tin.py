import streamlit as st
import feedparser
from bs4 import BeautifulSoup
import urllib.request

st.set_page_config(page_title="Điểm Tin Báo Chí - TGDV", page_icon="📰", layout="wide")

# ==========================================
# GIAO DIỆN & CSS TÙY CHỈNH
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; }
    .header-box { background-color: #ffffff; border-top: 4px solid #C8102E; border-radius: 8px; padding: 15px 30px; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05); text-align: center;}
    .main-title { font-size: 24px; font-weight: 900; color: #C8102E; text-transform: uppercase; margin: 0;}
    
    .news-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
        gap: 20px; 
        margin-bottom: 30px;
    }
    
    .news-card { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
        border-left: 4px solid #004B87; 
        transition: transform 0.2s;
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    .news-card:hover { transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.1);}
    
    .news-title { font-size: 16px; font-weight: bold; margin-bottom: 8px; line-height: 1.4;}
    .news-title a { color: #004B87; text-decoration: none; }
    .news-title a:hover { color: #C8102E; text-decoration: underline; }
    
    .news-date { font-size: 12px; color: #888; margin-bottom: 10px; font-style: italic;}
    
    .news-summary { 
        font-size: 14px; 
        color: #444; 
        line-height: 1.5;
        flex-grow: 1;
        display: -webkit-box;
        -webkit-line-clamp: 4;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-box">
    <div class="main-title">HỆ THỐNG ĐIỂM TIN BÁO CHÍ TỰ ĐỘNG</div>
    <div style="font-size: 13px; font-weight: bold; color: #6c757d; margin-top:3px;">BAN TUYÊN GIÁO VÀ DÂN VẬN TỈNH ỦY TUYÊN QUANG</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# CẤU HÌNH NGUỒN TIN (BẢN VIP: THÊM DƯ LUẬN & DÂN VẬN KHÉO)
# ==========================================
RSS_FEEDS = {
    "🔥 TIÊU ĐIỂM QUỐC GIA (Tin nóng 24h)": "https://news.google.com/news/rss/headlines/section/topic/NATION?hl=vi&gl=VN&ceid=VN%3Avi",
    "🌍 QUỐC TẾ NỔI BẬT (Báo Đảng & TTXVN)": "https://news.google.com/rss/search?q=(site:baotintuc.vn+OR+site:nhandan.vn+OR+site:dangcongsan.vn)+(%22Th%E1%BA%BF+gi%E1%BB%9Bi%22+OR+%22Qu%E1%BB%91c+t%E1%BA%BF%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi",
    "📍 TUYÊN GIÁO & DÂN VẬN TUYÊN QUANG": "https://news.google.com/rss/search?q=(site:baotuyenquang.com.vn+OR+%22Tuy%C3%AAn+Quang%22)+(%22Ban+Tuy%C3%AAn+gi%C3%A1o%22+OR+%22D%C3%A2n+v%E1%BA%ADn%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi",
    "🗣️ DƯ LUẬN XÃ HỘI (Điểm nóng 7 ngày)": "https://news.google.com/rss/search?q=(%22d%C6%B0+lu%E1%BA%ADn%22+OR+%22b%E1%BB%A9c+x%C3%BAc%22+OR+%22ph%E1%BA%A3n+%C3%A1nh%22)+%22Tuy%C3%AAn+Quang%22+when:7d&hl=vi&gl=VN&ceid=VN:vi",
    "🤝 MÔ HÌNH DÂN VẬN KHÉO (Tháng qua)": "https://news.google.com/rss/search?q=%22d%C3%A2n+v%E1%BA%ADn+kh%C3%A9o%22+%22Tuy%C3%AAn+Quang%22+when:30d&hl=vi&gl=VN&ceid=VN:vi",
    "🏛️ TUYÊN GIÁO & DÂN VẬN TRUNG ƯƠNG": "https://news.google.com/rss/search?q=(site:dangcongsan.vn+OR+site:tuyengiaodanvan.vn+OR+site:nhandan.vn)+(%22Ban+Tuy%C3%AAn+gi%C3%A1o%22+OR+%22D%C3%A2n+v%E1%BA%ADn%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi",
    "🇻🇳 TTXVN (Thời sự - Chính trị nổi bật)": "https://news.google.com/rss/search?q=site:baotintuc.vn+(%22th%E1%BB%9Di+s%E1%BB%B1%22+OR+%22ch%C3%ADnh+tr%E1%BB%8B%22+OR+%22l%C3%A3nh+%C4%91%E1%BA%A1o%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi"
}

def clean_html(raw_html):
    if not raw_html: return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

# ==========================================
# CỘT SIDEBAR - ĐIỀU KHIỂN
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ BỘ LỌC TIN TỨC")
    nguon_tin = st.selectbox("📌 Chọn nguồn tin:", ["Tất cả"] + list(RSS_FEEDS.keys()))
    tu_khoa = st.text_input("🔍 Tìm từ khóa (VD: đại hội, chỉ đạo...):", "")
    so_luong = st.slider("📑 Số lượng tin mỗi khối:", 4, 30, 8)
    
    st.markdown("---")
    st.info("💡 **Gợi ý:** Hệ thống tự động phân loại Tin Tuyên giáo, Dư luận xã hội và Mô hình Dân vận khéo để phục vụ công tác tham mưu.")

# ==========================================
# XỬ LÝ VÀ HIỂN THỊ TIN TỨC
# ==========================================
danh_sach_quet = RSS_FEEDS if nguon_tin == "Tất cả" else {nguon_tin: RSS_FEEDS[nguon_tin]}
tong_so_tin = 0

with st.spinner("Đang kết nối và tổng hợp dữ liệu báo chí..."):
    for ten_nguon, url_rss in danh_sach_quet.items():
        try:
            req = urllib.request.Request(url_rss, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                feed = feedparser.parse(response.read())
                
            tin_da_loc = []
            
            # --- MÀNG LỌC RÁC NÂNG CẤP BỌC THÉP ---
            # Thêm "tư liệu văn kiện" vào danh sách đen
            tu_khoa_rac = ["untitled", "vnaid", "lịch tạm ngừng", "cắt điện", "xổ số", "giá vàng", "thời tiết", "tỷ giá", "tư liệu văn kiện", "tulieuvankien"]
            
            for entry in feed.entries:
                tieu_de = entry.title.strip()
                tieu_de_lower = tieu_de.lower()
                ngay_dang_goc = entry.get('published', '')
                
                # 🛡️ CHỐT CHẶN 1: Từ khóa rác và tiêu đề bất thường
                if len(tieu_de) < 10 or any(rac in tieu_de_lower for rac in tu_khoa_rac):
                    continue 
                
                # 🛡️ CHỐT CHẶN 2: Lọc thời gian cứng (Chặn tuyệt đối tin trước 2026)
                # Kẻ nào có năm cũ trong ngày xuất bản -> Trảm ngay lập tức
                cac_nam_cu = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
                if any(nam in ngay_dang_goc for nam in cac_nam_cu):
                    continue
                
                tom_tat = clean_html(entry.get('summary', '')).strip()
                
                # 🛡️ CHỐT CHẶN 3: Lọc theo từ khóa sếp gõ (nếu có)
                if tu_khoa and tu_khoa.lower() not in tieu_de_lower and tu_khoa.lower() not in tom_tat.lower():
                    continue 
                
                tin_da_loc.append(entry)
                if len(tin_da_loc) >= so_luong: break
                    
            # --- HIỂN THỊ DẠNG LƯỚI ---
            if tin_da_loc:
                st.markdown(f"<h3 style='color:#004B87; margin-top: 20px; margin-bottom: 10px; border-bottom: 2px solid #e0e6ed; padding-bottom: 5px;'>📰 {ten_nguon}</h3>", unsafe_allow_html=True)
                
                html_grid = '<div class="news-grid">'
                
                for bai_viet in tin_da_loc:
                    tong_so_tin += 1
                    ngay_dang = bai_viet.get('published', 'Không rõ thời gian').replace("GMT", "").strip() 
                    link = bai_viet.link
                    tieu_de = bai_viet.title.replace('"', '&quot;')
                    tom_tat = clean_html(bai_viet.get('summary', '')).replace('"', '&quot;')
                    
                    html_grid += f"<div class='news-card'><div class='news-title'><a href='{link}' target='_blank'>{tieu_de}</a></div><div class='news-date'>🕒 Xuất bản: {ngay_dang}</div><div class='news-summary'>{tom_tat}</div></div>"
                    
                html_grid += '</div>'
                st.markdown(html_grid, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"⚠️ Không thể tải dữ liệu từ {ten_nguon}. Vui lòng thử lại sau.")

if tong_so_tin == 0:
    st.warning("Không tìm thấy tin tức nào phù hợp với bộ lọc hiện tại.")
else:
    st.success(f"✅ Đã tổng hợp thành công {tong_so_tin} tin bài nổi bật!")
