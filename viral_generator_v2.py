import streamlit as st
import google.generativeai as genai
import json

# 1. Konfigurasi Halaman Dasar
st.set_page_config(page_title="Viral Cross-Platform Trend Finder", page_icon="🔥", layout="wide")

if "trend_list" not in st.session_state:
    st.session_state.trend_list = []
if "selected_trend" not in st.session_state:
    st.session_state.selected_trend = ""
if "strategy_result" not in st.session_state:
    st.session_state.strategy_result = {}

# 2. INJEKSI CSS TAMPILAN MODERN
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    div.stButton > button { background-color: #ef4444; color: white; border-radius: 8px; font-weight: 600; border: none; }
    div.stButton > button:hover { background-color: #dc2626; color: white; }
    </style>
""", unsafe_allow_html=True)

# 3. HEADER
st.markdown("### 🔥 Viral Cross-Platform Trend Finder")
st.caption("AI Analyzer untuk Menemukan Celah Konten Ber-Views Tinggi di TikTok, YouTube Shorts, & Reels")
st.divider()

api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
if api_key:
    genai.configure(api_key=api_key)

# 4. STEP 1: SCANNER TREN VIRAL
st.markdown("#### ⚙️ STEP 1: Filter Niche & Target Platform")
col1, col2 = st.columns(2)
with col1:
    niche = st.selectbox("Pilih Niche Konten", [
        "🗿 Sejarah Dunia & Tokoh Kontroversial", 
        "🌍 Fakta Unik & Sains Mengejutkan", 
        "🤯 Misteri, Konspirasi & Sisi Gelap Sejarah", 
        "🍔 Fenomena & Budaya Unik Global"
    ])
with col2:
    target_platform = st.selectbox("Target Algoritma Utama", [
        "Cross-Platform (TikTok, YouTube Shorts, Reels)",
        "TikTok (Fokus Retensi & Komentar Cepat)",
        "YouTube Shorts (Fokus Retensi 3 Detik Pertama)",
        "Instagram Reels (Fokus Estetika & Shareability)"
    ])

keyword_fokus = st.text_input("Kata Kunci / Tema Khusus (Opsional)", placeholder="Contoh: Perang dunia, peradaban kuno yang hilang...")
scan_button = st.button("🚀 Scan Topik Paling Berpotensi Viral", use_container_width=True)

if scan_button:
    if not api_key:
        st.error("Silakan masukkan API Key di menu samping kiri terlebih dahulu.")
    else:
        with st.spinner("Memindai pola algoritma dan topik ber-views tinggi..."):
            try:
                model = genai.GenerativeModel('gemini-3.6-flash')
                prompt_trend = f"""
                Bertindaklah sebagai analis data media sosial dan algoritma video pendek (TikTok, YouTube Shorts, Reels).
                Analisis dan berikan 6 ide/topik konten untuk niche: '{niche}' dengan fokus tema: '{keyword_fokus}' yang memiliki probabilitas tertinggi mendapatkan jutaan views dan likes.
                Format output HARUS JSON Array murni tanpa teks lain:
                [
                    {{
                        "topik_viral": "Judul/Premis Konten yang Sangat Memancing Penasaran",
                        "estimasi_potensi": "9.8/10 (Sangat Tinggi)",
                        "platform_terkuat": "TikTok & YouTube Shorts",
                        "alasan_viral": "Penjelasan mengapa topik ini memicu algoritma (misal: penolakan logika umum, rasa penasaran tinggi)",
                        "hook_3_detik_pertama": "Kalimat pembuka di 3 detik pertama video agar penonton tidak swipe"
                    }}
                ]
                """
                response = model.generate_content(prompt_trend)
                cleaned = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.trend_list = json.loads(cleaned)
                st.success("Analisis tren selesai! Pilih topik di bawah untuk melihat strategi meledakannya.")
            except Exception as e:
                st.error(f"Gagal melakukan scanning tren. Error: {e}")

# 5. MENAMPILKAN HASIL SCANNING TREND
if st.session_state.trend_list:
    st.markdown("<br>#### 📊 Hasil Analisis Topik Berpotensi Viral", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, trend in enumerate(st.session_state.trend_list):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**TREN #{idx+1}** | 🔥 {trend['estimasi_potensi']}")
                st.markdown(f"##### \"{trend['topik_viral']}\"")
                st.caption(f"**Target:** {trend['platform_terkuat']}")
                st.markdown(f"**Hook 3 Detik:** *\"{trend['hook_3_detik_pertama']}\"*")
                st.markdown(f"<p style='font-size: 12px; color: #64748b;'>💡 {trend['alasan_viral']}</p>", unsafe_allow_html=True)
                
                if st.button(f"🎯 Bedah Strategi Topik Ini", key=f"select_trend_{idx}", use_container_width=True):
                    st.session_state.selected_trend = trend['topik_viral']
                    st.success(f"Dipilih: {trend['topik_viral']}")

# 6. STEP 2: STRATEGI EKsekusi & RICEK ALGORITMA
if st.session_state.selected_trend:
    st.divider()
    st.markdown(f"#### 🎬 STEP 2: Bedah Strategi & Blueprint Konten")
    st.info(f"Topik Terpilih: **{st.session_state.selected_trend}**")
    
    if st.button("⚙️ Generate Strategi Meledak (Script & Algoritma)", use_container_width=True):
        with st.spinner("Menyusun blueprint optimasi algoritma..."):
            model = genai.GenerativeModel('gemini-3.6-flash')
            prompt_strat = f"""
            Berikan blueprint eksekusi konten untuk topik: '{st.session_state.selected_trend}' agar bisa tembus FYP/Beranda di TikTok dan YouTube.
            Format JSON murni:
            {{
                "struktur_video": "Panduan detik ke detik (0-3s hook, 3-30s body, 30-50s twist, 50-60s CTA)",
                "visual_cues": "Saran visual, transisi, atau footage arsip yang memicu retensi",
                "sound_strategy": "Saran jenis musik latar belakang (misal: misterius, sinematik berketukan cepat)",
                "caption_hooks": ["Caption 1 untuk memancing komentar debat", "Caption 2 untuk shareability"]
            }}
            """
            res_strat = model.generate_content(prompt_strat)
            cleaned_strat = res_strat.text.replace("```json", "").replace("```", "").strip()
            st.session_state.strategy_result = json.loads(cleaned_strat)

    if st.session_state.strategy_result:
        strat = st.session_state.strategy_result
        st.markdown("**⏱️ Struktur & Alur Video:**")
        st.write(strat.get("struktur_video", ""))
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("**👁️ Strategi Visual & Footage:**")
            st.write(strat.get("visual_cues", ""))
        with col_s2:
            st.markdown("**🎵 Strategi Audio/Musik:**")
            st.write(strat.get("sound_strategy", ""))
            
        st.markdown("**💬 Pilihan Caption Pemicu Komentar/Debat:**")
        for cap in strat.get("caption_hooks", []):
            st.code(cap)
