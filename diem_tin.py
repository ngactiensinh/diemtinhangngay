import streamlit as st
import feedparser
import re
import time
from supabase import create_client, Client

st.set_page_config(page_title="Điểm tin Báo chí TGDV", page_icon="📰", layout="wide")
st.markdown("<div id='top-of-page'></div>", unsafe_allow_html=True)

# ---- GHI LƯỢT TRUY CẬP ----
if "da_ghi_truy_cap" not in st.session_state:
    try:
        _sb = create_client(
            "https://qqzsdxhqrdfvxnlurnyb.supabase.co",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxenNkeGhxcmRmdnhubHVybnliIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2MjY0NjAsImV4cCI6MjA5MTIwMjQ2MH0.H62F5zYEZ5l47fS4IdAE2JdRdI7inXQqWG0nvXhn2P8"
        )
        _sb.table("thong_ke_truy_cap").insert({"ten_app": "Điểm tin Báo chí"}).execute()
        st.session_state["da_ghi_truy_cap"] = True
    except Exception as e:
        pass
# ---- HẾT GHI LƯỢT TRUY CẬP ----

# ==========================================
# CSS TÙY CHỈNH GIAO DIỆN (CHUẨN TGDV)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #f4f6f9; }
    .main-header {color: #004B87; font-weight: 900; text-align: center; text-transform: uppercase; margin-bottom: 10px;}
    
    /* Giao diện thẻ tin tức (Card) */
    .news-card {
        border-left: 4px solid #004B87;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        height: 220px;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 15px rgba(0,75,135,0.15);
        border-left: 4px solid #C8102E;
    }
    .news-title {
        font-size: 16px;
        font-weight: bold;
        color: #004B87;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 3; /* Tối đa 3 dòng */
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .news-title:hover { color: #C8102E; }
    .news-date { font-size: 12px; color: #888; margin-bottom: 8px; font-style: italic; border-bottom: 1px dashed #eee; padding-bottom: 5px; }
    .news-summary { font-size: 13px; color: #444; line-height: 1.5; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;}
    
    /* Giao diện Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #e9ecef; border-radius: 5px 5px 0 0; padding: 10px 15px; font-weight: bold; color: #333;}
    .stTabs [aria-selected="true"] { background-color: #004B87; color: white !important; border-bottom: 2px solid #C8102E;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# CẤU HÌNH NGUỒN TIN
# ==========================================
RSS_FEEDS = {
    "🔥 TIÊU ĐIỂM TRONG NƯỚC (Tin nóng 24h)": "https://news.google.com/news/rss/headlines/section/topic/NATION?hl=vi&gl=VN&ceid=VN%3Avi",
    "🌍 QUỐC TẾ NỔI BẬT (TTXVN)": "https://www.vietnamplus.vn/rss/thegioi.rss",
    "📍 TIN TRONG TỈNH (Tuyên Quang 24h)": "https://news.google.com/rss/search?q=%22Tuy%C3%AAn+Quang%22+when:1d&hl=vi&gl=VN&ceid=VN:vi",
    "🗣️ DƯ LUẬN XÃ HỘI (Điểm nóng 7 ngày)": "https://news.google.com/rss/search?q=(%22d%C6%B0+lu%E1%BA%ADn%22+OR+%22b%E1%BB%A9c+x%C3%BAc%22+OR+%22ph%E1%BA%A3n+%C3%A1nh%22)+%22Tuy%C3%AAn+Quang%22+when:7d&hl=vi&gl=VN&ceid=VN:vi",
    "🤝 MÔ HÌNH DÂN VẬN KHÉO (Tháng qua)": "https://news.google.com/rss/search?q=%22d%C3%A2n+v%E1%BA%ADn+kh%C3%A9o%22+%22Tuy%C3%AAn+Quang%22+when:30d&hl=vi&gl=VN&ceid=VN:vi",
    "🏛️ TUYÊN GIÁO & DÂN VẬN TRUNG ƯƠNG": "https://news.google.com/rss/search?q=(site:dangcongsan.vn+OR+site:tuyengiaodanvan.vn+OR+site:nhandan.vn)+(%22Ban+Tuy%C3%AAn+gi%C3%A1o%22+OR+%22D%C3%A2n+v%E1%BA%ADn%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi",
    "🇻🇳 TTXVN (Thời sự - Chính trị)": "https://news.google.com/rss/search?q=site:baotintuc.vn+(%22th%E1%BB%9Di+s%E1%BB%B1%22+OR+%22ch%C3%ADnh+tr%E1%BB%8B%22+OR+%22l%C3%A3nh+%C4%91%E1%BA%A1o%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi"
}

# ==========================================
# BỘ LỌC KIỂM DUYỆT (BLACKLIST)
# ==========================================
BLACKLIST = ["bbc", "rfa", "voa", "rfi", "việt tân", "viet tan", "luatkhoa", "thoibao", "nguoi-viet"]

def is_safe(entry):
    content = (entry.get("title", "") + " " + entry.get("link", "") + " " + entry.get("summary", "")).lower()
    for bad_word in BLACKLIST:
        if bad_word in content:
            return False
    return True

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return " ".join(cleantext.split())

# Caching dữ liệu 15 phút + Lọc tin an toàn
@st.cache_data(ttl=900)
def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        safe_entries = [entry for entry in feed.entries if is_safe(entry)]
        return safe_entries[:50]
    except Exception as e:
        return []

# ==========================================
# THANH SIDEBAR TÙY CHỈNH
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#004B87;'>⚙️ TÙY CHỈNH HIỂN THỊ</h3>", unsafe_allow_html=True)
    so_luong_tin = st.slider("Số lượng tin bài mỗi mục:", min_value=3, max_value=30, value=12, step=3)
    st.markdown("---")
    st.markdown("💡 **Mẹo:**<br>Hệ thống tự động cập nhật tin mới mỗi 15 phút. Nhấn phím `C` trên bàn phím để làm mới ngay lập tức.", unsafe_allow_html=True)

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
c_logo1, c_logo2, c_logo3 = st.columns([1, 8, 1])
with c_logo2:
    st.markdown("<h1 class='main-header'>📰 HỆ THỐNG ĐIỂM TIN BÁO CHÍ TỰ ĐỘNG 24/7</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-top: -15px; margin-bottom: 30px;'>Tổng hợp tin tức thời sự, chính trị, dư luận xã hội phục vụ Ban Tuyên giáo và Dân vận</p>", unsafe_allow_html=True)

tabs = st.tabs(list(RSS_FEEDS.keys()))

for i, (tab_name, url) in enumerate(RSS_FEEDS.items()):
    with tabs[i]:
        with st.spinner("Đang tổng hợp tin tức..."):
            entries = fetch_rss(url)
            
        if not entries:
            st.info("📌 Hiện tại chưa có tin bài mới nào được cập nhật trong chuyên mục này.")
        else:
            entries_to_display = entries[:so_luong_tin]
            
            cols = st.columns(3)
            for idx, entry in enumerate(entries_to_display):
                with cols[idx % 3]:
                    title = entry.get("title", "Không có tiêu đề")
                    link = entry.get("link", "#")
                    pub_date = entry.get("published", "")
                    summary = clean_html(entry.get("summary", ""))
                    
                    # VIẾT SÁT LỀ ĐỂ TRÁNH LỖI HTML BỊ BIẾN THÀNH CODE BLOCK
                    html_card = f"""<div class="news-card">
<a class="news-title" href="{link}" target="_blank">{title}</a>
<div class="news-date">🕒 Xuất bản: {pub_date}</div>
<div class="news-summary">{summary}</div>
</div>"""
                    st.markdown(html_card, unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#888; font-size: 13px;'>Nguồn dữ liệu: Thông tấn xã Việt Nam, Báo điện tử Đảng Cộng sản, Báo Tuyên Quang và Google News.</p>", unsafe_allow_html=True)
# ==========================================
# NÚT CUỘN LÊN ĐẦU TRANG (SCROLL TO TOP)
# ==========================================
st.markdown("""
<style>
    .scroll-top {
        position: fixed;
        bottom: 80px; /* Đẩy lên cao để né logo Streamlit */
        right: 30px;
        background-color: #004B87;
        color: white !important;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        text-decoration: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 99999;
        transition: all 0.3s ease;
    }
    .scroll-top:hover {
        background-color: #C8102E;
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(200,16,46,0.4);
    }
    /* Chỉnh cho điện thoại */
    @media (max-width: 768px) {
        .scroll-top {
            width: 45px;
            height: 45px;
            font-size: 20px;
            bottom: 80px; /* Đẩy lên cao trên điện thoại */
            right: 20px;
        }
    }
</style>
<a href="#top-of-page" class="scroll-top" title="Lên đầu trang">⬆️</a>
""", unsafe_allow_html=True)
