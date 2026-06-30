"""
HỆ THỐNG ĐIỂM TIN & LẮNG NGHE DƯ LUẬN - PHIÊN BẢN V5.7 (LOCAL FOCUSED + FRESH SOCIAL + WIDE COVERAGE)
Cập nhật so với v5.6:
  - Mục "Dư luận MXH": thu hẹp cửa sổ thời gian (2 ngày), sắp xếp theo TIN MỚI NHẤT thay vì điểm số,
    gộp nhiều truy vấn để có nguồn tin tươi hơn.
  - Mục "Địa phương": mở rộng tối đa 200 tin, gộp nhiều truy vấn theo từng huyện/thành phố
    (bao gồm cả địa bàn Hà Giang cũ sau sáp nhập) để quét toàn bộ tin liên quan tới tỉnh.
  - Giao diện làm mới: header gradient, thẻ tin bo góc mềm, hiệu ứng hover tinh tế hơn,
    badge cảm xúc dạng pill, khu vực thống kê trực quan hơn.
"""

import streamlit as st
import feedparser
import re
import time
import datetime
from urllib.parse import quote
from supabase import create_client, Client

try:
    import pandas as pd
    import plotly.express as px
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

st.set_page_config(
    page_title="Điểm Tin & Dư Luận · TGDV",
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
        _sb.table("thong_ke_truy_cap").insert({"ten_app": "Điểm tin & Social Listening"}).execute()
        st.session_state["da_ghi_truy_cap"] = True
    except Exception:
        pass

# ==========================================
# CSS GIAO DIỆN HIỆN ĐẠI (V5.7)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif !important; }
    .stApp { background: linear-gradient(180deg, #F4F6F9 0%, #F8F9FA 250px); }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1440px; }

    /* ── BANNER GRADIENT ── */
    .masthead {
        text-align: center; padding: 28px 20px 22px; position: relative; overflow: hidden;
        background: linear-gradient(135deg, #0D1B2A 0%, #1B2F47 55%, #0D1B2A 100%);
        border-radius: 16px; margin-bottom: 22px; box-shadow: 0 10px 30px rgba(13,27,42,0.25);
    }
    .masthead::before {
        content: ""; position: absolute; top: -60px; right: -60px; width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(200,16,46,0.35) 0%, rgba(200,16,46,0) 70%);
    }
    .masthead::after {
        content: ""; position: absolute; bottom: -80px; left: -40px; width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(245,166,35,0.25) 0%, rgba(245,166,35,0) 70%);
    }
    .masthead-eyebrow { position:relative; font-size: 12.5px; font-weight: 800; letter-spacing: 2px; color: #F5A623; text-transform: uppercase; margin-bottom: 10px; }
    .masthead-title { position:relative; font-size: 34px; font-weight: 900; color: #ffffff; margin: 0 0 6px 0; text-transform: uppercase; letter-spacing: 0.5px; }
    .masthead-title span { color: #FF4D5E; }
    .masthead-subtitle { position:relative; font-size: 14px; color: #C9D2DC; font-weight: 500; margin: 0; }

    .live-badge {
        position:relative; display: inline-flex; align-items: center; gap: 7px;
        background: rgba(220,38,38,0.15); border: 1px solid rgba(255,77,94,0.5); color: #FF8A93;
        font-size: 11px; font-weight: bold; letter-spacing: 1px; padding: 5px 12px; border-radius: 20px; margin-top: 12px;
    }
    .live-dot { width: 8px; height: 8px; background: #FF4D5E; border-radius: 50%; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } }

    /* ── THANH ĐIỀU CHỈNH ── */
    .filter-box {
        background: #ffffff; padding: 16px 22px; border-radius: 14px;
        border: 1px solid #E6EAF0; box-shadow: 0 4px 14px rgba(13,27,42,0.05);
        margin-bottom: 20px;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] { background: #ffffff !important; border-bottom: 2px solid #E6EAF0 !important; border-radius: 14px 14px 0 0; padding: 6px 12px 0; box-shadow: 0 2px 8px rgba(13,27,42,0.04); }
    .stTabs [data-baseweb="tab"] { background: transparent !important; border: none !important; color: #64748B !important; font-size: 13.5px !important; font-weight: 700 !important; text-transform: uppercase; padding: 13px 16px !important; letter-spacing: 0.3px; }
    .stTabs [aria-selected="true"] { color: #C8102E !important; border-bottom: 3px solid #C8102E !important; }

    /* ── NEWS CARDS ── */
    .news-card {
        background: #ffffff; border: 1px solid #E6EAF0; border-radius: 14px;
        padding: 18px; margin-bottom: 16px; min-height: 168px; display: flex; flex-direction: column;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        position: relative; overflow: hidden;
    }
    .news-card::before {
        content: ""; position: absolute; top:0; left:0; right:0; height: 3px;
        background: linear-gradient(90deg, #C8102E, #F5A623);
        opacity: 0; transition: opacity 0.18s ease;
    }
    .news-card:hover { transform: translateY(-3px); box-shadow: 0 10px 22px rgba(13,27,42,0.10); border-color: #0D1B2A22; }
    .news-card:hover::before { opacity: 1; }
    .news-tag { display: inline-block; font-size: 10px; font-weight: 800; letter-spacing: 0.4px; color: #0D1B2A; background: #EEF2F8; padding: 4px 9px; border-radius: 6px; margin-bottom: 10px; }
    .news-title { font-size: 15px; font-weight: 700; color: #0F172A; text-decoration: none; line-height: 1.4; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
    .news-title:hover { color: #C8102E; }
    .news-summary { font-size: 13px; color: #475569; line-height: 1.5; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .news-meta { margin-top: auto; display: flex; align-items: center; justify-content: space-between; border-top: 1px dashed #E6EAF0; padding-top: 10px; }
    .news-date { font-size: 11px; color: #64748B; font-weight: 600; }
    .read-link { font-size: 12px; font-weight: bold; color: #C8102E; text-decoration: none; }
    .read-link:hover { text-decoration: underline; }

    /* ── PILL BADGE CẢM XÚC ── */
    .sentiment-badge { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 10.5px; font-weight: 800; margin-bottom: 8px; border: 1px solid; letter-spacing: 0.3px; }

    /* ── DASHBOARD ── */
    .dashboard-box { background: white; border-radius: 14px; padding: 16px; border: 1px solid #E6EAF0; box-shadow: 0 4px 14px rgba(13,27,42,0.05); height: 100%; }
    .kpi-title { font-size: 12.5px; color: #64748B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 5px;}
    .kpi-value { font-size: 32px; font-weight: 900; }

    /* ── SCROLL TO TOP ── */
    .scroll-top { position: fixed; bottom: 30px; right: 30px; background: #0D1B2A; color: white !important; border-radius: 50%; width: 46px; height: 46px; display: flex; justify-content: center; align-items: center; font-size: 20px; text-decoration: none !important; box-shadow: 0 6px 16px rgba(13,27,42,0.35); z-index: 99; }
    .scroll-top:hover { background: #C8102E; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DANH SÁCH HUYỆN/THÀNH PHỐ ĐỂ QUÉT DIỆN RỘNG
# (gồm cả địa bàn Hà Giang cũ sau sáp nhập với Tuyên Quang)
# ==========================================
DISTRICTS_FOR_WIDE_SCAN = [
    "Tuyên Quang", "Hàm Yên", "Sơn Dương", "Chiêm Hóa", "Nà Hang", "Lâm Bình", "Yên Sơn",
    "Hà Giang", "Bắc Quang", "Quang Bình", "Vị Xuyên", "Bắc Mê",
    "Hoàng Su Phì", "Xín Mần", "Quản Bạ", "Yên Minh", "Đồng Văn", "Mèo Vạc",
]

# ==========================================
# CẤU HÌNH NGUỒN TIN (RSS đơn) — dùng cho các tab không cần quét diện rộng
# ==========================================
RSS_FEEDS = {
    "🔥 Tiêu điểm 24h": {"url": "https://news.google.com/news/rss/headlines/section/topic/NATION?hl=vi&gl=VN&ceid=VN%3Avi", "tag": "TRONG NƯỚC"},
    "🌍 Quốc tế": {"url": "https://www.vietnamplus.vn/rss/thegioi.rss", "tag": "QUỐC TẾ"},
    "🗣️ Dư luận MXH": {"url": None, "tag": "MẠNG XÃ HỘI"},
    "📍 Địa phương": {"url": None, "tag": "ĐỊA PHƯƠNG"},
    "🤝 Dân vận khéo": {"url": "https://news.google.com/rss/search?q=%22d%C3%A2n+v%E1%BA%ADn+kh%C3%A9o%22+%22Tuy%C3%AAn+Quang%22+when:30d&hl=vi&gl=VN&ceid=VN:vi", "tag": "DÂN VẬN"},
    "🏛️ Tuyên giáo TW": {"url": "https://news.google.com/rss/search?q=(site:dangcongsan.vn+OR+site:tuyengiaodanvan.vn+OR+site:nhandan.vn)+(%22Ban+Tuy%C3%AAn+gi%C3%A1o%22+OR+%22D%C3%A2n+v%E1%BA%ADn%22)+when:3d&hl=vi&gl=VN&ceid=VN:vi", "tag": "TUYÊN GIÁO"},
}

BLACKLIST = ["bbc", "rfa", "voa", "rfi", "việt tân", "viet tan", "luatkhoa", "thoibao", "nguoi-viet"]

LOCAL_KEYWORDS = [
    "tuyên quang", "hàm yên", "sơn dương", "chiêm hóa", "nà hang", "na hang", "lâm bình", "yên sơn",
    "hà giang 2", "tân trịnh", "thái hòa", "sơn thủy", "tát ngà", "an tường", "bắc mê", "bắc quang",
    "bạch đích", "bạch ngọc", "bạch xa", "bản máy", "bằng hành", "bằng lang", "bình an", "bình ca",
    "bình thuận", "bình xa", "cán tỷ", "cao bồ", "côn lôn", "đồng tâm", "đông thọ", "đồng văn",
    "đồng yên", "du già", "đường hồng", "đường thượng", "giáp trung", "hà giang 1", "hồ thầu",
    "hoàng su phì", "hồng sơn", "hồng thái", "hùng an", "hùng đức", "hùng lợi", "khâu vai",
    "khuôn lùng", "kiên đài", "kiến thiết", "hòa an", "kim bình", "lao chải", "liên hiệp", "linh hồ",
    "lực hành", "lũng cú", "lũng phìn", "lùng tám", "mậu duệ", "mèo vạc", "minh ngọc", "minh quang",
    "minh sơn", "minh tân", "minh thanh", "minh xuân", "mỹ lâm", "nấm dẩn", "nậm dịch", "nghĩa thuận",
    "ngọc đường", "ngọc long", "nhữ khê", "niêm sơn", "nông tiến", "pà vầy sủ", "phố bảng", "phú linh",
    "phú lương", "phù lưu", "pờ ly ngài", "quản bạ", "quang bình", "quảng nguyên", "sà phìn",
    "tùng bá", "sơn vĩ", "sủng máng", "tân an", "tân long", "tân mỹ", "tân quang", "tân thanh",
    "tân tiến", "tân trào", "thái bình", "thuận hòa", "thái sơn", "thắng mố", "thàng tín",
    "thanh thủy", "thông nguyên", "thượng lâm", "thượng nông", "thượng sơn", "tiên nguyên",
    "tiên yên", "tri phú", "trung hà", "trung sơn", "trung thịnh", "trường sinh", "tùng vài",
    "vị xuyên", "việt lâm", "vĩnh tuy", "xín mần", "xuân giang", "xuân vân", "yên cường", "yên hoa",
    "yên lập", "yên minh", "yên nguyên", "yên phú", "yên thành"
]

SOCIAL_SIGNAL_WORDS = [
    "facebook", "fanpage", "mạng xã hội", "tiktok", "zalo", "youtube", "group", "hội nhóm",
    "bình luận", "chia sẻ", "lan truyền", "viral", "dư luận", "phản ánh", "bức xúc"
]


def is_safe(entry):
    content = (entry.get("title", "") + " " + entry.get("link", "") + " " + entry.get("summary", "")).lower()
    for bad_word in BLACKLIST:
        if bad_word in content:
            return False
    return True


def clean_html(raw_html):
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    return " ".join(re.sub(cleanr, '', raw_html).split())


def format_date(date_str):
    if not date_str:
        return "—"
    parts = date_str.split(" ")
    if len(parts) >= 5:
        return " ".join(parts[1:5])
    return date_str[:25]


def parse_pub_time(entry):
    """Trả về timestamp (giây) để sắp xếp theo độ mới. Tin không có ngày -> coi như cũ nhất."""
    try:
        if entry.get("published_parsed"):
            return time.mktime(entry["published_parsed"])
    except Exception:
        pass
    return 0


def analyze_sentiment(title, summary):
    text = (title + " " + summary).lower()
    neg_words = ['bức xúc', 'sai phạm', 'kêu cứu', 'phản ánh', 'ô nhiễm', 'ngập', 'xuống cấp', 'chậm tiến độ', 'đền bù', 'giải tỏa', 'tệ nạn', 'vi phạm', 'bất cập', 'chưa được', 'lừa đảo', 'chiếm đoạt', 'bắt giữ', 'khởi tố']
    pos_words = ['biểu dương', 'khen thưởng', 'hoàn thành', 'vượt mức', 'xây dựng nông thôn mới', 'khang trang', 'hiệu quả', 'ủng hộ', 'đóng góp', 'khắc phục', 'phát triển', 'thành công']

    neg_score = sum(1 for w in neg_words if w in text)
    pos_score = sum(1 for w in pos_words if w in text)

    if neg_score > pos_score:
        return "🔴 Tiêu cực", "#FEF2F2", "#DC2626", "Tiêu cực"
    elif pos_score > neg_score:
        return "🟢 Tích cực", "#F0FDF4", "#16A34A", "Tích cực"
    else:
        return "🟡 Trung lập", "#FFFBEB", "#D97706", "Trung lập"


def score_entry(entry):
    score = 0
    content = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    for kw in LOCAL_KEYWORDS:
        if kw in content:
            score += 2
    if len(entry.get("summary", "")) > 100:
        score += 1
    return score


def gnews_query_url(query, when="3d"):
    return f"https://news.google.com/rss/search?q={quote(query)}+when:{when}&hl=vi&gl=VN&ceid=VN:vi"


@st.cache_data(ttl=900)
def fetch_rss(url, require_local=False):
    try:
        feed = feedparser.parse(url)
        safe_entries = []
        for e in feed.entries:
            if not is_safe(e):
                continue
            if require_local:
                content = (e.get("title", "") + " " + e.get("summary", "")).lower()
                if not any(kw in content for kw in LOCAL_KEYWORDS):
                    continue
            safe_entries.append(e)
        safe_entries.sort(key=score_entry, reverse=True)
        return safe_entries[:50]
    except Exception:
        return []


@st.cache_data(ttl=900)
def fetch_multi_rss(queries, require_local=True, sort_mode="date", cap=200):
    """
    Gộp kết quả nhiều truy vấn Google News RSS, loại trùng (theo tiêu đề chuẩn hóa),
    lọc an toàn, lọc theo từ khóa địa phương (nếu cần), rồi sắp xếp.
    sort_mode: 'date' (tin mới nhất lên trước) hoặc 'score' (theo độ liên quan).
    """
    seen_titles = set()
    merged = []
    for q_url in queries:
        try:
            feed = feedparser.parse(q_url)
        except Exception:
            continue
        for e in feed.entries:
            if not is_safe(e):
                continue
            title_key = re.sub(r'\W+', '', e.get("title", "").lower())[:80]
            if not title_key or title_key in seen_titles:
                continue
            if require_local:
                content = (e.get("title", "") + " " + e.get("summary", "")).lower()
                if not any(kw in content for kw in LOCAL_KEYWORDS):
                    continue
            seen_titles.add(title_key)
            merged.append(e)

    if sort_mode == "date":
        merged.sort(key=parse_pub_time, reverse=True)
    else:
        merged.sort(key=score_entry, reverse=True)

    return merged[:cap]


# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
today_str = datetime.datetime.now().strftime("%d/%m/%Y")

st.markdown(f"""
<div class="masthead">
    <div class="masthead-eyebrow">BAN TUYÊN GIÁO VÀ DÂN VẬN TỈNH ỦY TUYÊN QUANG</div>
    <h1 class="masthead-title">ĐIỂM TIN & <span>LẮNG NGHE DƯ LUẬN</span></h1>
    <p class="masthead-subtitle">Hệ thống thu thập tin tức và phân tích mạng xã hội địa phương ứng dụng AI</p>
    <span class="live-badge"><span class="live-dot"></span>ĐANG CẬP NHẬT 24/7</span>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        st.markdown("<b style='color:#0D1B2A; font-size:14px;'>⚙ TÙY CHỈNH HIỂN THỊ:</b>", unsafe_allow_html=True)
    with c2:
        so_luong_tin = st.slider("Số lượng tin/mục hiển thị (các mục thường):", min_value=3, max_value=50, value=9, step=1, label_visibility="collapsed")
    with c3:
        st.write("")
        if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

tab_labels = list(RSS_FEEDS.keys())
tabs = st.tabs(tab_labels)

for i, (tab_name, cfg) in enumerate(RSS_FEEDS.items()):
    with tabs[i]:
        tag = cfg["tag"]

        # ---------------------------------------------------
        # TAB DƯ LUẬN MXH: quét diện hẹp 2 ngày, ưu tiên TIN MỚI
        # ---------------------------------------------------
        if tab_name == "🗣️ Dư luận MXH":
            with st.spinner("Đang quét tin mới nhất trên mạng xã hội..."):
                social_queries = [
                    gnews_query_url('("facebook" OR "fanpage" OR "mạng xã hội" OR "tiktok") "Tuyên Quang"', when="2d"),
                    gnews_query_url('("dư luận" OR "phản ánh" OR "bức xúc") "Tuyên Quang"', when="2d"),
                    gnews_query_url('"Tuyên Quang"', when="1d"),
                ]
                entries = fetch_multi_rss(social_queries, require_local=True, sort_mode="date", cap=80)

            if not entries:
                st.info("📭 Chưa có tin/bài mới trong 48 giờ qua liên quan đến Tuyên Quang trên mạng xã hội.")
                continue

            entries_to_show = entries[:so_luong_tin]

            sentiments = []
            for e in entries_to_show:
                t = e.get("title", "")
                s = clean_html(e.get("summary", ""))
                _, _, _, label = analyze_sentiment(t, s)
                sentiments.append(label)

            st.markdown("<h4 style='color:#0D1B2A; font-weight:800; text-transform:uppercase;'>🎯 Trạm Lắng Nghe & Phân Tích Mạng Xã Hội (48 giờ gần nhất)</h4>", unsafe_allow_html=True)

            d_col1, d_col2 = st.columns([1.2, 2.8])
            with d_col1:
                st.markdown(f"""
                <div class='dashboard-box'>
                    <div class='kpi-title'>Tin/Bài đang hiển thị</div>
                    <div class='kpi-value' style='color:#0D1B2A;'>{len(entries_to_show)} bài</div>
                    <hr style='margin:12px 0;'>
                    <div class='kpi-title' style='color:#DC2626'>Cảnh báo Tiêu cực</div>
                    <div class='kpi-value' style='color:#DC2626;'>{sentiments.count('Tiêu cực')} vụ</div>
                </div>
                """, unsafe_allow_html=True)
            with d_col2:
                st.markdown("<div class='dashboard-box'>", unsafe_allow_html=True)
                if HAS_LIBS and len(sentiments) > 0:
                    color_map = {"Tích cực": "#16A34A", "Trung lập": "#D97706", "Tiêu cực": "#DC2626"}
                    df_sent = pd.DataFrame(sentiments, columns=["Cảm xúc"])
                    sent_counts = df_sent["Cảm xúc"].value_counts().reset_index()
                    fig = px.pie(sent_counts, values='count', names='Cảm xúc', hole=0.55, color='Cảm xúc', color_discrete_map=color_map)
                    fig.update_traces(textposition='outside', textinfo='percent+label')
                    fig.update_layout(title=dict(text="Biểu đồ Phân tích Sắc thái Dư luận Tuyên Quang", font=dict(size=14, color='#475569')),
                                      margin=dict(t=40, b=10, l=10, r=10), height=220, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                elif not HAS_LIBS:
                    st.info("⚙️ Đang chờ máy chủ cài đặt bộ thư viện vẽ biểu đồ. Sếp vui lòng kiểm tra lại file 'requirements.txt' trên Github và nhấn Reboot App nhé!")
                else:
                    st.warning("Không đủ dữ liệu để vẽ biểu đồ.")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<hr style='margin:25px 0 15px;'>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#0D1B2A; font-weight:bold;'>Danh sách chi tiết, sắp xếp theo thời gian đăng mới nhất:</p>", unsafe_allow_html=True)

        # ---------------------------------------------------
        # TAB ĐỊA PHƯƠNG: quét diện rộng toàn bộ huyện/thành phố, tối đa 200 tin
        # ---------------------------------------------------
        elif tab_name == "📍 Địa phương":
            so_luong_dia_phuong = st.slider(
                "Số lượng tin Địa phương hiển thị (tối đa 200, quét toàn bộ huyện/thành phố trong tỉnh):",
                min_value=10, max_value=200, value=60, step=10
            )
            with st.spinner("Đang quét tin từ tất cả huyện/thành phố trong tỉnh..."):
                wide_queries = [gnews_query_url(f'"{d}"', when="14d") for d in DISTRICTS_FOR_WIDE_SCAN]
                entries = fetch_multi_rss(wide_queries, require_local=True, sort_mode="date", cap=200)

            if not entries:
                st.info("📭 Chưa có bài viết nào liên quan đến tỉnh Tuyên Quang trong 14 ngày qua.")
                continue

            entries_to_show = entries[:so_luong_dia_phuong]
            st.markdown(f"<p style='color:#0D1B2A; font-weight:bold; margin-top:10px;'>Đã quét {len(entries)} tin từ toàn bộ huyện/thành phố trong tỉnh · Đang hiển thị {len(entries_to_show)} tin mới nhất:</p>", unsafe_allow_html=True)

        # ---------------------------------------------------
        # CÁC TAB CÒN LẠI (RSS đơn nguồn)
        # ---------------------------------------------------
        else:
            with st.spinner(f"Đang xử lý dữ liệu {tab_name}..."):
                req_loc = tab_name == "🤝 Dân vận khéo"
                entries = fetch_rss(cfg["url"], require_local=req_loc)

            if not entries:
                st.info("📭 Chưa có bài viết nào trong khoảng thời gian thu thập.")
                continue

            entries_to_show = entries[:so_luong_tin]
            st.markdown(f"<p style='color:#0D1B2A; font-weight:bold; margin-top:10px;'>Đang hiển thị {len(entries_to_show)} tin bài nổi bật nhất:</p>", unsafe_allow_html=True)

        # =======================================================
        # RENDER DANH SÁCH TIN (DÙNG CHUNG)
        # =======================================================
        cols = st.columns(3)
        for idx, entry in enumerate(entries_to_show):
            title = entry.get("title", "Không có tiêu đề")
            link = entry.get("link", "#")
            pub_date = format_date(entry.get("published", ""))
            summary = clean_html(entry.get("summary", ""))

            badge_html = ""
            if tab_name == "🗣️ Dư luận MXH":
                lbl_text, bg_col, text_col, _ = analyze_sentiment(title, summary)
                badge_html = f"<div class='sentiment-badge' style='background:{bg_col}; color:{text_col}; border-color:{text_col}'>{lbl_text}</div>"

            card_html = f"""
            <div class="news-card">
                <div>
                    <span class="news-tag">{tag}</span>
                    <br>{badge_html}
                </div>
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

st.markdown("""
<hr>
<div style='text-align:center; color:#64748B; font-size:12px; margin-bottom:20px;'>
    Hệ thống Điểm tin & Lắng nghe Dư luận · Ban Tuyên giáo & Dân vận Tỉnh ủy Tuyên Quang
</div>
<a href="#top-of-page" class="scroll-top" title="Lên đầu trang">⬆</a>
""", unsafe_allow_html=True)
