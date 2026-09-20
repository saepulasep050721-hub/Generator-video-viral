import streamlit as st
import google.generativeai as genai
import json
import subprocess
import yt_dlp
import os
import re

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

# 3. FUNGSI PEMOTONG VIDEO DENGAN PARSER WAKTU SUPER AMAN
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

    def parse_to_seconds(time_str):
        if not time_str:
            return 0.0
        # Bersihkan string dari karakter non-standar
        clean_str = str(time_str).strip()
        parts = clean_str.split(':')
        try:
            if len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            else:
                return float(clean_str)
        except:
            # Fallback ekstraksi angka jika format berantakan
            numbers = re.findall(r'\d+', clean_str)
            if len(numbers) >= 3:
                return float(numbers[0]) * 3600 + float(numbers[1]) * 60 + float(numbers[2])
            elif len(numbers) == 2:
                return float(numbers[0]) * 60 + float(numbers[1])
            elif len(numbers) == 1:
                return float(numbers[0])
            return 0.0

    start_sec = parse_to_seconds(start_time)
    end_sec = parse_to_seconds(end_time)
    duration = end_sec - start_sec

    if duration <= 0:
        duration = 30.0 # Default durasi aman

    crop_filter = f"crop=ih*9/16:ih:(iw-ih*9/16)*{pan_percent}/100:0"
    
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
                    Format output HARUS JSON Array murni.
                    [
                        {{
                            "id_klip": 1,
                            "waktu_mulai": "00:00:45",
                            "waktu_selesai": "00:01:45",
                            "judul_klip": "Pengakuan Mengejutkan",
                            "skor_viral": "9.8/10",
                            "voice_to_text": "Transkrip teks suara..."
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
                        st.success("Analisis selesai! Silakan gulir ke bawah untuk memproses dan mengunduh MP4.")
                    else:
                        st.error("Gagal membaca format JSON dari AI. Silakan coba klik tombol sekali lagi.")
                except Exception as e:
                    st.error(f"Error AI: {e}")

# 5. STUDIO RENDER & DOWNLOAD SUNGGUHAN
if st.session_state.clips_data:
    st.markdown("<br>#### 🎬 STEP 2: Studio Render & Download", unsafe_allow_html=True)

    for idx, clip in enumerate(st.session_state.clips_data):
        with st.container():
            st.markdown(f"<div class='clip-card'><b>Klip #{clip['id_klip']} ({clip['waktu_mulai']} - {clip['waktu_selesai']}) | 🔥 Skor: {clip['skor_viral']}</b><br>{clip['judul_klip']}</div>", unsafe_allow_html=True)
            
            c_prev, c_edit = st.columns([1, 1.2])
            
            with c_prev:
                st.markdown("**📱 Pratinjau 9:16 (Bebas Teks)**")
                st.markdown(f"""
                    <div class="phone-mockup">
                        <div style="position: absolute; top: 15px; font-size: 11px; background: rgba(0,0,0,0.6); padding: 3px 8px; border-radius: 10px;">
                            9:16 Vertical View
                        </div>
                        <div style="font-size: 12px; color: #94a3b8; text-align: center; margin-top: auto; margin-bottom: auto;">
                            Video akan bersih<br>tanpa teks apa pun
                        </div>
                        <div style="position: absolute; bottom: 15px; font-size: 10px; color: #94a3b8;">
                            Durasi: {clip['waktu_mulai']} - {clip['waktu_selesai']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with c_edit:
                pan_position = st.slider(f"↔️ Geser Posisi Bingkai 9:16 (0=Kiri, 50=Tengah, 100=Kanan) [Klip {clip['id_klip']}]", 0, 100, 50, key=f"pan_{idx}")
                st.text_area("🎙️ Voice-to-Text (Transkrip Kasar):", clip.get('voice_to_text', ''), height=100, key=f"txt_{idx}")
                
                output_file = f"hasil_klip_{clip['id_klip']}.mp4"
                
                if os.path.exists(output_file):
                    with open(output_file, "rb") as f:
                        st.download_button(
                            label=f"📥 Download MP4 Bersih (Klip #{clip['id_klip']})",
                            data=f,
                            file_name=output_file,
                            mime="video/mp4",
                            key=f"dl_btn_{idx}",
                            type="primary"
                        )
                else:
                    if st.button(f"⚙️ Mulai Proses Potong MP4 (Klip #{clip['id_klip']})", key=f"render_{idx}", use_container_width=True):
                        with st.spinner(f"Mesin sedang menarik video dan merender format 9:16... Mohon tunggu sebentar."):
                            render_video_clip(youtube_url, clip['waktu_mulai'], clip['waktu_selesai'], pan_position, output_file)
                            if os.path.exists(output_file):
                                st.success("Berhasil! Halaman akan dimuat ulang untuk menampilkan tombol Download.")
                                st.rerun()
                            else:
                                st.error("Gagal memotong video. Periksa kembali jaringan atau link YouTube.")
            st.divider()
