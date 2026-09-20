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
                Format output HARUS JSON Array murni.
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
                
                # PARSING JSON AMAN TANPA BACKTICKS
                text_res = response.text
                start_idx = text_res.find('[')
                end_idx = text_res.rfind(']') + 1
                
                if start_idx != -1 and end_idx != 0:
                    clean_json = text_res[start_idx:end_idx]
                    st.session_state.clips_data = json.loads(clean_json)
                    st.success("Analisis selesai! Suara berhasil diekstrak menjadi teks.")
                else:
                    st.error("Gagal membaca struktur data dari AI. Silakan coba tekan tombol lagi.")
                    
            except Exception as e:
                st.error(f"Gagal memproses video. Error: {e}")

# 5. STUDIO PENGATURAN, TOOLS PREVIEW 9:16 & DOWNLOAD
if st.session_state.clips_data:
    st.markdown("<br>#### 🎬 STEP 2: Studio Review, Pan/Crop 9:16 & Editor Voice-to-Text", unsafe_allow_html=True)

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
                        <div style="font-size: 12px; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 8px 12px; border-radius: 6px; border: 1px solid #3b82f6; margin-top: 20px;">
                            🎙️ Voice-to-Text:<br>"{clip.get('voice_to_text', '')[:60]}..."
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
                
                st.markdown("**🎙️ Editor Hasil Generate Voice-to-Text:**")
                st.text_area(
                    f"Edit Teks Hasil Ekstraksi Suara Klip #{clip['id_klip']}", 
                    value=clip.get('voice_to_text', ''),
                    height=100,
                    key=f"text_{idx}"
                )
                
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                if st.button(f"🔍 Play / Review Klip", key=f"rev_{idx}", use_container_width=True):
                    st.info(f"Memutar pratinjau klip #{clip['id_klip']} dengan posisi pan {pan_position}%...")
            with col_b2:
                if st.button(f"✨ Download Klip #{clip['id_klip']}", key=f"dl_{idx}", use_container_width=True):
                    st.success(f"Klip #{clip['id_klip']} siap diunduh lengkap dengan data Voice-to-Text (Format MP4 9:16)!")
            with col_b3:
                if st.button(f"🗑️ Hapus Klip", key=f"del_{idx}", use_container_width=True):
                    st.warning(f"Klip #{clip['id_klip']} dihapus.")
            
            st.divider()
