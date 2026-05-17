"""
HỆ THỐNG ĐIỂM TIN & LẮNG NGHE DƯ LUẬN - PHIÊN BẢN V5.0 (ALL-IN-ONE)
Đã vá: Tích hợp AI Phân tích Cảm xúc và Khảo sát trực tuyến vào Tab Dư luận XH
"""

import streamlit as st
import feedparser
import re
import time
import datetime
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

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
# CSS GIAO DIỆN HIỆN ĐẠI
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] { font-family: 'Be Vietnam Pro', sans-serif !important; }
    .stApp { background-color: #F8F9FA; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1rem; padding-bottom: 3rem; max-width: 1400px; }

    /* ── BANNER GỌN GÀNG ── */
    .masthead {
        text-align: center; padding: 20px 15px 15px; background: #ffffff;
        border-top: 4px solid #C8102E; border-bottom: 2px solid #004B87;
        border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .masthead-eyebrow { font-size: 13px; font-weight: 800; letter-spacing: 1.5px; color: #004B87; text-transform: uppercase; margin-bottom: 8px; }
    .masthead-title { font-size: 32px; font-weight: 900; color: #111827; margin: 0 0 5px 0; text-transform: uppercase; }
    .masthead-title span { color: #C8102E; }
    .masthead-subtitle { font-size: 14px; color: #4B5563; font-weight: 500; margin: 0; }
    
    .live-badge {
        display: inline-flex; align-items: center; gap: 6px; background: #FEF2F2;
        border: 1px solid #FECACA; color: #DC2626; font-size: 11px; font-weight: bold;
        letter-spacing: 1px; padding: 4px 10px; border-radius: 20px; margin-top: 10px;
    }
    .live-dot { width: 8px; height: 8px; background: #DC2626; border-radius: 50%; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] { background: #ffffff !important; border-bottom: 2px solid #CBD5E1 !important; border-radius: 8px 8px 0 0; padding: 5px 10px 0; }
    .stTabs [data-baseweb="tab"] { background: transparent !important; border: none !important; color: #64748B !important; font-size: 14px !important; font-weight: bold !important; text-transform: uppercase; padding: 12px 15px !important; }
    .stTabs [aria-selected="true"] { color: #C8102E !important; border-bottom: 3px solid #C8102E !important; }

    /* ── NEWS CARDS ── */
    .news-card {
        background: #ffffff; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 18px; margin-bottom: 15px; min-height: 160px; display: flex; flex-direction: column;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .news-card:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0,0,0,0.08); border-color: #004B87; }
    .news-tag { display: inline-block; font-size: 10px; font-weight: 800; color: #004B87; background: #EFF6FF; padding: 3px 8px; border-radius: 4px; margin-bottom: 10px; }
    .news-title { font-size: 15px; font-weight: 700; color: #0F172A; text-decoration: none; line-height: 1.4; margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
    .news-title:hover { color: #C8102E; }
    .news-summary { font-size: 13px; color: #475569; line-height: 1.5; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .news-meta { margin-top: auto; display: flex; align-items: center; justify-content: space-between; border-top: 1px dashed #E2E8F0; padding-top: 10px; }
    .news-date { font-size: 11px; color: #64748B; font-weight: 600; }
    .read-link { font-size: 12px; font-weight: bold; color: #C8102E; text-decoration: none; }
    .read-link:hover { text-decoration: underline; }

    /* ── KHOẢNG LẮNG NGHE DƯ LUẬN ── */
    .dashboard-box { background: white; border-radius: 8px; padding: 15px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.02); height: 100%; }
    .kpi-title { font-size: 12px; color: #64748B; font-weight: bold; text-transform: uppercase; margin-bottom: 5px;}
    .kpi-value { font-size: 28px; font-weight: 900; }
    .sentiment-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-bottom: 8px; border: 1px solid;}
    
    .poll-bar-bg { background: #E2E8F0; border-radius: 10px; height: 12px; width: 100%; margin-top: 5px; overflow: hidden; }
    .poll-bar-fg { height: 100%; border-radius: 10px; }

    /* ── SCROLL TO TOP ── */
    .scroll-top { position: fixed; bottom: 30px; right: 30px; background: #004B87; color: white !important; border-radius: 50%; width: 45px; height: 45px; display: flex; justify-content: center; align-items: center; font-size: 20px; text-decoration: none !important; box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 99; }
    .scroll-top:hover { background: #C8102E; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CẤU HÌNH NGUỒN TIN
# ==========================================
RSS_FEEDS = {
    "🔥 Tiêu điểm 24h": {"url": "https://news.google.com/news/rss/headlines/section/topic/NATION?hl=vi&gl=VN&ceid=VN%3Avi", "tag": "TRONG NƯỚC"},
    "🗣️ Dư luận XH": {"url": "https://news.google.com/rss/search?q=(%22d%C6%B0+lu%E1%BA%ADn%22+OR+%22b%E1%BB%A9c+x%C3%BAc%22+OR+%22ph%E1%BA%A3n+%C3%A1nh%22+OR+%22sai+ph%E1%BA%A1m%22)+%22Tuy%C3%AAn+Quang%22+when:30d&hl=vi&gl=VN&ceid=VN:vi", "tag": "DƯ LUẬN"},
    "📍 Tuyên Quang": {"url": "https://news.google.com/rss/search?q=%22Tuy%C3%AAn+Quang%22+when:1d&hl=vi&gl=VN&ceid=VN:vi", "tag": "ĐỊA PHƯƠNG"},
    "🤝 Dân vận khéo": {"url": "https://news.google.com/rss/search?q=%22d%C3%A2n+v%E1%BA%ADn+kh%C3%A9o%22+%22Tuy%C3%AAn+Quang%22+when:30d&hl=vi&gl=VN&ceid=VN:vi", "tag": "DÂN VẬN"},
    "🏛️ Tuyên giáo TW": {"url": "https://news.google.com/rss/search?q=(site:dangcongsan.vn+OR+site:tuyengiaodanvan.vn+OR+site:nhandan.vn)+(%22Ban+Tuy%C3%AAn+gi%C3%A1o%22+OR+%22D%C3%A2n+v%E1%BA%ADn%22)+when:1d&hl=vi&gl=VN&ceid=VN:vi", "tag": "TUYÊN GIÁO"},
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

def analyze_sentiment(title, summary):
    """Hàm AI giả lập phân tích cảm xúc của tin bài"""
    text = (title + " " + summary).lower()
    
    neg_words = ['bức xúc', 'sai phạm', 'kỷ luật', 'đình chỉ', 'chậm', 'kêu cứu', 'phản ánh', 'lừa đảo', 'chiếm đoạt', 'bắt giữ', 'khởi tố', 'vi phạm', 'bất bình', 'tai nạn', 'ngập', 'thiệt hại']
    pos_words = ['tuyên dương', 'thành công', 'phát triển', 'hiệu quả', 'khen thưởng', 'hoàn thành', 'vượt mức', 'nâng cao', 'tốt', 'biểu dương', 'hỗ trợ', 'khắc phục']
    
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
    priority = ["tổng bí thư", "chủ tịch nước", "thủ tướng", "quốc hội", "nghị quyết", "chỉ thị", "quyết định", "hội nghị", "điều tra", "khởi tố", "bắt giữ", "tham nhũng"]
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
    except Exception:
        return []

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
today_str = datetime.datetime.now().strftime("%d/%m/%Y")

# 1. Banner Header
st.markdown(f"""
<div class="masthead">
    <div class="masthead-eyebrow">BAN TUYÊN GIÁO VÀ DÂN VẬN TỈNH ỦY TUYÊN QUANG</div>
    <h1 class="masthead-title">ĐIỂM TIN & <span>LẮNG NGHE DƯ LUẬN</span></h1>
    <p class="masthead-subtitle">Hệ thống thu thập tin tức và phân tích mạng xã hội ứng dụng AI</p>
    <span class="live-badge"><span class="live-dot"></span>ĐANG CẬP NHẬT 24/7</span>
</div>
""", unsafe_allow_html=True)

# 2. Thanh lọc số lượng tin
with st.container():
    c1, c2, c3 = st.columns([1, 3, 1])
    with c2:
        so_luong_tin = st.slider("Số lượng tin/mục hiển thị:", min_value=3, max_value=30, value=9, step=3)
    with c3:
        st.write("")
        if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 3. Tabs Nội dung
tab_labels = list(RSS_FEEDS.keys())
tabs = st.tabs(tab_labels)

for i, (tab_name, cfg) in enumerate(RSS_FEEDS.items()):
    with tabs[i]:
        with st.spinner(f"Đang xử lý dữ liệu {tab_name}..."):
            entries = fetch_rss(cfg["url"])

        if not entries:
            st.info("📭 Chưa có dữ liệu mới trong chuyên mục này.")
            continue
            
        entries_to_show = entries[:so_luong_tin]
        tag = cfg["tag"]

        # =======================================================
        # NẾU LÀ TAB DƯ LUẬN XÃ HỘI -> HIỂN THỊ DASHBOARD LẮNG NGHE
        # =======================================================
        if tab_name == "🗣️ Dư luận XH":
            # Xử lý sentiment cho tất cả entry cào được để vẽ biểu đồ
            sentiments = []
            for e in entries:
                t = e.get("title", "")
                s = clean_html(e.get("summary", ""))
                _, _, _, label = analyze_sentiment(t, s)
                sentiments.append(label)
                
            df_sent = pd.DataFrame(sentiments, columns=["Cảm xúc"])
            sent_counts = df_sent["Cảm xúc"].value_counts().reset_index()
            
            # --- DASHBOARD UI ---
            st.markdown("<h4 style='color:#004B87; font-weight:800; text-transform:uppercase;'>🎯 Trạm Lắng Nghe & Phân Tích Dư Luận</h4>", unsafe_allow_html=True)
            
            d_col1, d_col2, d_col3 = st.columns([1, 1.5, 1.5])
            
            # Cột 1: KPI đếm số bài
            with d_col1:
                st.markdown(f"""
                <div class='dashboard-box'>
                    <div class='kpi-title'>Tổng lượt quét (30 ngày)</div>
                    <div class='kpi-value' style='color:#004B87;'>{len(entries)} bài</div>
                    <hr style='margin:10px 0;'>
                    <div class='kpi-title' style='color:#DC2626'>Cảnh báo Tiêu cực</div>
                    <div class='kpi-value' style='color:#DC2626;'>{sentiments.count('Tiêu cực')} vụ</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Cột 2: Biểu đồ AI phân tích cảm xúc
            with d_col2:
                st.markdown("<div class='dashboard-box'>", unsafe_allow_html=True)
                color_map = {"Tích cực": "#16A34A", "Trung lập": "#D97706", "Tiêu cực": "#DC2626"}
                fig = px.pie(sent_counts, values='count', names='Cảm xúc', hole=0.6, color='Cảm xúc', color_discrete_map=color_map)
                fig.update_traces(textposition='outside', textinfo='percent+label')
                fig.update_layout(title=dict(text="AI Phân tích Cảm xúc dư luận", font=dict(size=13, color='#475569')), 
                                  margin=dict(t=30, b=10, l=10, r=10), height=180, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Cột 3: Khảo sát Zalo (Demo)
            with d_col3:
                st.markdown("""
                <div class='dashboard-box'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div class='kpi-title' style='margin:0;'>📊 Khảo sát trực tuyến (Zalo)</div>
                        <span style='background:#EFF6FF; color:#004B87; font-size:10px; padding:2px 6px; border-radius:4px; font-weight:bold;'>Đang diễn ra</span>
                    </div>
                    <div style='font-size:13px; font-weight:bold; color:#0F172A; margin:8px 0;'>Đánh giá tiến độ Đền bù GPMB Cao tốc Tuyên Quang - Hà Giang</div>
                    
                    <div style='font-size:11px; color:#475569; display:flex; justify-content:space-between;'><span>Đồng thuận cao (75%)</span><span>1,204 vote</span></div>
                    <div class='poll-bar-bg'><div class='poll-bar-fg' style='width: 75%; background: #16A34A;'></div></div>
                    
                    <div style='font-size:11px; color:#475569; display:flex; justify-content:space-between; margin-top:8px;'><span>Còn vướng mắc (25%)</span><span>401 vote</span></div>
                    <div class='poll-bar-bg'><div class='poll-bar-fg' style='width: 25%; background: #D97706;'></div></div>
                    
                    <button style='width:100%; background:#004B87; color:white; border:none; padding:6px; border-radius:4px; margin-top:12px; font-size:12px; font-weight:bold; cursor:pointer;'>+ Tạo chiến dịch Khảo sát mới</button>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<hr style='margin:25px 0 15px;'>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#004B87; font-weight:bold;'>Danh sách {len(entries_to_show)} bài viết thu thập mới nhất:</p>", unsafe_allow_html=True)

        else:
            # Nếu là các Tab bình thường
            st.markdown(f"<p style='color:#004B87; font-weight:bold; margin-top:10px;'>Đang hiển thị {len(entries_to_show)} tin bài nổi bật nhất:</p>", unsafe_allow_html=True)

        # =======================================================
        # RENDER DANH SÁCH TIN (CÓ GẮN NHÃN CẢM XÚC NẾU LÀ TAB DƯ LUẬN)
        # =======================================================
        cols = st.columns(3)
        for idx, entry in enumerate(entries_to_show):
            title = entry.get("title", "Không có tiêu đề")
            link = entry.get("link", "#")
            pub_date = format_date(entry.get("published", ""))
            summary = clean_html(entry.get("summary", ""))
            
            # Gắn nhãn AI nếu đang ở Tab Dư luận
            badge_html = ""
            if tab_name == "🗣️ Dư luận XH":
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

# Footer & Nút cuộn lên
st.markdown("""
<hr>
<div style='text-align:center; color:#64748B; font-size:12px; margin-bottom:20px;'>
    Hệ thống Điểm tin & Lắng nghe Dư luận · Ban Tuyên giáo & Dân vận Tỉnh ủy Tuyên Quang
</div>
<a href="#top-of-page" class="scroll-top" title="Lên đầu trang">⬆</a>
""", unsafe_allow_html=True)
