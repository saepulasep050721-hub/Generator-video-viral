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
    </style>
""", unsafe_allow_html=True)

st.markdown("### ✂️ Noah Padlan Clipper")
st.caption("Ubah Link Video YouTube (>1 Jam) Menjadi Multi-Klip Vertikal (9:16) + Download MP4 Asli")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 3. FUNGSI PEMOTONG VIDEO (FFMPEG + YT-DLP)
def render_video_clip(url, start_time, end_time, pan_percent, output_filename):
    # Dapatkan URL streaming langsung tanpa mengunduh video full
    ydl_opts = {'format': 'best', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info['url']

    # Rumus Crop 9:16 dan posisi Pan (Kiri-Kanan)
    # ih*9/16 adalah lebar baru. Posisi X digeser berdasarkan persentase pan_percent
    crop_filter = f"crop=ih*9/16:ih:(iw-ih*9/16)*{pan_percent}/100:0"
    
    # Perintah FFmpeg
    command = [
        'ffmpeg', '-y', 
        '-ss', start_time, 
        '-to', end_time, 
        '-i', stream_url, 
        '-vf', crop_filter, 
        '-c:a', 'copy', 
        output_filename
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 4. PANEL INPUT & AI ANALYZER
with st.container():
    youtube_url = st.text_input("🔗 Tempel Link YouTube Video Panjang (> 1 Jam):")
    
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
                    Analisis video: {youtube_url}. Fokus: {fokus_momen}. 
                    Buat {jumlah_klip} klip durasi {target_durasi} detik.
                    Format JSON murni.
                    [
                        {{
                            "id_klip": 1,
                            "waktu_mulai": "00:01:10",
                            "waktu_selesai": "00:01:40",
                            "judul_klip": "Momen Epik",
                            "skor_viral": "9.5/10",
                            "voice_to_text": "Teks otomatis dari suara..."
                        }}
                    ]
                    """
                    response = model.generate_content(prompt)
                    text_res = response.text.strip()
                    if text_res.startswith("```json"): text_res = text_res[7:]
                    if text_res.endswith("```"): text_res = text_res[:-3]
                    
                    st.session_state.clips_data = json.loads(text_res.strip())
                    st.success("Analisis selesai! Gulir ke bawah untuk memotong MP4.")
                except Exception as e:
                    st.error(f"Error AI: {e}")

# 5. STUDIO RENDER & DOWNLOAD SUNGGUHAN
if st.session_state.clips_data:
    st.markdown("<br>#### 🎬 STEP 2: Studio Render & Download", unsafe_allow_html=True)

    for idx, clip in enumerate(st.session_state.clips_data):
        with st.container():
            st.markdown(f"<div class='clip-card'><b>Klip #{clip['id_klip']} ({clip['waktu_mulai']} - {clip['waktu_selesai']}) | 🔥 Skor: {clip['skor_viral']}</b><br>{clip['judul_klip']}</div>", unsafe_allow_html=True)
            
            pan_position = st.slider(f"↔️ Geser Posisi Bingkai 9:16 (0=Kiri, 50=Tengah, 100=Kanan) [Klip {clip['id_klip']}]", 0, 100, 50, key=f"pan_{idx}")
            st.text_area("🎙️ Voice-to-Text:", clip.get('voice_to_text', ''), height=80, key=f"txt_{idx}")
            
            output_file = f"hasil_klip_{clip['id_klip']}.mp4"
            
            # Cek apakah file sudah di-render
            if os.path.exists(output_file):
                with open(output_file, "rb") as f:
                    st.download_button(
                        label=f"📥 Download MP4 (Klip #{clip['id_klip']})",
                        data=f,
                        file_name=output_file,
                        mime="video/mp4",
                        key=f"dl_btn_{idx}",
                        type="primary"
                    )
            else:
                if st.button(f"⚙️ Mulai Proses Potong MP4 (Klip #{clip['id_klip']})", key=f"render_{idx}"):
                    with st.spinner(f"Mesin sedang menarik video dan memotong 9:16... (Bisa memakan waktu 1-3 menit)"):
                        render_video_clip(youtube_url, clip['waktu_mulai'], clip['waktu_selesai'], pan_position, output_file)
                        if os.path.exists(output_file):
                            st.success("Berhasil! Halaman akan dimuat ulang untuk menampilkan tombol Download.")
                            st.rerun()
                        else:
                            st.error("Gagal memotong video. Server mungkin kehabisan memori.")
            st.divider()
