import streamlit as st
import google.generativeai as genai
import json

# Setup halaman Streamlit
st.set_page_config(page_title="Viral Video Generator", page_icon="🚀", layout="wide")
st.title("🚀 Web Generator Ide & Script Video Viral")
st.markdown("Alat AI untuk kreator: Cari Ide, Prediksi Skor Viral, dan Buat Naskah (Shorts/TikTok/Reels).")

# Session State untuk menyimpan data agar tidak hilang saat tombol ditekan
if "ide_list" not in st.session_state:
    st.session_state.ide_list = []

# Sidebar untuk API Key
st.sidebar.header("Pengaturan")
api_key = st.sidebar.text_input("Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.sidebar.warning("Silakan masukkan API Key Gemini Anda di sini untuk mulai.")

# Form Input Pengguna
with st.container():
    st.subheader("1. Cari Ide Konten")
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            kategori = st.selectbox("Kategori Konten:", 
                                    ["Dongeng Anak Animasi 3D", "Fakta Dunia", "Hewan Unik", "Sains & Teknologi", "Lainnya"])
            kategori_lainnya = st.text_input("Sebutkan jika 'Lainnya':") if kategori == "Lainnya" else ""
                
        with col2:
            jumlah_topik = st.slider("Jumlah Ide:", min_value=1, max_value=10, value=3)
            
        spesifikasi = st.text_area("Spesifikasi/Karakter (Opsional):", 
                                   placeholder="Contoh: Fokus pada karakter Boni (anak beruang madu).")
        
        submit_button = st.form_submit_button("Generate Ide & Skor Viral ✨")

# Logika Generate Ide
if submit_button and api_key:
    kategori_final = kategori_lainnya if kategori == "Lainnya" else kategori
    
    prompt_ide = f"""
    Anda adalah analis tren TikTok dan YouTube Shorts. Buatkan {jumlah_topik} ide konten untuk kategori: {kategori_final}.
    Spesifikasi: {spesifikasi}.
    Format output HARUS JSON Array murni, contoh:
    [
        {{
            "topik": "Judul Ide",
            "skor_viral": 95,
            "alasan_menarik": "Alasan kenapa viral"
        }}
    ]
    Jangan gunakan awalan/akhiran markdown ```json.
    """
    
    with st.spinner("Mencari ide viral terbaik..."):
        try:
            response = model.generate_content(prompt_ide)
            cleaned = response.text.replace("```json", "").replace("```", "").strip()
            st.session_state.ide_list = json.loads(cleaned)
            st.success("Ide berhasil dibuat!")
        except Exception as e:
            st.error(f"Gagal menghasilkan ide. Coba lagi. Error: {e}")

# Menampilkan Hasil Ide dan Tombol Generate Script
st.divider()
if st.session_state.ide_list:
    st.subheader("2. Hasil Ide & Generator Naskah")
    
    for idx, ide in enumerate(st.session_state.ide_list):
        with st.expander(f"🔥 {ide['topik']} (Skor: {ide['skor_viral']}/100)"):
            st.progress(ide['skor_viral'] / 100)
            st.write(f"**Alasan:** {ide['alasan_menarik']}")
            
            # Tombol untuk generate naskah
            if st.button(f"✍️ Buat Script & SEO untuk: {ide['topik']}", key=f"btn_script_{idx}"):
                if api_key:
                    prompt_script = f"""
                    Buatkan naskah video vertikal (Shorts/TikTok) durasi 30-60 detik untuk topik: "{ide['topik']}".
                    
                    Tolong berikan output dalam format JSON murni dengan struktur:
                    {{
                        "hook": "Kalimat pertama yang sangat menarik perhatian (3 detik pertama)",
                        "isi_naskah": "Isi cerita/fakta, gunakan bahasa santai dan menarik",
                        "call_to_action": "Ajakan like/subscribe di akhir video",
                        "keyword_pencarian_footage": ["keyword inggris 1", "keyword mandarin 1 (untuk douyin)", "keyword inggris 2"],
                        "judul_seo": "Judul YouTube Shorts yang clickbait tapi aman",
                        "hashtag": "#tag1 #tag2 #tag3"
                    }}
                    Jangan gunakan awalan/akhiran markdown ```json.
                    """
                    
                    with st.spinner("Menulis naskah dan meracik SEO..."):
                        try:
                            res_script = model.generate_content(prompt_script)
                            cln_script = res_script.text.replace("```json", "").replace("```", "").strip()
                            script_data = json.loads(cln_script)
                            
                            st.success("Script berhasil dibuat!")
                            st.markdown("### 📜 Naskah Video")
                            st.info(f"**[HOOK 3 DETIK]**\n{script_data['hook']}")
                            st.write(f"**[ISI NASKAH]**\n{script_data['isi_naskah']}")
                            st.warning(f"**[CTA]**\n{script_data['call_to_action']}")
                            
                            st.markdown("### 🔍 Bahan & SEO")
                            st.write("**Kata Kunci Cari Footage (Inggris & Mandarin):**")
                            st.code(", ".join(script_data['keyword_pencarian_footage']))
                            st.write("**Judul Video (SEO):**")
                            st.code(script_data['judul_seo'])
                            st.write("**Hashtag:**")
                            st.code(script_data['hashtag'])
                            
                        except Exception as e:
                            st.error(f"Gagal membuat naskah: {e}")
                else:
                    st.warning("API Key belum dimasukkan.")
