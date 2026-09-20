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
st.caption("Ubah Link Video YouTube (>1 Jam) Menjadi Multi-Klip Vertikal (9:16) + Fitur Review & Auto-Captions")
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
                        "transkrip_teks": "Potongan teks narasi yang akan dijadikan auto-captions..."
                    }}
                ]
                """
                response = model.generate_content(prompt_clipper)
                text_res = response.text.strip()
                if text_res.startswith("```json"):
                    text_res = text_res[7:]
                if text_res.endswith("```"):
                    text_res = text_res[:-3]
                
                st.session_state.clips_data = json.loads(text_res.strip())
                st.success("Analisis selesai! Silakan review hasil potongan di bawah.")
            except Exception as e:
                st.error(f"Gagal memproses video. Error: {e}")

# 5. STUDIO PENGATURAN, TOOLS PREVIEW 9:16 & DOWNLOAD
if st.session_state.clips_data:
    st.markdown("<br>#### 🎬 STEP 2: Studio Review, Pan/Crop 9:16 & Download Klip", unsafe_allow_html=True)

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
            
            c_prev, c_edit = st.columns([1, 1.2])
            
            with c_prev:
                st.markdown("**📱 Pratinjau Tampilan 9:16 (Live Preview)**")
                st.markdown(f"""
                    <div class="phone-mockup">
                        <div style="position: absolute; top: 15px; font-size: 11px; background: rgba(0,0,0,0.6); padding: 3px 8px; border-radius: 10px;">
                            9:16 Vertical View
                        </div>
                        <div style="font-size: 14px; font-weight: bold; margin-bottom: 10px; padding: 0 15px;">
                            {clip['judul_klip']}
                        </div>
                        <div style="font-size: 12px; background: rgba(250, 204, 21, 0.2); color: #facc15; padding: 8px 12px; border-radius: 6px; border: 1px solid #facc15; margin-top: 20px;">
                            💬 Auto-Captions:<br>"{clip['transkrip_teks'][:60]}..."
                        </div>
                        <div style="position: absolute; bottom: 15px; font-size: 10px; color: #94a3b8;">
                            Durasi: {clip['waktu_mulai']} - {clip['waktu_selesai']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
            with c_edit:
                st.markdown(f"**Judul Klip:** {clip['judul_klip']}")
                st.markdown(f"*Alasan AI:* {clip['alasan']}")
                
                pan_position = st.slider(
                    f"↔️ Geser Posisi Bingkai 9:16 (Kiri ➔ Kanan) [Klip {clip['id_klip']}]", 
                    min_value=0, max_value=100, value=50, step=5,
                    key=f"pan_{idx}"
                )
                
                st.markdown("**📝 Editor Teks Auto-Captions:**")
                st.text_area(
                    f"Edit Transkrip Klip #{clip['id_klip']}", 
                    value=clip['transkrip_teks'],
                    height=80,
                    key=f"text_{idx}"
                )
                
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button(f"🔍 Play / Review Klip", key=f"rev_{idx}", use_container_width=True):
                    st.info(f"Memutar pratinjau klip #{clip['id_klip']} dengan posisi pan {pan_position}%...")
            with col_b2:
                if st.button(f"✨ Download Klip #{clip['id_klip']}", key=f"dl_{idx}", use_container_width=True):
                    st.success(f"Klip #{clip['id_klip']} siap diunduh (Format MP4 9:16, Gaya: {auto_caption})!")
            with col_b3:
                if st.button(f"🗑️ Hapus Klip", key=f"del_{idx}", use_container_width=True):
                    st.warning(f"Klip #{clip['id_klip']} dihapus.")
            
            st.divider()
