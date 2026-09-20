import streamlit as st
import google.generativeai as genai
import json
import subprocess
import yt_dlp
import os

# 1. Konfigurasi Halaman Dasar
st.set_page_config(page_title="Noah Padlan Clipper", page_icon="✂️", layout="wide")

if "clips_data" not in st.session_state:
    st.session_state.clips_data = []

# 2. INJEKSI CSS TAMPILAN MODERN
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    div.stButton > button { background-color: #8b5cf6; color: white; border-radius: 8px; font-weight: 600; border: none; }
    div.stButton > button:hover { background-color: #7c3aed; color: white; }
    .clip-card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
    .phone-mockup {
        background: #0f172a;
        border: 8px solid #334155;
        border-radius: 24px;
        padding: 10px;
        width: 100%;
        max-width: 280px;
        height: 480px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
        position: relative;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("### ✂️ Noah Padlan Clipper")
st.caption("Ubah Link Video YouTube (>1 Jam) Menjadi Multi-Klip Vertikal (9:16) + Download MP4 Asli")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 3. FUNGSI PEMOTONG VIDEO DENGAN PENANGANAN WAKTU AMAN
def render_video_clip(url, start_time, end_time, pan_percent, output_filename):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'url' in info:
            stream_url = info['url']
        else:
            formats = info.get('formats', [info])
            stream_url = formats[-1]['url']

    # Konversi format waktu HH:MM:SS ke total detik agar aman dibaca FFmpeg
    def time_to_seconds(t_str):
        parts = t_str.strip().split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        return float(t_str)

    try:
        start_sec = time_to_seconds(start_time)
        end_sec = time_to_seconds(end_time)
        duration = end_sec - start_sec
        if duration <= 0:
            duration = 30 # Default aman jika durasi tidak valid
    except:
        start_sec = 10
        duration = 30

    crop_filter = f"crop=ih*9/16:ih:(iw-ih*9/16)*{pan_percent}/100:0"
    
    # Menggunakan -ss dengan durasi (-t) agar lebih stabil di server cloud
    command = [
        'ffmpeg', '-y', 
        '-ss', str(start_sec), 
        '-i', stream_url, 
        '-t', str(duration),
        '-vf', crop_filter, 
        '-c:a', 'aac', 
        output_filename
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 4. PANEL INPUT & AI ANALYZER
with st.container():
    youtube_url = st.text_input("🔗 Tempel Link YouTube Video Panjang (> 1 Jam):", value="https://youtu.be/gkbLm5KV5ZM")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fokus_momen = st.selectbox("🎯 Fokus Kategori Skor AI", ["✨ Golden Moment", "😂 Momen Lucu", "🔥 Debat", "💡 Fakta Unik"])
    with col2:
        target_durasi = st.slider("Durasi Per Klip (Detik)", 15, 90, 45, step=5)
    with col3:
        jumlah_klip = st.selectbox("Jumlah Target Klip Multi-Potong", [3, 5, 10])

    if st.button("🚀 Analisis & Siapkan Potongan", use_container_width=True):
        if not api_key or not youtube_url:
            st.error("Masukkan API Key dan Link YouTube terlebih dahulu!")
        else:
            with st.spinner("AI sedang memindai video..."):
                try:
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    prompt = f"""
                    Analisis video YouTube: {youtube_url}. Fokus kategori: {fokus_momen}. 
                    Buat {jumlah_klip} klip durasi sekitar {target_durasi} detik yang paling berpotensi viral.
                    Format output HARUS JSON Array murni tanpa backticks.
                    [
                        {{
                            "id_klip": 1,
                            "waktu_mulai": "00:01:15",
                            "waktu_selesai": "00:02:00",
                            "judul_klip": "Reaksi Kaget",
                            "skor_viral": "9.8/10",
                            "voice_to_text": "Transkrip teks suara..."
                        }}
                    ]
                    """
                    response = model.generate_content(prompt)
                    text_res = response.text.strip()
                    if text_res.startswith("```json"): text_res = text_res[7:]
                    if text_res.endswith("
