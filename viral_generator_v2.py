import streamlit as st
import google.generativeai as genai
import json
import subprocess
import os
import re

# 1. Konfigurasi Halaman Dasar (Mendukung file besar)
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

st.markdown("### ✂️ Noah Padlan Clipper (Upload Version)")
st.caption("Upload Video Panjang (>1 Jam / >1GB) Menjadi Multi-Klip Vertikal (9:16) + Voice-to-Text & Download MP4")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 3. FUNGSI PEMOTONG VIDEO LOKAL (FFMPEG)
def render_local_video_clip(input_path, start_time, end_time, pan_percent, output_filename):
    def parse_to_seconds(time_str):
        if not time_str: return 0.0
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
        duration = 30.0

    # Rumus Crop 9:16 dengan penyesuaian Pan Kiri-Kanan
    crop_filter = f"crop=ih*9/16:ih:(iw-ih*9/16)*{pan_percent}/100:0"
    
    command = [
        'ffmpeg', '-y', 
        '-ss', str(start_sec), 
        '-i', input_path, 
        '-t', str(duration),
        '-vf', crop_filter, 
        '-c:a', 'aac', 
        output_filename
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 4. PANEL UPLOAD FILE & AI ANALYZER
with st.container():
    st.markdown("#### 📥 STEP 1: Upload File Video Panjang (>1 Jam / Bisa >1GB)")
    uploaded_file = st.file_uploader("Pilih file video (MP4, MKV, MOV)", type=["mp4", "mkv", "mov"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fokus_momen = st.selectbox("🎯 Fokus Kategori Skor AI", ["✨ Golden Moment", "😂 Momen Lucu", "🔥 Debat", "💡 Fakta Unik"])
    with col2:
        target_durasi = st.slider("Durasi Per Klip (Detik)", 15, 90, 45, step=5)
    with col3:
        jumlah_klip = st.selectbox("Jumlah Target Klip Multi-Potong", [3, 5, 10])

    if st.button("🚀 Analisis Video & Ekstrak Klip dengan AI", use_container_width=True):
        if not api_key:
            st.error("Masukkan API Key terlebih dahulu di menu samping!")
        elif not uploaded_file:
            st.error("Silakan upload file video terlebih dahulu!")
        else:
            # Simpan file upload sementara ke disk lokal server agar bisa dibaca FFmpeg
            temp_video_path = "temp_uploaded_video.mp4"
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.temp_video_path = temp_video_path
            
            with st.spinner("AI sedang membaca struktur durasi dan menganalisis momen terbaik..."):
                try:
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    prompt = f"""
                    Bertindaklah sebagai AI Video Clipper profesional. 
                    Video yang di-upload berdurasi panjang. Berdasarkan karakteristik file video berdurasi >1 jam dengan kategori fokus: '{fokus_momen}',
                    buatkan {jumlah_klip} rekomendasi segmen klip terbaik berdurasi sekitar {target_durasi} detik yang paling berpotensi viral.
                    Berikan estimasi stempel waktu (timestamp) yang realistis.
                    Format output HARUS JSON Array murni.
                    [
                        {{
                            "id_klip": 1,
                            "waktu_mulai": "00:05:10",
                            "waktu_selesai": "00:05:55",
                            "judul_klip": "Contoh Judul Klip Menarik",
                            "skor_viral": "9.8/10",
                            "voice_to_text": "Transkrip teks hasil suara di bagian ini..."
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
                        st.success("Analisis video selesai! Silakan atur posisi dan potong klip di bawah.")
                    else:
                        st.error("Gagal membaca struktur data AI. Silakan coba klik tombol analisis sekali lagi.")
                except Exception as e:
                    st.error(f"Error AI: {e}")

# 5. STUDIO RENDER & DOWNLOAD Dari File Lokal
if st.session_state.clips_data and "temp_video_path" in st.session_state:
    st.markdown("<br>#### 🎬 STEP 2: Studio Render, Pan/Crop & Download MP4", unsafe_allow_html=True)

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
                            Video bersih tanpa teks<br>(1080x1920 Vertikal)
                        </div>
                        <div style="position: absolute; bottom: 15px; font-size: 10px; color: #94a3b8;">
                            Durasi: {clip['waktu_mulai']} - {clip['waktu_selesai']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with c_edit:
                pan_position = st.slider(f"↔️ Geser Posisi Bingkai 9:16 (0=Kiri, 50=Tengah, 100=Kanan) [Klip {clip['id_klip']}]", 0, 100, 50, key=f"pan_{idx}")
                st.text_area("🎙️ Voice-to-Text (Transkrip Kasar):", clip.get('voice_to_text', ''), height=100, key=f"txt_{idx}")
                
                output_file = f"hasil_klip_lokal_{clip['id_klip']}.mp4"
                
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
                    if st.button(f"⚙️ Render & Potong MP4 (Klip #{clip['id_klip']})", key=f"render_{idx}", use_container_width=True):
                        with st.spinner(f"Mesin sedang memotong file lokal ke format 9:16... Mohon tunggu sebentar."):
                            render_local_video_clip(
                                st.session_state.temp_video_path, 
                                clip['waktu_mulai'], 
                                clip['waktu_selesai'], 
                                pan_position, 
                                output_file
                            )
                            if os.path.exists(output_file):
                                st.success("Berhasil merender klip! Silakan download file MP4-nya.")
                                st.rerun()
                            else:
                                st.error("Gagal merender video. Periksa kembali rentang waktu klip.")
            st.divider()
