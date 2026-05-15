import streamlit as st
import feedparser
import re
import time
from supabase import create_client, Client

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
# CSS GIAO DIỆN HIỆN ĐẠI - EDITORIAL STYLE
# ==========================================
st.markdown("""
<style>
    /* ── FONT IMPORTS ── */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Serif+4:ital,wght@0,300;0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    /* ── RESET & BASE ── */
    .stApp {
        background: #0d1117;
        background-image:
            radial-gradient(ellipse at 20% 0%, rgba(0,75,135,0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 100%, rgba(200,16,46,0.08) 0%, transparent 50%);
    }

    /* Ẩn header/footer mặc định của Streamlit */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1400px; }

    /* ── HEADER ── */
    .masthead {
        position: relative;
        text-align: center;
        padding: 48px 20px 36px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 8px;
        overflow: hidden;
    }
    .masthead::before {
        content: '';
        position: absolute;
        top: 0; left: 50%; transform: translateX(-50%);
        width: 1px; height: 40px;
        background: linear-gradient(to bottom, transparent, #C8102E);
    }
    .masthead-eyebrow {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 3px;
        color: #C8102E;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    .masthead-title {
        font-family: 'Playfair Display', serif;
        font-size: clamp(32px, 5vw, 62px);
        font-weight: 900;
        color: #ffffff;
        line-height: 1.05;
        letter-spacing: -1px;
        margin-bottom: 16px;
    }
    .masthead-title span { color: #C8102E; }
    .masthead-subtitle {
        font-family: 'Source Serif 4', serif;
        font-size: 15px;
        font-style: italic;
        color: rgba(255,255,255,0.45);
        max-width: 560px;
        margin: 0 auto;
        line-height: 1.6;
    }
    .masthead-date {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 11px;
        color: rgba(255,255,255,0.3);
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 20px;
    }
    .masthead-line {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-top: 24px;
    }
    .masthead-line::before, .masthead-line::after {
        content: '';
        flex: 1;
        max-width: 200px;
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(255,255,255,0.15));
    }
    .masthead-line::after {
        background: linear-gradient(to left, transparent, rgba(255,255,255,0.15));
    }
    .masthead-ornament {
        color: #C8102E;
        font-size: 18px;
    }

    /* ── BADGE TICKER (LIVE INDICATOR) ── */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(200,16,46,0.12);
        border: 1px solid rgba(200,16,46,0.3);
        color: #ff4d6d;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 20px;
    }
    .live-dot {
        width: 6px; height: 6px;
        background: #C8102E;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.8); }
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
        gap: 0 !important;
        padding: 0 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        color: rgba(255,255,255,0.45) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
        padding: 14px 20px !important;
        margin-bottom: -1px !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: rgba(255,255,255,0.8) !important;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #C8102E !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 28px;
    }

    /* ── NEWS CARDS ── */
    .card-grid { display: flex; flex-direction: column; gap: 0; }

    .news-card {
        position: relative;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 16px;
        display: flex;
        flex-direction: column;
        min-height: 180px;
        overflow: hidden;
        transition: background 0.25s ease, border-color 0.25s ease, transform 0.25s ease;
    }
    .news-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(to bottom, #004B87, #C8102E);
        opacity: 0;
        transition: opacity 0.25s ease;
        border-radius: 12px 0 0 12px;
    }
    .news-card:hover {
        background: rgba(255,255,255,0.055);
        border-color: rgba(255,255,255,0.12);
        transform: translateY(-3px);
    }
    .news-card:hover::before { opacity: 1; }

    /* Category tag */
    .news-tag {
        display: inline-block;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #C8102E;
        background: rgba(200,16,46,0.1);
        border: 1px solid rgba(200,16,46,0.25);
        padding: 2px 8px;
        border-radius: 4px;
        margin-bottom: 12px;
        width: fit-content;
    }

    .news-title {
        font-family: 'Playfair Display', serif;
        font-size: 16px;
        font-weight: 700;
        color: #f0f4f8;
        text-decoration: none;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        line-height: 1.45;
        margin-bottom: 12px;
        transition: color 0.2s;
    }
    .news-title:hover { color: #7eb8f7; text-decoration: none; }

    .news-meta {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: auto;
        padding-top: 12px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    .news-date {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 11px;
        color: rgba(255,255,255,0.3);
        letter-spacing: 0.5px;
    }
    .news-dot { color: rgba(255,255,255,0.15); font-size: 10px; }

    .news-summary {
        font-family: 'Source Serif 4', serif;
        font-size: 13px;
        color: rgba(255,255,255,0.45);
        line-height: 1.65;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        margin-bottom: 4px;
    }

    /* Read more link */
    .read-link {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 11px;
        font-weight: 600;
        color: rgba(126, 184, 247, 0.7);
        text-decoration: none;
        letter-spacing: 0.5px;
    }
    .read-link:hover { color: #7eb8f7; }

    /* ── FEATURED (FIRST) CARD ── */
    .news-card-featured {
        background: linear-gradient(135deg, rgba(0,75,135,0.2) 0%, rgba(0,75,135,0.05) 100%);
        border: 1px solid rgba(0,75,135,0.3);
        min-height: 220px;
    }
    .news-card-featured .news-title {
        font-size: 19px;
        -webkit-line-clamp: 4;
    }
    .news-card-featured .news-tag {
        color: #7eb8f7;
        background: rgba(0,75,135,0.2);
        border-color: rgba(0,75,135,0.4);
    }

    /* ── SECTION HEADER ── */
    .section-header {
        display: flex;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 24px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .section-count {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 11px;
        color: rgba(255,255,255,0.25);
        letter-spacing: 1px;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: #0a0e14 !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #7eb8f7;
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 13px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] .stSlider label {
        color: rgba(255,255,255,0.6) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 12px !important;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: rgba(255,255,255,0.4);
        font-size: 12px;
    }

    /* ── EMPTY STATE ── */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: rgba(255,255,255,0.25);
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 13px;
        letter-spacing: 0.5px;
    }
    .empty-state-icon { font-size: 36px; margin-bottom: 12px; opacity: 0.4; }

    /* ── FOOTER ── */
    .site-footer {
        text-align: center;
        padding: 32px 20px;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin-top: 20px;
    }
    .site-footer p {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 11px;
        color: rgba(255,255,255,0.2);
        letter-spacing: 1px;
        text-transform: uppercase;
        margin: 4px 0;
    }

    /* ── SCROLL TO TOP BUTTON ── */
    .scroll-top {
        position: fixed;
        bottom: 90px;
        right: 28px;
        background: #004B87;
        color: white !important;
        border-radius: 50%;
        width: 46px;
        height: 46px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 20px;
        text-decoration: none !important;
        box-shadow: 0 4px 20px rgba(0,75,135,0.5);
        z-index: 99999;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .scroll-top:hover {
        background: #C8102E;
        box-shadow: 0 6px 24px rgba(200,16,46,0.5);
        transform: translateY(-4px);
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #C8102E !important; }
    [data-testid="stSpinnerContainer"] p {
        color: rgba(255,255,255,0.4) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 12px !important;
    }

    /* Info box */
    .stAlert {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: rgba(255,255,255,0.4) !important;
        border-radius: 8px !important;
    }

    @media (max-width: 768px) {
        .masthead { padding: 32px 12px 24px; }
        .masthead-title { font-size: 28px; }
        .stTabs [data-baseweb="tab"] { padding: 10px 12px !important; font-size: 10px !important; }
        .news-card { padding: 16px; }
        .scroll-top { width: 40px; height: 40px; font-size: 17px; bottom: 80px; right: 16px; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CẤU HÌNH NGUỒN TIN
# ==========================================
RSS_FEEDS = {
    "🔥 Tiêu điểm 24h": {
        "url": "https://news.google.com/news/rss/headlines/section/topic/NATION?hl=vi&gl=VN&ceid=VN%3Avi",
        "tag": "TRONG NƯỚC",
        "color": "#ff4d6d"
    },
    "🌍 Quốc tế": {
        "url": "https://www.vietnamplus.vn/rss/thegioi.rss",
        "tag": "QUỐC TẾ",
        "color": "#64b5f6"
    },
    "📍 Tuyên Quang": {
        "url": "https://news.google.com/rss/search?q=%22Tuy%C3%AAn+Quang%22+when:1d&hl=vi&gl=VN&ceid=VN:vi",
        "tag": "ĐỊA PHƯƠNG",
        "color": "#81c784"
    },
    "🗣️ Dư luận XH": {
        "url": "https://news.google.com/rss/search?q=(%22d%C6%B0+lu%E1%BA%ADn%22+OR+%22b%E1%BB%A9c+x%C3%BAc%22+OR+%22ph%E1%BA%A3n+%C3%A1nh%22)+%22Tuy%C3%AAn+Quang%22+when:7d&hl=vi&gl=VN&ceid=VN:vi",
        "tag": "DƯ LUẬN",
        "color": "#ffb74d"
    },
    "🤝 Dân vận khéo": {
        "url": "https://news.google.com/rss/search?q=%22d%C3%A2n+v%E1%BA%ADn+kh%C3%A9o%22+%22Tuy%C3%AAn+Quang%22+when:30d&hl=vi&gl=VN&ceid=VN:vi",
        "tag": "DÂN VẬN",
        "color": "#ce93d8"
    },
    "🏛️ Tuyên giáo TW": {
        "url": "https://news.google.com/rss/search?q=(site:dangcongsan.vn+OR+site:tuyengiaodanvan.vn+OR+site:nhandan.vn)+(%22Ban+Tuy%C3%AAn+gi%C3%A1o%22+OR+%22D%C3%A2n+v%E1%BA%ADn%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi",
        "tag": "TUYÊN GIÁO",
        "color": "#4dd0e1"
    },
    "🇻🇳 TTXVN": {
        "url": "https://news.google.com/rss/search?q=site:baotintuc.vn+(%22th%E1%BB%9Di+s%E1%BB%B1%22+OR+%22ch%C3%ADnh+tr%E1%BB%8B%22+OR+%22l%C3%A3nh+%C4%91%E1%BA%A1o%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi",
        "tag": "TTXVN",
        "color": "#a5d6a7"
    }
}

# ==========================================
# BỘ LỌC KIỂM DUYỆT (GIỮ NGUYÊN BLACKLIST GỐC)
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

def format_date(date_str):
    """Rút gọn chuỗi ngày tháng cho dễ đọc hơn."""
    if not date_str:
        return "—"
    # Lấy phần ngày + giờ cơ bản, bỏ timezone dài
    parts = date_str.split(" ")
    if len(parts) >= 5:
        return " ".join(parts[1:5])
    return date_str[:25]

def score_entry(entry):
    """Chấm điểm tin để ưu tiên hiển thị (lọc thông minh)."""
    score = 0
    title = entry.get("title", "").lower()
    summary = entry.get("summary", "").lower()
    content = title + " " + summary
    # Từ khóa ưu tiên cao
    priority_keywords = [
        "tổng bí thư", "chủ tịch nước", "thủ tướng", "quốc hội",
        "nghị quyết", "chỉ thị", "quyết định", "hội nghị", "ban chấp hành",
        "điều tra", "khởi tố", "bắt giữ", "tham nhũng",
        "lũ lụt", "thiên tai", "dịch bệnh", "khẩn cấp"
    ]
    for kw in priority_keywords:
        if kw in content:
            score += 2
    # Các từ khóa thứ cấp
    secondary_keywords = ["khai mạc", "bế mạc", "ra mắt", "triển khai", "ký kết", "trao đổi"]
    for kw in secondary_keywords:
        if kw in content:
            score += 1
    # Ưu tiên tin có summary dài (nội dung đầy đủ hơn)
    if len(summary) > 200:
        score += 1
    return score

@st.cache_data(ttl=900)
def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        safe_entries = [e for e in feed.entries if is_safe(e)]
        # Sắp xếp theo điểm ưu tiên (tin quan trọng lên đầu)
        safe_entries.sort(key=score_entry, reverse=True)
        return safe_entries[:50]
    except Exception as e:
        return []

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#7eb8f7; font-family: IBM Plex Sans, sans-serif; font-size:13px; letter-spacing:2px; text-transform:uppercase;'>⚙ Tùy chỉnh</h3>", unsafe_allow_html=True)
    so_luong_tin = st.slider("Số bài mỗi mục:", min_value=3, max_value=30, value=12, step=3)
    st.markdown("---")
    st.markdown("""
    <p style='color:rgba(255,255,255,0.35); font-size:12px; line-height:1.7;'>
    💡 <strong style='color:rgba(255,255,255,0.5);'>Lọc thông minh:</strong> Tin quan trọng (hội nghị, nghị quyết, lãnh đạo) được ưu tiên hiển thị trước.<br><br>
    🔄 Dữ liệu tự cập nhật mỗi <strong style='color:rgba(255,255,255,0.5);'>15 phút</strong>.<br><br>
    ⌨️ Nhấn <code style='background:rgba(255,255,255,0.1); padding:1px 5px; border-radius:3px;'>C</code> để làm mới ngay.
    </p>
    """, unsafe_allow_html=True)

# ==========================================
# MASTHEAD
# ==========================================
import datetime
today_str = datetime.datetime.now().strftime("%A, %d/%m/%Y").upper()

st.markdown(f"""
<div class="masthead">
    <div class="masthead-eyebrow">Ban Tuyên giáo &amp; Dân vận · Tuyên Quang</div>
    <h1 class="masthead-title">Điểm Tin <span>Báo Chí</span></h1>
    <p class="masthead-subtitle">Tổng hợp thời sự, chính trị, dư luận xã hội — cập nhật liên tục 24/7</p>
    <div class="masthead-line"><span class="masthead-ornament">◆</span></div>
    <div class="masthead-date">{today_str}</div>
    <br>
    <span class="live-badge"><span class="live-dot"></span>ĐANG CẬP NHẬT</span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# TABS + NỘI DUNG
# ==========================================
tab_labels = list(RSS_FEEDS.keys())
tabs = st.tabs(tab_labels)

for i, (tab_name, cfg) in enumerate(RSS_FEEDS.items()):
    with tabs[i]:
        with st.spinner("Đang tổng hợp tin tức..."):
            entries = fetch_rss(cfg["url"])

        if not entries:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                Chưa có tin mới trong chuyên mục này.
            </div>
            """, unsafe_allow_html=True)
        else:
            entries_to_show = entries[:so_luong_tin]
            count = len(entries_to_show)
            tag = cfg["tag"]

            st.markdown(f"""
            <div class="section-header">
                <span class="live-badge"><span class="live-dot"></span>{tag}</span>
                <span class="section-count">{count} TIN BÀI</span>
            </div>
            """, unsafe_allow_html=True)

            # Layout: cột đặc trưng tuỳ số lượng
            cols = st.columns(3)
            for idx, entry in enumerate(entries_to_show):
                title = entry.get("title", "Không có tiêu đề")
                link = entry.get("link", "#")
                pub_date = format_date(entry.get("published", ""))
                summary = clean_html(entry.get("summary", ""))

                # Tin đầu tiên: nổi bật hơn
                featured_class = "news-card-featured" if idx == 0 else ""

                card_html = f"""<div class="news-card {featured_class}">
<span class="news-tag">{tag}</span>
<a class="news-title" href="{link}" target="_blank" rel="noopener noreferrer">{title}</a>
<div class="news-summary">{summary}</div>
<div class="news-meta">
<span class="news-date">🕒 {pub_date}</span>
<span class="news-dot">·</span>
<a class="read-link" href="{link}" target="_blank" rel="noopener noreferrer">Đọc tiếp →</a>
</div>
</div>"""
                with cols[idx % 3]:
                    st.markdown(card_html, unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="site-footer">
    <p>Nguồn dữ liệu: TTXVN · Báo điện tử Đảng Cộng sản · Báo Tuyên Quang · Google News</p>
    <p style="margin-top:6px; color:rgba(255,255,255,0.12);">Hệ thống điểm tin tự động · Cập nhật mỗi 15 phút</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# NÚT CUỘN LÊN ĐẦU TRANG
# ==========================================
st.markdown("""
<a href="#top-of-page" class="scroll-top" title="Lên đầu trang">⬆</a>
""", unsafe_allow_html=True)
