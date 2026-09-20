import streamlit as st
import google.generativeai as genai
import subprocess
import os
import time

# 1. Konfigurasi Halaman Dasar
st.set_page_config(page_title="Noah Padlan Subtitle Burner", page_icon="✍️", layout="wide")

if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = ""
if "video_processed" not in st.session_state:
    st.session_state.video_processed = False

# 2. INJEKSI CSS TAMPILAN MODERN & PREVIEW KUSTOM
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    div.stButton > button { background-color: #2563eb; color: white; border-radius: 8px; font-weight: 600; border: none; }
    div.stButton > button:hover { background-color: #1d4ed8; color: white; }
    .card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown("### ✍️ Noah Padlan Subtitle Burner Pro (Real Audio AI + Live Preview)")
st.caption("Mendengarkan Suara Asli Video & Pratinjau Tampilan Subtitle Secara Langsung")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 3. FUNGSI PEMBAKARAN SUBTITLE FFMPEG
def burn_subtitles_to_video(input_path, transcript_content, output_path, font_name, font_size, color_code, alignment_val):
    srt_path = "temp_subs.srt"
    
    sentences = [s.strip() for s in transcript_content.split('.') if s.strip()]
    
    with open(srt_path, "w", encoding="utf-8") as f:
        start_sec = 0
        duration_per_sentence = 4.0 
        for i, sentence in enumerate(sentences):
            end_sec = start_sec + duration_per_sentence
            
            def format_time(sec):
                hrs = int(sec // 3600)
                mins = int((sec % 3600) // 60)
                secs = int(sec % 60)
                millis = int((sec - int(sec)) * 1000)
                return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"
            
            f.write(f"{i+1}\n")
            f.write(f"{format_time(start_sec)} --> {format_time(end_sec)}\n")
            f.write(f"{sentence}.\n\n")
            start_sec = end_sec

    force_style = (
        f"FontName={font_name},"
        f"FontSize={font_size},"
        f"PrimaryColour={color_code},"
        f"OutlineColour=&H000000&,"
        f"BorderStyle=1,"
        f"Outline=2,"
        f"Alignment={alignment_val}"
    )
    
    vf_arg = f"subtitles={srt_path}:force_style='{force_style}'"
    
    command = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-vf', vf_arg,
        '-c:a', 'copy',
        output_path
    ]
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if os.path.exists(srt_path):
        os.remove(srt_path)
    return result.returncode == 0

# 4. PANEL UPLOAD & BACA SUARA ASLI DENGAN GEMINI FILE API
with st.container():
    st.markdown("#### 📥 STEP 1: Upload Video & Analisis Suara Asli")
    uploaded_file = st.file_uploader("Upload File Video (MP4, MKV, MOV)", type=["mp4", "mkv", "mov"])
    
    language_style = st.selectbox("Gaya Bahasa Transkrip", [
        "Bahasa Indonesia (Casual / Santai / Gaul)", 
        "Bahasa Indonesia (Formal / Profesional)", 
        "English (Standard)"
    ])

    if st.button("🎙️ Proses Baca Suara Asli Video dengan AI", use_container_width=True):
        if not api_key:
            st.error("Masukkan API Key terlebih dahulu di menu samping!")
        elif not uploaded_file:
            st.error("Silakan upload file video terlebih dahulu!")
        else:
            temp_video_path = "source_video_input.mp4"
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.temp_video_path = temp_video_path

            with st.spinner("Mengunggah video ke peladen AI & mendengarkan suara asli... Mohon tunggu"):
                try:
                    video_file = genai.upload_file(path=temp_video_path)
                    
                    while video_file.state.name == "PROCESSING":
                        time.sleep(2)
                        video_file = genai.get_file(video_file.name)
                        
                    if video_file.state.name == "FAILED":
                        raise ValueError("Gagal memproses file video di server AI.")

                    model = genai.GenerativeModel('gemini-3.6-flash')
                    prompt = f"""
                    Dengarkan audio/suara dari video yang di-upload ini dengan seksama. 
                    Buat transkrip teks percakapan/suara asli secara akurat kalimat demi kalimat sesuai dengan isi video tersebut, dengan gaya bahasa: '{language_style}'.
                    Output HARUS berupa teks transkrip murni tanpa prolog atau markdown tambahan.
                    """
                    
                    response = model.generate_content([video_file, prompt])
                    st.session_state.transcript_text = response.text.strip()
                    
                    genai.delete_file(video_file.name)
                    st.success("Suara asli video berhasil dibaca dan ditranskrip oleh AI!")
                except Exception as e:
                    st.error(f"Gagal membaca suara video. Error: {e}")

# 5. STUDIO EDITOR TEKS, KUSTOMISASI & LIVE PREVIEW
if st.session_state.transcript_text and "temp_video_path" in st.session_state:
    st.markdown("<br>#### 🎬 STEP 2: Kustomisasi Gaya Teks & Live Preview", unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        font_choice = st.selectbox("🔤 Gaya Teks (Font)", ["Arial", "Impact", "Verdana", "Courier New"])
    with col_c2:
        size_choice = st.slider("📏 Ukuran Teks (Skala)", min_value=12, max_value=36, value=20, step=2)
    with col_c3:
        color_choice = st.selectbox("🎨 Warna Teks", [
            "Kuning (Khas Reels/TikTok)", 
            "Putih Bersih", 
            "Hijau Terang", 
            "Merah Menyala"
        ])
    with col_c4:
        pos_choice = st.selectbox("📍 Posisi Teks", [
            "Bawah (Default)", 
            "Tengah Layar", 
            "Atas Layar"
        ])

    # Mapping warna untuk FFmpeg (ASS format) & CSS Preview
    color_map_ffmpeg = {
        "Kuning (Khas Reels/TikTok)": "&H00FFFF&",
        "Putih Bersih": "&HFFFFFF&",
        "Hijau Terang": "&H00FF00&",
        "Merah Menyala": "&H0000FF&"
    }
    color_map_css = {
        "Kuning (Khas Reels/TikTok)": "#00ffff",
        "Putih Bersih": "#ffffff",
        "Hijau Terang": "#00ff00",
        "Merah Menyala": "#ff0000"
    }
    
    selected_color_code = color_map_ffmpeg.get(color_choice, "&H00FFFF&")
    css_color = color_map_css.get(color_choice, "#00ffff")

    align_map_ffmpeg = {
        "Bawah (Default)": 2,
        "Tengah Layar": 5,
        "Atas Layar": 8
    }
    selected_alignment = align_map_ffmpeg.get(pos_choice, 2)

    # Mapping CSS Flexbox untuk posisi pratinjau teks
    css_flex_pos = {
        "Bawah (Default)": "flex-end; padding-bottom: 25px;",
        "Tengah Layar": "center;",
        "Atas Layar": "flex-start; padding-top: 25px;"
    }
    selected_flex_pos = css_flex_pos.get(pos_choice, "flex-end; padding-bottom: 25px;")

    # --- KOTAK PRATINJAU (LIVE PREVIEW CONTAINER) ---
    st.markdown("**📱 Pratinjau Tampilan Subtitle pada Video (Live Preview):**")
    
    preview_html = f"""
    <div style="
        background: #0f172a; 
        border: 6px solid #334155; 
        border-radius: 16px; 
        width: 100%; 
        max-width: 320px; 
        height: 220px; 
        margin: 0 auto 20px auto; 
        display: flex; 
        flex-direction: column; 
        justify-content: {selected_flex_pos}; 
        align-items: center; 
        text-align: center; 
        padding: 10px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    ">
        <span style="
            font-family: '{font_choice}', sans-serif;
            font-size: {size_choice}px;
            color: {css_color};
            font-weight: bold;
            text-shadow: -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000;
            line-height: 1.2;
        ">
            Contoh Teks Subtitle Anda di Sini!
        </span>
    </div>
    """
    st.markdown(preview_html, unsafe_allow_html=True)
    # ------------------------------------------------

    edited_transcript = st.text_area(
        "📝 Editor Hasil Baca Suara (Voice-to-Text):", 
        value=st.session_state.transcript_text, 
        height=150
    )
    
    output_final_video = "video_final_with_subtitles.mp4"
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔥 Proses Bakar Teks ke Dalam Video", use_container_width=True):
            with st.spinner("Mesin sedang merender video dengan subtitle kustom..."):
                success = burn_subtitles_to_video(
                    st.session_state.temp_video_path, 
                    edited_transcript, 
                    output_final_video,
                    font_name=font_choice,
                    font_size=size_choice + 4, # Penyesuaian skala agar pas di video asli
                    color_code=selected_color_code,
                    alignment_val=selected_alignment
                )
                if success and os.path.exists(output_final_video):
                    st.session_state.video_processed = True
                    st.success("Berhasil! Subtitle suara asli telah ditanamkan secara permanen.")
                else:
                    st.error("Gagal merender video.")

    if st.session_state.video_processed and os.path.exists(output_final_video):
        with col_b2:
            with open(output_final_video, "rb") as f:
                st.download_button(
                    label="📥 Download Video Berisi Subtitle (MP4)",
                    data=f,
                    file_name="NoahPadlan_RealAudio_Captioned.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                    type="primary"
                )
