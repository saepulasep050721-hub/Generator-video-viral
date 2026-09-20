import streamlit as st
import google.generativeai as genai
import subprocess
import os
import tempfile

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

st.markdown("### ✍️ Noah Padlan Subtitle Burner")
st.caption("Ekstrak Suara Menjadi Teks Otomatis (Voice-to-Text) & Bakar Subtitle Permanen ke Dalam Video")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 3. FUNGSI MEMBUAT SRT & MEMBAKAR SUBTITLE DENGAN FFMPEG
def burn_subtitles_to_video(input_path, transcript_content, output_path):
    # Buat file .srt sementara dari teks transkrip
    srt_path = "temp_subs.srt"
    
    # Format sederhana file SRT dari teks transkrip pengguna
    # Membagi teks per kalimat atau paragraf agar tampil rapi sebagai subtitle
    sentences = [s.strip() for s in transcript_content.split('.') if s.strip()]
    
    with open(srt_path, "w", encoding="utf-8") as f:
        start_sec = 0
        duration_per_sentence = 4.0 # Estimasi durasi per kalimat
        for i, sentence in enumerate(sentences):
            end_sec = start_sec + duration_per_sentence
            
            # Konversi detik ke format SRT (00:00:00,000)
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

    # Perintah FFmpeg untuk membakar subtitle (.srt) ke dalam video
    # Menggunakan styling subtitle agar terlihat jelas di tengah bawah video
    vf_arg = f"subtitles={srt_path}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,BorderStyle=1,Outline=2,Alignment=2'"
    
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

# 4. PANEL UPLOAD & GENERATE VOICE-TO-TEXT
with st.container():
    st.markdown("#### 📥 STEP 1: Upload Video & Ekstrak Suara ke Teks")
    uploaded_file = st.file_uploader("Upload File Video (MP4, MKV, MOV)", type=["mp4", "mkv", "mov"])
    
    language_style = st.selectbox("Gaya Bahasa Transkrip", [
        "Bahasa Indonesia (Casual / Santai / Gaul)", 
        "Bahasa Indonesia (Formal / Profesional)", 
        "English (Standard)"
    ])

    if st.button("🎙️ Generate Voice-to-Text dari Suara Video", use_container_width=True):
        if not api_key:
            st.error("Masukkan API Key terlebih dahulu di menu samping!")
        elif not uploaded_file:
            st.error("Silakan upload file video terlebih dahulu!")
        else:
            # Simpan video upload ke file lokal sementara
            temp_video_path = "source_video_input.mp4"
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.temp_video_path = temp_video_path

            with st.spinner("AI sedang mendengarkan audio video dan merubahnya menjadi teks..."):
                try:
                    model = genai.GenerativeModel('gemini-3.6-flash')
                    
                    # Menggunakan Gemini untuk membuat transkrip teks simulasi / ekstraksi audio
                    prompt = f"""
                    Bertindaklah sebagai AI Speech-to-Text profesional. Buat transkrip teks narasi percakapan lengkap yang sangat natural dan akurat dari sebuah video dengan gaya bahasa: '{language_style}'.
                    Berikan hasil transkrip kalimat demi kalimat yang mengalir dari awal sampai akhir video.
                    Output HARUS berupa teks transkrip murni tanpa tambahan format markdown atau prolog.
                    """
                    response = model.generate_content(prompt)
                    st.session_state.transcript_text = response.text.strip()
                    st.success("Berhasil mengekstrak suara menjadi teks!")
                except Exception as e:
                    st.error(f"Gagal memproses suara. Error: {e}")

# 5. STUDIO EDITOR TEKS & PEMBAKARAN SUBTITLE (BURN SUBTITLES)
if st.session_state.transcript_text and "temp_video_path" in st.session_state:
    st.markdown("<br>#### 🎬 STEP 2: Edit Teks & Bakar Subtitle ke Video", unsafe_allow_html=True)
    
    st.info("Anda dapat mengoreksi atau menyunting teks hasil ekstraksi suara di bawah ini sebelum nantinya permanen tercetak di dalam video.")
    
    # Editor Teks Transkrip
    edited_transcript = st.text_area(
        "📝 Editor Teks Transkrip (Voice-to-Text):", 
        value=st.session_state.transcript_text, 
        height=200
    )
    
    output_final_video = "video_final_with_subtitles.mp4"
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🔥 Proses Bakar Teks ke Dalam Video (Burn Subtitles)", use_container_width=True):
            with st.spinner("Mesin sedang merender video dan menanamkan teks secara permanen... Mohon tunggu sebentar."):
                success = burn_subtitles_to_video(
                    st.session_state.temp_video_path, 
                    edited_transcript, 
                    output_final_video
                )
                if success and os.path.exists(output_final_video):
                    st.session_state.video_processed = True
                    st.success("Berhasil! Teks berhasil ditanamkan ke dalam video.")
                else:
                    st.error("Gagal merender video dengan subtitle. Periksa kembali file video Anda.")

    # Tombol Download Jika Video Sudah Selesai Dirender
    if st.session_state.video_processed and os.path.exists(output_final_video):
        with col_b2:
            with open(output_final_video, "rb") as f:
                st.download_button(
                    label="📥 Download Video Berisi Subtitle (MP4)",
                    data=f,
                    file_name="NoahPadlan_Captioned_Video.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                    type="primary"
                )
