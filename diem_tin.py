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
# CẤU HÌNH NGUỒN TIN (BẢN VIP)
# ==========================================
RSS_FEEDS = {
    "🔥 TIÊU ĐIỂM TRONG NƯỚC (Tin nóng 24h)": "https://news.google.com/news/rss/headlines/section/topic/NATION?hl=vi&gl=VN&ceid=VN%3Avi",
    
    # ĐÃ SỬA LẠI THÀNH KÊNH QUỐC TẾ CHUẨN 100%
    "🌍 QUỐC TẾ NỔI BẬT (Báo Đảng & TTXVN)": "https://news.google.com/news/rss/headlines/section/topic/WORLD?hl=vi&gl=VN&ceid=VN%3Avi",
    
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
# LÕI TĂNG TỐC BẰNG BỘ NHỚ ĐỆM (CACHE 15 PHÚT)
# ==========================================
@st.cache_data(ttl=900, show_spinner=False)
def fetch_all_feeds_to_cache():
    kho_du_lieu = {}
    tu_khoa_rac = ["untitled", "vnaid", "lịch tạm ngừng", "cắt điện", "xổ số", "giá vàng", "thời tiết", "tỷ giá", "tư liệu văn kiện", "tulieuvankien"]
    cac_nam_cu = ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
    
    for ten_nguon, url_rss in RSS_FEEDS.items():
        try:
            req = urllib.request.Request(url_rss, headers={'User-Agent': 'Mozilla/5.0'})
            # Thêm timeout 5s để phòng trường hợp báo bị sập thì bỏ qua luôn, không làm treo app
            with urllib.request.urlopen(req, timeout=5) as response:
                feed = feedparser.parse(response.read())
            
            ds_bai_viet = []
            for entry in feed.entries:
                tieu_de = entry.title.strip()
                tieu_de_lower = tieu_de.lower()
                ngay_dang_goc = entry.get('published', '')
                
                if len(tieu_de) < 10 or any(rac in tieu_de_lower for rac in tu_khoa_rac): continue 
                if any(nam in ngay_dang_goc for nam in cac_nam_cu): continue
                
                tom_tat = clean_html(entry.get('summary', '')).strip()
                
                ds_bai_viet.append({
                    "title": tieu_de,
                    "link": entry.link,
                    "published": ngay_dang_goc.replace("GMT", "").strip(),
                    "summary": tom_tat
                })
            kho_du_lieu[ten_nguon] = ds_bai_viet
        except Exception as e:
            kho_du_lieu[ten_nguon] = []
            
    return kho_du_lieu

# ==========================================
# CỘT SIDEBAR - ĐIỀU KHIỂN
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ BỘ LỌC TIN TỨC")
    nguon_tin = st.selectbox("📌 Chọn nguồn tin:", ["Tất cả"] + list(RSS_FEEDS.keys()))
    tu_khoa = st.text_input("🔍 Tìm từ khóa (VD: đại hội, chỉ đạo...):", "")
    so_luong = st.slider("📑 Số lượng tin mỗi khối:", 5, 30, 3)
    
    st.markdown("---")
    st.info("⚡ **Trạng thái:** Hệ thống đã được tối ưu tốc độ bằng Bộ nhớ đệm. Tự động làm mới tin sau mỗi 15 phút.")

# ==========================================
# XỬ LÝ VÀ HIỂN THỊ TIN TỨC (RÚT TỪ KHO RA)
# ==========================================
tong_so_tin = 0

# Tải dữ liệu từ kho (Lần đầu mất 5s, các lần sau mất 0.01s)
with st.spinner("Đang quét dữ liệu báo chí (Cập nhật 15 phút/lần)..."):
    kho_du_lieu_cache = fetch_all_feeds_to_cache()

danh_sach_hien_thi = list(RSS_FEEDS.keys()) if nguon_tin == "Tất cả" else [nguon_tin]

for ten_nguon in danh_sach_hien_thi:
    tin_goc = kho_du_lieu_cache.get(ten_nguon, [])
    tin_da_loc = []
    
    # Lọc nhanh trong bộ nhớ
    for bai in tin_goc:
        if tu_khoa and tu_khoa.lower() not in bai['title'].lower() and tu_khoa.lower() not in bai['summary'].lower():
            continue 
        tin_da_loc.append(bai)
        if len(tin_da_loc) >= so_luong: break
            
    # --- HIỂN THỊ DẠNG LƯỚI ---
    if tin_da_loc:
        st.markdown(f"<h3 style='color:#004B87; margin-top: 20px; margin-bottom: 10px; border-bottom: 2px solid #e0e6ed; padding-bottom: 5px;'>📰 {ten_nguon}</h3>", unsafe_allow_html=True)
        
        html_grid = '<div class="news-grid">'
        for bai in tin_da_loc:
            tong_so_tin += 1
            t_title = bai['title'].replace('"', '&quot;')
            t_sum = bai['summary'].replace('"', '&quot;')
            
            html_grid += f"<div class='news-card'><div class='news-title'><a href='{bai['link']}' target='_blank'>{t_title}</a></div><div class='news-date'>🕒 Xuất bản: {bai['published']}</div><div class='news-summary'>{t_sum}</div></div>"
            
        html_grid += '</div>'
        st.markdown(html_grid, unsafe_allow_html=True)
        
if tong_so_tin == 0:
    st.warning("Không tìm thấy tin tức nào phù hợp với bộ lọc hiện tại.")
else:
    st.success(f"✅ Đã tải siêu tốc {tong_so_tin} tin bài nổi bật!")
