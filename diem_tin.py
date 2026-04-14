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
    .news-card { background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 4px solid #004B87; transition: transform 0.2s;}
    .news-card:hover { transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.1);}
    .news-title { font-size: 18px; font-weight: bold; margin-bottom: 5px;}
    .news-title a { color: #004B87; text-decoration: none; }
    .news-title a:hover { color: #C8102E; text-decoration: underline; }
    .news-date { font-size: 12px; color: #888; margin-bottom: 10px; font-style: italic;}
    .news-summary { font-size: 14px; color: #444; line-height: 1.5;}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-box">
    <div class="main-title">HỆ THỐNG ĐIỂM TIN BÁO CHÍ TỰ ĐỘNG</div>
    <div style="font-size: 13px; font-weight: bold; color: #6c757d; margin-top:3px;">BAN TUYÊN GIÁO VÀ DÂN VẬN TỈNH ỦY TUYÊN QUANG</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# CẤU HÌNH NGUỒN TIN (RSS FEEDS) - BẢN TRỌNG TÂM 24H
# ==========================================
RSS_FEEDS = {
    "🔥 TIÊU ĐIỂM QUỐC GIA (Nóng nhất trong ngày)": "https://news.google.com/news/rss/headlines/section/topic/NATION?hl=vi&gl=VN&ceid=VN%3Avi",
    "🌟 TIN NỔI BẬT (Báo Nhân Dân)": "https://nhandan.vn/rss/tin-noi-bat.rss",
    "📍 ĐIỂM NÓNG TUYÊN QUANG (Trong 24h qua)": "https://news.google.com/rss/search?q=%22Tuy%C3%AAn+Quang%22+when:1d&hl=vi&gl=VN&ceid=VN:vi",
    "📢 TUYÊN GIÁO & DÂN VẬN (Trong 24h qua)": "https://news.google.com/rss/search?q=(%22Ban+Tuy%C3%AAn+gi%C3%A1o%22+OR+%22D%C3%A2n+v%E1%BA%ADn%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi",
    "🇻🇳 TIN CHÍNH TỪ TTXVN & BÁO ĐẢNG (Trong 24h qua)": "https://news.google.com/rss/search?q=(site:dangcongsan.vn+OR+site:vnanet.vn+OR+site:baotintuc.vn)+when:1d&hl=vi&gl=VN&ceid=VN:vi"
}

# Hàm làm sạch mã HTML trong nội dung tóm tắt
def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

# ==========================================
# CỘT SIDEBAR - ĐIỀU KHIỂN & LỌC TỪ KHÓA
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ BỘ LỌC TIN TỨC")
    nguon_tin = st.selectbox("📌 Chọn nguồn tin:", ["Tất cả"] + list(RSS_FEEDS.keys()))
    tu_khoa = st.text_input("🔍 Tìm từ khóa (VD: chuyển đổi số, đại hội...):", "")
    so_luong = st.slider("📑 Số lượng tin hiển thị mỗi nguồn:", 5, 30, 10)
    
    st.markdown("---")
    st.info("💡 **Gợi ý:** Hệ thống tự động cập nhật tin bài mới nhất từ các đầu báo chính thống. Nhấp vào tiêu đề để đọc chi tiết trên trang gốc.")

# ==========================================
# XỬ LÝ VÀ HIỂN THỊ TIN TỨC
# ==========================================
# Xác định danh sách link RSS cần quét
danh_sach_quet = {}
if nguon_tin == "Tất cả":
    danh_sach_quet = RSS_FEEDS
else:
    danh_sach_quet[nguon_tin] = RSS_FEEDS[nguon_tin]

tong_so_tin = 0

with st.spinner("Đang kết nối và tổng hợp dữ liệu báo chí..."):
    for ten_nguon, url_rss in danh_sach_quet.items():
        try:
            # Gửi yêu cầu lấy feed với header tùy chỉnh để tránh bị chặn
            req = urllib.request.Request(url_rss, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                feed_data = response.read()
                feed = feedparser.parse(feed_data)
                
            tin_da_loc = []
            
            # Quét từng bài viết trong feed
            for entry in feed.entries:
                tieu_de = entry.title
                tom_tat = clean_html(entry.get('summary', ''))
                
                # Lọc theo từ khóa nếu có
                if tu_khoa:
                    if tu_khoa.lower() not in tieu_de.lower() and tu_khoa.lower() not in tom_tat.lower():
                        continue # Bỏ qua nếu không chứa từ khóa
                
                tin_da_loc.append(entry)
                if len(tin_da_loc) >= so_luong:
                    break
                    
            if tin_da_loc:
                st.markdown(f"### 📰 {ten_nguon}")
                for bai_viet in tin_da_loc:
                    tong_so_tin += 1
                    ngay_dang = bai_viet.get('published', 'Không rõ thời gian')
                    link = bai_viet.link
                    tieu_de = bai_viet.title
                    tom_tat = clean_html(bai_viet.get('summary', 'Không có tóm tắt.'))
                    
                    # Vẽ thẻ tin tức (Card)
                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-title"><a href="{link}" target="_blank">{tieu_de}</a></div>
                        <div class="news-date">🕒 Xuất bản: {ngay_dang}</div>
                        <div class="news-summary">{tom_tat}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"⚠️ Không thể tải dữ liệu từ {ten_nguon}. Vui lòng thử lại sau.")

if tong_so_tin == 0:
    st.warning("Không tìm thấy tin tức nào phù hợp với bộ lọc hiện tại.")
else:
    st.success(f"✅ Đã tổng hợp thành công {tong_so_tin} tin bài mới nhất!")
