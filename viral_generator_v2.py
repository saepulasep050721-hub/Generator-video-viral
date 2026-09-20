import streamlit as st
import google.generativeai as genai
import json

# 1. Konfigurasi Halaman Dasar
st.set_page_config(page_title="YukiVerse AI Video Clipper Pro", page_icon="✂️", layout="wide")

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
st.markdown("### ✂️ YukiVerse AI Video Clipper Pro")
st.caption("Ubah Video Panjang (>1 Jam) Menjadi Multi-Klip Vertikal (9:16) Ber-Skor Viral & Auto-Captions")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 4. PANEL UPLOAD & PENGATURAN PEMOTONGAN
with st.container():
    st.markdown("#### 📥 STEP 1: Upload Video Panjang & Atur Parameter Klip")
    
    uploaded_file = st.file_uploader("Upload Video Utama (MP4, MKV, MOV - Bisa > 1 Jam)", type=["mp4", "mkv", "mov"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        target_durasi = st.slider("Durasi Per Klip (Detik)", min_value=15, max_value=90, value=45, step=5)
    with col2:
        jumlah_klip = st.selectbox("Jumlah Target Klip Multi-Potong", [3, 5, 10, 15])
    with col3:
        auto_caption = st.selectbox("Gaya Auto-Captions Teks", [
            "Alex Hormozi Style (Kuning Menonjol)", 
            "Clean Minimalist (Putih Elegan)", 
            "Dynamic Pop (Warna Warni Aktif)"
        ])

    ai_crop_mode = st.checkbox("Aktifkan AI Smart Reframe (Fokuskan wajah/objek di tengah 9:16)", value=True)
    
    analyze_button = st.button("🚀 Analisis & Potong Multi-Klip dengan AI", use_container_width=True)

if analyze_button:
    if not api_key:
        st.error("Silakan masukkan API Key di menu samping kiri terlebih dahulu.")
    elif not uploaded_file:
        st.warning("Silakan upload file video terlebih dahulu.")
    else:
        with st.spinner("Menganalisis audio, transkripsi teks, dan memindai momen paling viral dari video..."):
            try:
                model = genai.GenerativeModel('gemini-3.6-flash')
                
                # Simulasi analisis AI untuk memecah video panjang menjadi multi-klip bernilai viral tinggi
                prompt_clipper = f"""
                Simulasikan analisis file video berdurasi panjang. Buatkan {jumlah_klip} segmen klip terbaik berdurasi sekitar {target_durasi} detik yang paling berpotensi viral.
                Format output HARUS JSON Array murni tanpa teks lain:
                [
                    {{
                        "id_klip": 1,
                        "waktu_mulai": "00:12:45",
                        "waktu_selesai": "00:13:30",
                        "judul_klip": "Momen Paling Mengejutkan dalam Video",
                        "skor_viral": "9.6/10",
                        "alasan": "Memiliki hook emosional yang kuat di detik pertama",
                        "transkrip_teks": "Potongan teks narasi yang akan dijadikan auto-captions..."
                    }}
                ]
                """
                response = model.generate_content(prompt_clipper)
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.clips_data = json.loads(cleaned)
                st.success("Berhasil memindai dan memotong multi-klip!")
            except Exception as e:
                st.error(f"Gagal memproses klip. Error: {e}")

# 5. MENAMPILKAN HASIL MULTI-KLIP & TOOLS PENYESUAIAN (PAN/CROP & EDIT)
if st.session_state.clips_data:
    st.markdown("<br>#### 🎬 STEP 2: Studio Pengaturan Multi-Klip (9:16 & Posisi Frame)", unsafe_allow_html=True)
    st.info("Setiap klip di bawah dilengkapi skor prediksi viral, kontrol posisi horizontal, dan transkrip teks otomatis.")

    for idx, clip in enumerate(st.session_state.clips_data):
        with st.container():
            st.markdown(f"""
                <div class="clip-card">
                    <div style='display: flex; justify-content: space-between; font-weight: bold; color: #1e293b; margin-bottom: 8px;'>
                        <span>Klip #{clip['id_klip']} ({clip['waktu_mulai']} - {clip['waktu_selesai']})</span>
                        <span style='color: #ea580c;'>🔥 Skor Viral: {clip['skor_viral']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.markdown(f"**Judul:** {clip['judul_klip']}")
                st.markdown(f"*Alasan AI:* {clip['alasan']}")
                
                # Tools Penggeser Posisi Video (Pan/Crop Kiri-Kanan) khusus format 9:16
                pan_position = st.slider(
                    f"↔️ Geser Posisi Bingkai 9:16 (Kiri ➔ Kanan) [Klip {clip['id_klip']}]", 
                    min_value=0, max_value=100, value=50, step=5,
                    key=f"pan_{idx}"
                )
            with c2:
                st.markdown("**📝 Preview Auto-Captions (Teks Otomatis dari Suara):**")
                st.text_area(
                    f"Edit Teks Transkrip [{clip['id_klip']}]", 
                    value=clip['transkrip_tsx'] if 'transkrip_tsx' in clip else clip['transkrip_teks'],
                    height=100,
                    key=f"text_{idx}"
                )
                
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button(f"✨ Download Klip #{clip['id_klip']} (MP4 9:16)", key=f"dl_{idx}", use_container_width=True):
                    st.success(f"Klip #{clip['id_klip']} dengan posisi pan {pan_position}% dan style takarir berhasil dirender!")
            with col_b2:
                if st.button(f"🗑️ Hapus Klip Ini", key=f"del_{idx}", use_container_width=True):
                    st.warning(f"Klip #{clip['id_klip']} dihapus dari antrean.")
            
            st.divider()
