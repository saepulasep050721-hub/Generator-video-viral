import streamlit as st
import google.generativeai as genai
import json

# 1. Konfigurasi Halaman Dasar
st.set_page_config(page_title="Noah Padlan Clipper", page_icon="✂️", layout="wide")

if "clips_data" not in st.session_state:
    st.session_state.clips_data = []

# 2. INJEKSI CSS TAMPILAN MODERN & LAYOUT PREVIEW 9:16
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

# 3. HEADER
st.markdown("### ✂️ Noah Padlan Clipper")
st.caption("Ubah Link Video YouTube (>1 Jam) Menjadi Multi-Klip Vertikal (9:16) + Review & Generate Voice-to-Text")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 4. PANEL INPUT LINK YOUTUBE & PENGATURAN AI
with st.container():
    st.markdown("#### 🔗 STEP 1: Masukkan Link YouTube & Pengaturan Klip")
    
    youtube_url = st.text_input("🔗 Tempel Link YouTube Video Panjang (> 1 Jam):", placeholder="https://www.youtube.com/watch?v=...")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fokus_momen = st.selectbox("🎯 Fokus Kategori Skor AI", [
            "✨ Golden Moment (Puncak Emosi / Inspiratif)", 
            "😂 Momen Lucu / Komedi / Hiburan", 
            "🔥 Debat / Perdebatan / Kontroversi", 
            "💡 Fakta Unik / Wawasan / Edukasi",
            "🎲 Acak Semua Jenis Momen"
        ])
    with col2:
        target_durasi = st.slider("Durasi Per Klip (Detik)", min_value=15, max_value=90, value=45, step=5)
    with col3:
        jumlah_klip = st.selectbox("Jumlah Target Klip Multi-Potong", [3, 5, 10, 15])

    ai_crop_mode = st.checkbox("Aktifkan AI Smart Reframe (Fokuskan objek di tengah 9:16)", value=True)
    
    analyze_button = st.button("🚀 Analisis Klip & Ekstrak Suara ke Teks", use_container_width=True)

if analyze_button:
    if not api_key:
        st.error("Silakan masukkan API Key di menu samping kiri terlebih dahulu.")
    elif not youtube_url:
        st.warning("Silakan masukkan link YouTube terlebih dahulu.")
    else:
        with st.spinner(f"Menganalisis momen '{fokus_momen}' & mengekstrak suara menjadi teks..."):
            try:
                model = genai.GenerativeModel('gemini-3.6-flash')
                
                prompt_clipper = f"""
                Analisis video YouTube dari tautan berikut: {youtube_url}. 
                Fokuskan pencarian klip dan penilaian skor viral berdasarkan kategori momen: '{fokus_momen}'.
                Buatkan {jumlah_klip} segmen klip terbaik berdurasi sekitar {target_durasi} detik yang paling berpotensi viral.
                Lakukan ekstraksi ucapan dalam audio klip tersebut (Voice-to-Text).
                Format output HARUS JSON Array murni tanpa teks lain, tanpa markdown block.
                [
                    {{
                        "id_klip": 1,
                        "waktu_mulai": "00:12:45",
                        "waktu_selesai": "00:13:30",
                        "kategori_momen": "{fokus_momen}",
                        "judul_klip": "Judul Klip yang Menarik",
                        "skor_viral": "9.6/10",
                        "alasan": "Alasan spesifik mengapa klip ini berpotensi viral",
                        "voice_to_text": "Teks hasil ekstraksi suara (speech-to-text) dari audio video..."
                    }}
                ]
                """
                response = model.generate_content(prompt_clipper)
                text_res = response.text.strip()
                if text_res.startswith("```json"):
                    text_res = text_res[7:]
                if text_res.endswith("
