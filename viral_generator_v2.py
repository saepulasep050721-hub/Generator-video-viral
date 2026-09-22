import streamlit as st
import google.generativeai as genai
import json
import re

# 1. Konfigurasi Halaman Dasar
st.set_page_config(page_title="YouTube Viral Scanner AI", page_icon="🚀", layout="wide")

if "clips_data" not in st.session_state:
    st.session_state.clips_data = []

# 2. INJEKSI CSS TAMPILAN MODERN
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    div.stButton > button { background-color: #f43f5e; color: white; border-radius: 8px; font-weight: 600; border: none; padding: 15px; }
    div.stButton > button:hover { background-color: #e11d48; color: white; }
    .clip-card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .score-badge { background-color: #fff7ed; color: #ea580c; padding: 5px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #fed7aa; }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 🚀 YouTube Viral Scanner AI")
st.caption("Cukup tempel Link YouTube, AI akan mencari minimal 10 momen viral (tanpa perlu download/upload video!)")
st.divider()

# Sidebar untuk API Key
api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

def get_yt_id(url):
    import re
    match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    return match.group(1) if match else None

def time_to_seconds(time_str):
    parts = str(time_str).strip().split(':')
    try:
        if len(parts) == 3: return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2: return int(parts[0]) * 60 + int(parts[1])
        return int(time_str)
    except:
        return 0

# 3. PANEL INPUT URL & PENGATURAN AI
with st.container():
    youtube_url = st.text_input("🔗 Tempel Link YouTube (Video Panjang / Podcast):", placeholder="https://www.youtube.com/watch?v=...")
    
    col1, col2 = st.columns(2)
    with col1:
        fokus_momen = st.selectbox("🎯 Kategori Momen yang Ingin Dicari", [
            "✨ Golden Moment (Inspiratif/Puncak Emosi)", 
            "😂 Momen Lucu / Ngakak", 
            "🔥 Debat Panas / Kontroversi", 
            "💡 Fakta Unik / Mindblowing",
            "🎲 Campur Semua Momen Viral"
        ])
    with col2:
        jumlah_klip = st.number_input("Target Jumlah Klip (Minimal 10)", min_value=10, max_value=30, value=11)

    if st.button("🔍 Scan Momen Viral Sekarang!", use_container_width=True):
        if not api_key:
            st.error("Silakan masukkan API Key Gemini di menu samping kiri.")
        elif not youtube_url or not get_yt_id(youtube_url):
            st.warning("Silakan masukkan link YouTube yang valid.")
        else:
            with st.spinner(f"AI sedang menscan isi video untuk mencari {jumlah_klip} momen '{fokus_momen}'..."):
                try:
                    # KUNCI PERBAIKAN: Langsung kunci model ke versi 3.6-flash yang direkomendasikan server
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    
                    prompt = f"""
                    Analisis konten dari URL video YouTube ini: {youtube_url}
                    Tugas Anda adalah mencari {jumlah_klip} momen spesifik yang masuk ke dalam kategori: '{fokus_momen}'.
                    Untuk setiap momen, tentukan waktu mulai dan selesainya (durasi ideal 30-60 detik per klip).
                    Berikan skor potensi viral dari 1 hingga 10.
                    
                    Format Output WAJIB menggunakan JSON Array murni tanpa penjelasan teks lainnya.
                    Contoh format:
                    [
                        {{
                            "id_klip": 1,
                            "waktu_mulai": "00:05:10",
                            "waktu_selesai": "00:06:00",
                            "judul": "Judul momen yang clickbait dan menarik",
                            "skor": "9.5/10",
                            "alasan": "Penjelasan detail kenapa momen ini lucu/menarik/viral."
                        }}
                    ]
                    """
                    
                    response = model.generate_content(prompt)
                    text_res = response.text
                    
                    start_idx = text_res.find('[')
                    end_idx = text_res.rfind(']') + 1
                    
                    if start_idx != -1 and end_idx != 0:
                        clean_json = text_res[start_idx:end_idx]
                        st.session_state.clips_data = json.loads(clean_json)
                        st.session_state.yt_id = get_yt_id(youtube_url)
                        st.success("Berhasil menemukan momen viral menggunakan model gemini-3.6-flash!")
                    else:
                        st.error("Gagal membaca hasil analisis AI. Silakan klik tombol Scan lagi.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses URL: {e}")

# 4. HASIL SCAN: MENAMPILKAN KLIP & PEMUTAR VIDEO (EMBED)
if st.session_state.clips_data and "yt_id" in st.session_state:
    st.markdown("<br>#### 📋 Hasil Analisis Klip Viral", unsafe_allow_html=True)
    st.info("Anda bisa langsung memutar setiap klip di bawah ini. AI telah mengatur agar video hanya memutar pada detik momen tersebut.")

    for clip in st.session_state.clips_data:
        start_sec = time_to_seconds(clip.get('waktu_mulai', '0'))
        end_sec = time_to_seconds(clip.get('waktu_selesai', '0'))
        
        with st.container():
            st.markdown(f"""
                <div class="clip-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <h4 style="margin: 0; color: #1e293b;">#{clip.get('id_klip', '')} - {clip.get('judul', 'Klip Viral')}</h4>
                        <span class="score-badge">🔥 Skor: {clip.get('skor', 'N/A')}</span>
                    </div>
                    <p style="color: #64748b; margin-bottom: 15px;">
                        ⏱️ <b>Waktu:</b> {clip.get('waktu_mulai', '')} sampai {clip.get('waktu_selesai', '')} <br>
                        💡 <b>Alasan AI:</b> {clip.get('alasan', '')}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Memunculkan pemutar YouTube Embed yang hanya memutar bagian klip tersebut
            embed_url = f"https://www.youtube.com/embed/{st.session_state.yt_id}?start={start_sec}&end={end_sec}"
            st.components.v1.iframe(embed_url, width=640, height=360)
            
            st.divider()
