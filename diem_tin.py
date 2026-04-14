import streamlit as st
import feedparser
from bs4 import BeautifulSoup
import urllib.request

st.set_page_config(page_title="Điểm Tin Báo Chí - TGDV", page_icon="📰", layout="wide")

# ==========================================
# GIAO DIỆN & CSS TÙY CHỈNH (NÂNG CẤP DẠNG LƯỚI)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; }
    .header-box { background-color: #ffffff; border-top: 4px solid #C8102E; border-radius: 8px; padding: 15px 30px; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(0,0,0,0.05); text-align: center;}
    .main-title { font-size: 24px; font-weight: 900; color: #C8102E; text-transform: uppercase; margin: 0;}
    
    /* GIAO DIỆN LƯỚI (GRID) HIỆN ĐẠI */
    .news-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); /* Tự động chia cột, mỗi cột tối thiểu 400px */
        gap: 20px; 
        margin-bottom: 30px;
    }
    
    /* ĐỊNH DẠNG THẺ TIN TỨC */
    .news-card { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 8px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
        border-left: 4px solid #004B87; 
        transition: transform 0.2s;
        display: flex;
        flex-direction: column;
        height: 100%; /* Ép các thẻ cao bằng nhau */
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
        /* Giới hạn tóm tắt hiển thị tối đa 4 dòng cho đều nhau */
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
# CẤU HÌNH NGUỒN TIN (ĐÃ TỐI ƯU HÓA)
# ==========================================
RSS_FEEDS = {
    "🔥 TIÊU ĐIỂM QUỐC GIA (Tin nóng 24h)": "https://news.google.com/news/rss/headlines/section/topic/NATION?hl=vi&gl=VN&ceid=VN%3Avi",
    "🌍 QUỐC TẾ NỔI BẬT (Báo Đảng & TTXVN)": "https://news.google.com/rss/search?q=(site:baotintuc.vn+OR+site:nhandan.vn+OR+site:dangcongsan.vn)+(%22Th%E1%BA%BF+gi%E1%BB%9Bi%22+OR+%22Qu%E1%BB%91c+t%E1%BA%BF%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi",
    "📍 TUYÊN GIÁO & DÂN VẬN TUYÊN QUANG": "https://news.google.com/rss/search?q=(site:baotuyenquang.com.vn+OR+%22Tuy%C3%AAn+Quang%22)+(%22Ban+Tuy%C3%AAn+gi%C3%A1o%22+OR+%22D%C3%A2n+v%E1%BA%ADn%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi",
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
    so_luong = st.slider("📑 Số lượng tin mỗi khối:", 4, 20, 8)
    
    st.markdown("---")
    st.info("💡 **Gợi ý:** Hệ thống hiển thị dạng lưới (Grid) trực quan. Các tin rác, tiện ích dân sinh đã được loại bỏ tự động.")

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
            
            # --- MÀNG LỌC RÁC NÂNG CẤP ---
            tu_khoa_rac = ["untitled", "vnaid", "lịch tạm ngừng", "cắt điện", "xổ số", "giá vàng", "thời tiết", "tỷ giá"]
            
            for entry in feed.entries:
                tieu_de = entry.title
                tieu_de_lower = tieu_de.lower()
                
                # Loại bài có tiêu đề quá ngắn hoặc chứa từ khóa đen
                if len(tieu_de) < 10 or any(rac in tieu_de_lower for rac in tu_khoa_rac):
                    continue 
                
                tom_tat = clean_html(entry.get('summary', ''))
                
                if tu_khoa and tu_khoa.lower() not in tieu_de_lower and tu_khoa.lower() not in tom_tat.lower():
                    continue 
                
                tin_da_loc.append(entry)
                if len(tin_da_loc) >= so_luong: break
                    
            # --- HIỂN THỊ DẠNG LƯỚI (GRID) ---
                    # ÉP SÁT LỀ TRÁI ĐỂ KHÔNG BỊ LỖI HIỂN THỊ RAW HTML
                    html_grid += f"""<div class="news-card">
<div class="news-title"><a href="{bai_viet.link}" target="_blank">{bai_viet.title}</a></div>
<div class="news-date">🕒 Xuất bản: {ngay_dang}</div>
<div class="news-summary">{clean_html(bai_viet.get('summary', ''))}</div>
</div>"""
                    
                # Đóng thẻ div container
                html_grid += '</div>'
                
                # Đẩy toàn bộ khối lưới này ra màn hình
                st.markdown(html_grid, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"⚠️ Không thể tải dữ liệu từ {ten_nguon}. Vui lòng thử lại sau.")

if tong_so_tin == 0:
    st.warning("Không tìm thấy tin tức nào phù hợp với bộ lọc hiện tại.")
else:
    st.success(f"✅ Đã tổng hợp thành công {tong_so_tin} tin bài mới nhất!")
