import streamlit as st
import google.generativeai as genai
import json

# 1. Konfigurasi Halaman Dasar (Ubah ke WIDE agar muat 3 kolom)
st.set_page_config(page_title="Shorts Engine", page_icon="🌌", layout="wide")

# Session State untuk menyimpan hasil ide agar tidak hilang saat tombol diklik
if "ide_list" not in st.session_state:
    st.session_state.ide_list = []

# 2. INJEKSI CSS UNTUK TAMPILAN KARTU
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    
    /* Desain form atas */
    .form-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
    /* Tombol utama */
    div.stButton > button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #2563eb;
        color: white;
    }
    
    /* Tombol sekunder (Buat Script) */
    .btn-script button {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        border: 1px solid #e2e8f0 !important;
    }
    .btn-script button:hover {
        background-color: #e2e8f0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER
st.markdown("### 🌌 Shorts Engine")
st.caption("AI VIRAL FACTS GENERATOR")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

# 4. FORMULIR INPUT
with st.container():
    st.markdown("#### ⚙️ STEP 1: Konfigurasi Topik")
    col1, col2 = st.columns(2)
    with col1:
        kategori = st.selectbox("Filter Kategori", [
            "🎲 Acak Semua Kategori", "🐻 Dongeng Anak Animasi 3D", 
            "🌍 Fakta Dunia", "🐒 Hewan Unik", "🍔 Makanan Unik", 
            "🔬 Sains Menarik", "🤯 Fakta yang Mematahkan Logika"
        ])
    with col2:
        jumlah_topik = st.selectbox("Jumlah Topik", [6, 9, 12, 15]) # Kelipatan 3 agar pas di grid

    spesifik = st.text_input("Topik Spesifik (Opsional)", placeholder="Contoh: Seli si siput dan Boni beruang madu...")
    submit_button = st.button("✨ Generate Topic", use_container_width=True)

# 5. LOGIKA GENERATE IDE
if submit_button:
    if not api_key:
        st.error("Silakan masukkan API Key di menu samping kiri terlebih dahulu.")
    else:
        prompt_ide = f"""
        Buatkan {jumlah_topik} ide konten untuk kategori: {kategori}. Fokus: {spesifik}.
        Format output HARUS JSON Array murni:
        [
            {{
                "topik": "Judul Ide",
                "skor_viral": "9.5/10",
                "poin_menarik": ["Poin visual menarik 1", "Poin emosi 2", "Poin fakta unik 3"]
            }}
        ]
        """
        with st.spinner("Mencari ide viral terbaik..."):
            try:
                response = model.generate_content(prompt_ide)
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.ide_list = json.loads(cleaned)
            except Exception as e:
                st.error(f"Gagal menghasilkan ide. Error: {e}")

# 6. MENAMPILKAN HASIL DENGAN GRID (KARTU)
if st.session_state.ide_list:
    st.markdown("<br>#### 🚀 Hasil Ide Konten", unsafe_allow_html=True)
    
    # Membuat 3 kolom
    cols = st.columns(3)
    
    for idx, ide in enumerate(st.session_state.ide_list):
        # Menempatkan kartu secara bergantian di kolom 1, 2, dan 3
        with cols[idx % 3]:
            # Membuat wadah (kartu) dengan garis tepi
            with st.container(border=True):
                # Baris atas: Topik ke-berapa & Skor
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; font-size: 12px; color: #64748b; margin-bottom: 10px; font-weight: bold;'>"
                    f"<span>TOPIK #{idx+1}</span>"
                    f"<span style='color: #f97316;'>🔥 {ide['skor_viral']}</span>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
                
                # Judul
                st.markdown(f"##### \"{ide['topik']}\"")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Alasan Menarik (Poin-poin)
                st.caption("KENAPA MENARIK:")
                for poin in ide['poin_menarik']:
                    st.markdown(f"<div style='font-size: 13px; color: #475569; margin-bottom: 5px;'>✓ {poin}</div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Tombol Buat Script (dengan style khusus agar tidak biru semua)
                st.markdown('<div class="btn-script">', unsafe_allow_html=True)
                if st.button("📄 Buat Script Topik Ini", key=f"btn_{idx}", use_container_width=True):
                    st.success(f"Fitur pembuat script untuk '{ide['topik']}' sedang disiapkan!")
                st.markdown('</div>', unsafe_allow_html=True)
