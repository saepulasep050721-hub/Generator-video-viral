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

# 2. INJEKSI CSS TAMPILAN MODERN
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    div.stButton > button { background-color: #2563eb; color: white; border-radius: 8px; font-weight: 600; border: none; }
    div.stButton > button:hover { background-color: #1d4ed8; color: white; }
    .card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown("### ✍️ Noah Padlan Subtitle Burner Pro (Real Audio AI)")
st.caption("Mendengarkan Suara Asli Video Menggunakan Gemini File API & Kustomisasi Subtitle Permanen")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 3. FUNGSI PEMBAKARAN SUBTITLE DENGAN KUSTOMISASI GAYA FFMPEG
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
                    # Mengunggah file video asli agar AI bisa membaca audionya
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
                    
                    # Bersihkan file dari peladen AI setelah selesai
                    genai.delete_file(video_file.name)
                    
                    st.success("Suara asli video berhasil dibaca dan ditranskrip oleh AI!")
                except Exception as e:
                    st.error(f"Gagal membaca suara video. Error: {e}")

# 5. STUDIO EDITOR TEKS & KUSTOMISASI TAMPILAN SUBTITLE
if st.session_state.transcript_text and "temp_video_path" in st.session_state:
    st.markdown("<br>#### 🎬 STEP 2: Kustomisasi Teks & Pembakaran Subtitle", unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        font_choice = st.selectbox("🔤 Gaya Teks (Font)", ["Arial", "Impact", "Verdana", "Courier New"])
    with col_c2:
        size_choice = st.slider("📏 Ukuran Teks", min_value=16, max_value=48, value=24, step=2)
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

    color_map = {
        "Kuning (Khas Reels/TikTok)": "&H00FFFF&",
        "Putih Bersih": "&HFFFFFF&",
        "Hijau Terang": "&H00FF00&",
        "Merah Menyala": "&H0000FF&"
    }
    selected_color_code = color_map.get(color_choice, "&H00FFFF&")

    align_map = {
        "Bawah (Default)": 2,
        "Tengah Layar": 5,
        "Atas Layar": 8
    }
    selected_alignment = align_map.get(pos_choice, 2)

    edited_transcript = st.text_area(
        "📝 Editor Hasil Baca Suara (Voice-to-Text):", 
        value=st.session_state.transcript_text, 
        height=180
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
                    font_size=size_choice,
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
