"""
HỆ THỐNG ĐIỂM TIN BÁO CHÍ - PHIÊN BẢN GỌN GÀNG, SẮC NÉT
Đã vá: Thu gọn Banner, font chữ đậm dễ đọc, đưa thanh trượt chọn số lượng tin ra ngoài
"""

import streamlit as st
import feedparser
import re
import time
from supabase import create_client, Client
import datetime

st.set_page_config(
    page_title="Điểm Tin Báo Chí · TGDV",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)
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
# CSS GIAO DIỆN TIN TỨC CHUẨN (Đậm, dễ đọc)
# ==========================================
st.markdown("""
<style>
    /* Dùng font cơ bản, dễ đọc, nét đậm để không hoa mắt */
    html, body, [class*="css"] { 
        font-family: 'Helvetica Neue', Arial, sans-serif !important; 
    }
    
    .stApp {
        background-color: #F8F9FA;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1400px; }

    /* ── BANNER GỌN GÀNG ── */
    .masthead {
        text-align: center;
        padding: 20px 15px 15px;
        background: #ffffff;
        border-top: 4px solid #C8102E;
        border-bottom: 2px solid #004B87;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .masthead-eyebrow {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #004B87;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .masthead-title {
        font-size: 36px;
        font-weight: 900;
        color: #111827;
        margin: 0 0 5px 0;
        text-transform: uppercase;
    }
    .masthead-title span { color: #C8102E; }
    .masthead-subtitle {
        font-size: 15px;
        color: #4B5563;
        font-weight: 500;
        margin: 0;
    }
    
    /* ── BADGE LIVE CẬP NHẬT ── */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FEF2F2;
        border: 1px solid #FECACA;
        color: #DC2626;
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
        padding: 4px 10px;
        border-radius: 20px;
        margin-top: 10px;
    }
    .live-dot {
        width: 8px; height: 8px;
        background: #DC2626;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
    }

    /* ── THANH ĐIỀU CHỈNH SỐ LƯỢNG TIN ── */
    .filter-box {
        background: #ffffff;
        padding: 15px 20px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    
    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #ffffff !important;
        border-bottom: 2px solid #CBD5E1 !important;
        border-radius: 8px 8px 0 0;
        padding: 5px 10px 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        color: #64748B !important;
        font-size: 14px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        padding: 12px 15px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #C8102E !important;
        border-bottom: 3px solid #C8102E !important;
    }

    /* ── NEWS CARDS ── */
    .news-card {
        background: #ffffff;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 15px;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
        border-color: #004B87;
    }
    .news-tag {
        display: inline-block;
        font-size: 10px;
        font-weight: 800;
        color: #004B87;
        background: #EFF6FF;
        padding: 3px 8px;
        border-radius: 4px;
        margin-bottom: 10px;
    }
    .news-title {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        text-decoration: none;
        line-height: 1.4;
        margin-bottom: 8px;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .news-title:hover { color: #C8102E; }
    .news-summary {
        font-size: 14px;
        color: #475569;
        line-height: 1.5;
        margin-bottom: 10px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .news-meta {
        margin-top: auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-top: 1px dashed #E2E8F0;
        padding-top: 10px;
    }
    .news-date {
        font-size: 11px;
        color: #64748B;
        font-weight: 600;
    }
    .read-link {
        font-size: 12px;
        font-weight: bold;
        color: #C8102E;
        text-decoration: none;
    }
    .read-link:hover { text-decoration: underline; }

    /* ── SCROLL TO TOP BUTTON ── */
    .scroll-top {
        position: fixed; bottom: 30px; right: 30px;
        background: #004B87; color: white !important;
        border-radius: 50%; width: 45px; height: 45px;
        display: flex; justify-content: center; align-items: center;
        font-size: 20px; text-decoration: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 99;
    }
    .scroll-top:hover { background: #C8102E; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CẤU HÌNH NGUỒN TIN
# ==========================================
RSS_FEEDS = {
    "🔥 Tiêu điểm 24h": {"url": "https://news.google.com/news/rss/headlines/section/topic/NATION?hl=vi&gl=VN&ceid=VN%3Avi", "tag": "TRONG NƯỚC"},
    "🌍 Quốc tế": {"url": "https://www.vietnamplus.vn/rss/thegioi.rss", "tag": "QUỐC TẾ"},
    "📍 Tuyên Quang": {"url": "https://news.google.com/rss/search?q=%22Tuy%C3%AAn+Quang%22+when:1d&hl=vi&gl=VN&ceid=VN:vi", "tag": "ĐỊA PHƯƠNG"},
    "🗣️ Dư luận XH": {"url": "https://news.google.com/rss/search?q=(%22d%C6%B0+lu%E1%BA%ADn%22+OR+%22b%E1%BB%A9c+x%C3%BAc%22+OR+%22ph%E1%BA%A3n+%C3%A1nh%22)+%22Tuy%C3%AAn+Quang%22+when:7d&hl=vi&gl=VN&ceid=VN:vi", "tag": "DƯ LUẬN"},
    "🤝 Dân vận khéo": {"url": "https://news.google.com/rss/search?q=%22d%C3%A2n+v%E1%BA%ADn+kh%C3%A9o%22+%22Tuy%C3%AAn+Quang%22+when:30d&hl=vi&gl=VN&ceid=VN:vi", "tag": "DÂN VẬN"},
    "🏛️ Tuyên giáo TW": {"url": "https://news.google.com/rss/search?q=(site:dangcongsan.vn+OR+site:tuyengiaodanvan.vn+OR+site:nhandan.vn)+(%22Ban+Tuy%C3%AAn+gi%C3%A1o%22+OR+%22D%C3%A2n+v%E1%BA%ADn%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi", "tag": "TUYÊN GIÁO"},
    "🇻🇳 TTXVN": {"url": "https://news.google.com/rss/search?q=site:baotintuc.vn+(%22th%E1%BB%9Di+s%E1%BB%B1%22+OR+%22ch%C3%ADnh+tr%E1%BB%8B%22+OR+%22l%C3%A3nh+%C4%91%E1%BA%A1o%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi", "tag": "TTXVN"}
}

BLACKLIST = ["bbc", "rfa", "voa", "rfi", "việt tân", "viet tan", "luatkhoa", "thoibao", "nguoi-viet"]

def is_safe(entry):
    content = (entry.get("title", "") + " " + entry.get("link", "") + " " + entry.get("summary", "")).lower()
    for bad_word in BLACKLIST:
        if bad_word in content: return False
    return True

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    return " ".join(re.sub(cleanr, '', raw_html).split())

def format_date(date_str):
    if not date_str: return "—"
    parts = date_str.split(" ")
    if len(parts) >= 5: return " ".join(parts[1:5])
    return date_str[:25]

def score_entry(entry):
    score = 0
    content = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    priority = ["tổng bí thư", "chủ tịch nước", "thủ tướng", "quốc hội", "nghị quyết", "chỉ thị", "quyết định", "hội nghị", "ban chấp hành", "điều tra", "khởi tố", "bắt giữ", "tham nhũng", "lũ lụt", "thiên tai", "dịch bệnh", "khẩn cấp"]
    for kw in priority:
        if kw in content: score += 2
    if len(entry.get("summary", "")) > 200: score += 1
    return score

@st.cache_data(ttl=900)
def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        safe_entries = [e for e in feed.entries if is_safe(e)]
        safe_entries.sort(key=score_entry, reverse=True)
        return safe_entries[:50]
    except Exception as e:
        return []

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
today_str = datetime.datetime.now().strftime("%d/%m/%Y")

# 1. Banner Header (Gọn gàng)
st.markdown(f"""
<div class="masthead">
    <div class="masthead-eyebrow">BAN TUYÊN GIÁO VÀ DÂN VẬN TỈNH ỦY TUYÊN QUANG</div>
    <h1 class="masthead-title">ĐIỂM TIN <span>BÁO CHÍ</span></h1>
    <p class="masthead-subtitle">Cập nhật lúc: {today_str}</p>
    <span class="live-badge"><span class="live-dot"></span>ĐANG CẬP NHẬT 24/7</span>
</div>
""", unsafe_allow_html=True)

# 2. Thanh lọc số lượng tin (Đưa ra ngoài)
with st.container():
    st.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        st.markdown("<b style='color:#004B87; font-size:14px;'>⚙ TÙY CHỈNH HIỂN THỊ:</b>", unsafe_allow_html=True)
    with c2:
        so_luong_tin = st.slider("Số lượng tin/mục:", min_value=3, max_value=30, value=9, step=3, label_visibility="collapsed")
    with c3:
        if st.button("🔄 Làm mới tin tức", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# 3. Tabs Nội dung
tab_labels = list(RSS_FEEDS.keys())
tabs = st.tabs(tab_labels)

for i, (tab_name, cfg) in enumerate(RSS_FEEDS.items()):
    with tabs[i]:
        with st.spinner(f"Đang lấy tin {tab_name}..."):
            entries = fetch_rss(cfg["url"])

        if not entries:
            st.info("📭 Chưa có tin mới trong chuyên mục này.")
        else:
            entries_to_show = entries[:so_luong_tin]
            tag = cfg["tag"]
            
            st.markdown(f"<p style='color:#004B87; font-weight:bold; margin-top:10px;'>Đang hiển thị {len(entries_to_show)} tin bài nổi bật nhất:</p>", unsafe_allow_html=True)

            cols = st.columns(3)
            for idx, entry in enumerate(entries_to_show):
                title = entry.get("title", "Không có tiêu đề")
                link = entry.get("link", "#")
                pub_date = format_date(entry.get("published", ""))
                summary = clean_html(entry.get("summary", ""))

                card_html = f"""
                <div class="news-card">
                    <span class="news-tag">{tag}</span>
                    <a class="news-title" href="{link}" target="_blank">{title}</a>
                    <div class="news-summary">{summary}</div>
                    <div class="news-meta">
                        <span class="news-date">🕒 {pub_date}</span>
                        <a class="read-link" href="{link}" target="_blank">Đọc tiếp →</a>
                    </div>
                </div>
                """
                with cols[idx % 3]:
                    st.markdown(card_html, unsafe_allow_html=True)

# Footer & Nút cuộn lên
st.markdown("""
<hr>
<div style='text-align:center; color:#64748B; font-size:12px; margin-bottom:20px;'>
    Hệ thống Điểm tin Tự động · Nguồn: TTXVN, Báo Nhân Dân, Google News
</div>
<a href="#top-of-page" class="scroll-top" title="Lên đầu trang">⬆</a>
""", unsafe_allow_html=True)
