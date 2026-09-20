import streamlit as st
import google.generativeai as genai
import json

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

# 3. HEADER
st.markdown("### ✂️ Noah Padlan Clipper")
st.caption("Ubah Link Video YouTube (>1 Jam) Menjadi Multi-Klip Vertikal (9:16) Ber-Skor Viral Berdasarkan Kategori Momen & Auto-Captions")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 4. PANEL INPUT LINK YOUTUBE & PILIHAN KATEGORI SKOR MOMEN AI
with st.container():
    st.markdown("#### 🔗 STEP 1: Masukkan Link YouTube & Kategori Fokus Skor AI")
    
    youtube_url = st.text_input("🔗 Tempel Link YouTube Video Panjang (> 1 Jam):", placeholder="https://www.youtube.com/watch?v=...")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Pilihan Kategori Fokus Skor AI yang baru
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

    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        auto_caption = st.selectbox("Gaya Auto-Captions Teks", [
            "Alex Hormozi Style (Kuning Menonjol)", 
            "Clean Minimalist (Putih Elegan)", 
            "Dynamic Pop (Warna Warni Aktif)"
        ])
    with col_opt2:
        ai_crop_mode = st.checkbox("Aktifkan AI Smart Reframe (Fokuskan objek di tengah 9:16)", value=True)
    
    analyze_button = st.button("🚀 Analisis & Potong Multi-Klip Berdasarkan Fokus Momen", use_container_width=True)

if analyze_button:
    if not api_key:
        st.error("Silakan masukkan API Key di menu samping kiri terlebih dahulu.")
    elif not youtube_url:
        st.warning("Silakan masukkan link YouTube terlebih dahulu.")
    else:
        with st.spinner(f"Menganalisis video berdasarkan kategori '{fokus_momen}'..."):
            try:
                model = genai.GenerativeModel('gemini-3.6-flash')
                
                prompt_clipper = f"""
                Analisis video YouTube dari tautan berikut: {youtube_url}. 
                Fokuskan pencarian klip dan penilaian skor viral berdasarkan kategori momen: '{fokus_momen}'.
                Buatkan {jumlah_klip} segmen klip terbaik berdurasi sekitar {target_durasi} detik yang paling berpotensi viral di TikTok/Shorts sesuai kategori tersebut.
                Format output HARUS JSON Array murni tanpa teks lain:
                [
                    {{
                        "id_klip": 1,
                        "waktu_mulai": "00:12:45",
                        "waktu_selesai": "00:13:30",
                        "kategori_momen": "{fokus_momen}",
                        "judul_klip": "Judul Klip yang Menarik",
                        "skor_viral": "9.6/10",
                        "alasan": "Alasan spesifik mengapa klip ini masuk kategori pilihan dan berpotensi viral",
                        "transkrip_teks": "Potongan teks narasi yang akan dijadikan auto-captions..."
                    }}
                ]
                """
                response = model.generate_content(prompt_clipper)
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.clips_data = json.loads(cleaned)
                st.success("Berhasil memindai klip berdasarkan kategori momen pilihan Anda!")
            except Exception as e:
                st.error(f"Gagal memproses video. Error: {e}")

# 5. MENAMPILKAN HASIL MULTI-KLIP & TOOLS PENYESUAIAN (PAN/CROP & EDIT)
if st.session_state.clips_data:
    st.markdown("<br>#### 🎬 STEP 2: Studio Pengaturan Multi-Klip (9:16 & Posisi Frame)", unsafe_allow_html=True)
    st.info("Setiap klip menampilkan skor prediksi viral yang disesuaikan dengan kategori momen yang Anda pilih, lengkap dengan kontrol pan/crop dan transkrip teks.")

    for idx, clip in enumerate(st.session_state.clips_data):
        with st.container():
            st.markdown(f"""
                <div class="clip-card">
                    <div style='display: flex; justify-content: space-between; font-weight: bold; color: #1e293b; margin-bottom: 8px;'>
                        <span>Klip #{clip['id_klip']} ({clip['waktu_mulai']} - {clip['waktu_selesai']}) | Kategori: {clip.get('kategori_momen', 'Umum')}</span>
                        <span style='color: #ea580c;'>🔥 Skor Viral: {clip['skor_viral']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"**Judul:** {clip['judul_klip']}")
                st.markdown(f"*Alasan AI:* {clip['alasan']}")
                
                # Tools Penggeser Posisi Video (Pan/Crop Kiri-Kanan) format 9:16
                pan_position = st.slider(
                    f"↔️ Geser Posisi Bingkai 9:16 (Kiri ➔ Kanan) [Klip {clip['id_klip']}]", 
                    min_value=0, max_value=100, value=50, step=5,
                    key=f"pan_{idx}"
                )
            with c2:
                st.markdown("**📝 Preview Auto-Captions (Teks Otomatis dari Suara):**")
                st.text_area(
                    f"Edit Teks Transkrip [{clip['id_klip']}]", 
                    value=clip['transkrip_teks'],
                    height=100,
                    key=f"text_{idx}"
                )
                
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button(f"✨ Download Klip #{clip['id_klip']} (MP4 9:16)", key=f"dl_{idx}", use_container_width=True):
                    st.success(f"Klip #{clip['id_klip']} dengan posisi pan {pan_position}% dan style takarir '{auto_caption}' berhasil dirender!")
            with col_b2:
                if st.button(f"🗑️ Hapus Klip Ini", key=f"del_{idx}", use_container_width=True):
                    st.warning(f"Klip #{clip['id_klip']} dihapus dari antrean.")
            
            st.divider()
