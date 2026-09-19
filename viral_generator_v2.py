import streamlit as st
import google.generativeai as genai
import json

# 1. Konfigurasi Halaman Dasar
st.set_page_config(page_title="YukiVerse Shorts Engine", page_icon="🌌", layout="wide")

if "ide_list" not in st.session_state:
    st.session_state.ide_list = []
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ""
if "script_result" not in st.session_state:
    st.session_state.script_result = ""
if "keyword_result" not in st.session_state:
    st.session_state.keyword_result = {}
if "seo_result" not in st.session_state:
    st.session_state.seo_result = {}

# 2. INJEKSI CSS TAMPILAN MODERN
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    div.stButton > button { background-color: #3b82f6; color: white; border-radius: 8px; font-weight: 600; border: none; }
    div.stButton > button:hover { background-color: #2563eb; color: white; }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER
st.markdown("### 🌌 YukiVerse Shorts Engine")
st.caption("AI VIRAL FACTS GENERATOR")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 4. STEP 1: KONFIGURASI TOPIK
st.markdown("#### ⚙️ STEP 1: Konfigurasi Topik")
col1, col2 = st.columns(2)
with col1:
    kategori = st.selectbox("Filter Kategori", [
        "🎲 Acak Semua Kategori", "🗿 Sejarah Unik", 
        "🌍 Fakta Dunia", "🐒 Hewan Unik", "🍔 Makanan Unik", 
        "🔬 Sains Menarik", "🤯 Fakta yang Mematahkan Logika"
    ])
with col2:
    jumlah_topik = st.selectbox("Jumlah Topik", [6, 9, 12])

spesifik = st.text_input("Topik Spesifik (Opsional)", placeholder="Contoh: Peradaban kuno, rahasia sejarah...")
submit_button = st.button("✨ Generate Topic", use_container_width=True)

if submit_button:
    if not api_key:
        st.error("Silakan masukkan API Key di menu samping kiri terlebih dahulu.")
    else:
        with st.spinner("Merangkai ide konten viral terbaik..."):
            try:
                model = genai.GenerativeModel('gemini-3.6-flash')
                prompt_ide = f"""
                Buatkan {jumlah_topik} ide konten video short sejarah/fakta unik untuk kategori: {kategori}. Fokus spesifik: {spesifik}.
                Format output HARUS JSON Array murni tanpa teks lain:
                [
                    {{
                        "topik": "Judul Ide yang Memancing Rasa Penasaran",
                        "skor_viral": "9.5/10",
                        "poin_menarik": ["Poin visual 1", "Hook emosi 2", "Fakta unik 3"]
                    }}
                ]
                """
                response = model.generate_content(prompt_ide)
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.ide_list = json.loads(cleaned)
                st.success("Ide berhasil dibuat! Silakan pilih topik di bawah.")
            except Exception as e:
                st.error(f"Gagal menghasilkan ide. Error: {e}")

# 5. MENAMPILKAN HASIL GRID IDE
if st.session_state.ide_list:
    st.markdown("<br>#### 🚀 Hasil Ide Konten", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, ide in enumerate(st.session_state.ide_list):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**TOPIK #{idx+1}** | 🔥 {ide['skor_viral']}")
                st.markdown(f"##### \"{ide['topik']}\"")
                for p in ide['poin_menarik']:
                    st.caption(f"✓ {p}")
                if st.button( f"Pilih Topik Ini", key=f"select_{idx}", use_container_width=True):
                    st.session_state.selected_topic = ide['topik']
                    st.success( dipilih: {ide['topik']})

# 6. STEP 2: GENERATE SCRIPT
if st.session_state.selected_topic:
    st.divider()
    st.markdown(f"#### 🎬 STEP 2: Script Generator")
    st.info(f"Topik Terpilih: **{st.session_state.selected_topic}**")
    
    if st.button("✨ Generate Script Naskah", use_container_width=True):
        with genai.GenerativeModel('gemini-3.6-flash') as model:
            res_script = model.generate_content(f"Buatkan naskah video short (maks 60 detik) yang sangat engaging untuk topik: '{st.session_state.selected_topic}'. Sertakan Visual Cue dan Audio Cue.")
            st.session_state.script_result = res_script.text
            
    if st.session_state.script_result:
        st.text_area("Hasil Naskah (Script)", st.session_state.script_result, height=250)

    # 7. STEP 3: KEYWORD & FOOTAGE FINDER
    st.divider()
    st.markdown("#### 🔍 STEP 3: Keyword & Footage Finder")
    if st.button("🔎 Generate Keywords & Footage", use_container_width=True):
        with st.spinner("Mencari kata kunci dan referensi..."):
            model = genai.GenerativeModel('gemini-3.6-flash')
            prompt_kw = f"""
            Berikan data keyword untuk topik: '{st.session_state.selected_topic}'.
            Format JSON murni:
            {{
                "id": ["keyword indo 1", "keyword indo 2", "keyword indo 3"],
                "en": ["keyword eng 1", "keyword eng 2", "keyword eng 3"],
                "zh": ["keyword mandal 1", "keyword mandal 2"],
                "hashtags": ["#tag1", "#tag2", "#tag3"],
                "links": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
            }}
            """
            res_kw = model.generate_content(prompt_kw)
            cleaned_kw = res_kw.text.replace("```json", "").replace("```", "").strip()
            st.session_state.keyword_result = json.loads(cleaned_kw)

    if st.session_state.keyword_result:
        kw = st.session_state.keyword_result
        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            st.markdown("**Keyword Indonesia**")
            st.write(kw.get("id", []))
        with col_k2:
            st.markdown("**Keyword Inggris**")
            st.write(kw.get("en", []))
        with col_k3:
            st.markdown("**Keyword Mandarin**")
            st.write(kw.get("zh", []))
            
        st.markdown("**Hashtags Pencarian**")
        st.code(" ".join(kw.get("hashtags", [])))
        st.markdown("**Footage Reference Links**")
        for l in kw.get("links", []):
            st.markdown(f"- {l}")

    # 8. STEP 4: SEO & DESCRIPTION GENERATOR
    st.divider()
    st.markdown("#### 📈 STEP 4: SEO & Description Generator")
    if st.button("🚀 Generate SEO & Titles", use_container_width=True):
        with st.spinner("Meracik judul dan SEO terbaik..."):
            model = genai.GenerativeModel('gemini-3.6-flash')
            prompt_seo = f"""
            Berikan data SEO untuk topik: '{st.session_state.selected_topic}'.
            Format JSON murni:
            {{
                "titles": ["Judul 1", "Judul 2", "Judul 3"],
                "description": "Deskripsi singkat yang menarik untuk YouTube Shorts...",
                "score": "9.5/10"
            }}
            """
            res_seo = model.generate_content(prompt_seo)
            cleaned_seo = res_seo.text.replace("```json", "").replace("```", "").strip()
            st.session_state.seo_result = json.loads(cleaned_seo)

    if st.session_state.seo_result:
        seo = st.session_state.seo_result
        st.markdown("**Pilihan Judul Shorts:**")
        for t in seo.get("titles", []):
            st.markdown(f"- {t}")
        st.markdown("**Deskripsi Video:**")
        st.info(seo.get("description", ""))
        st.metric(label="SEO Potential Score", value=seo.get("score", "9.0/10"))
