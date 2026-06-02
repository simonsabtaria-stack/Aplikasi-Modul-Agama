import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io
import PyPDF2
import google.generativeai as genai

st.set_page_config(page_title="Modul AI Agama Katolik", page_icon="🕊️", layout="wide")

st.title("🕊️ Penyusun Modul Ajar Agama Katolik")
st.write("Sistem perancang modul otomatis berbasis dokumen Buku Ajar.")

st.sidebar.subheader("🤖 Pengaturan Asisten AI")
api_key_guru = st.sidebar.text_input("🔑 Kunci API Gemini:", type="password")
st.sidebar.divider()
st.sidebar.write("Unggah PDF Buku Ajar di Tab 1 agar AI bisa membaca materinya.")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        box-shadow: inset 0 -2px 0 0 #cbd5e1;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b;
        color: #ffffff !important;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.1);
    }
    .stButton > button[kind="primary"] {
        border-radius: 8px;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

if 'data_isian' not in st.session_state:
    st.session_state.data_isian = {}
if 'teks_buku' not in st.session_state:
    st.session_state.teks_buku = ""
if 'draft_pemantik' not in st.session_state:
    st.session_state.draft_pemantik = ""
if 'draft_kegiatan' not in st.session_state:
    st.session_state.draft_kegiatan = ""
if 'draft_asesmen' not in st.session_state:
    st.session_state.draft_asesmen = ""

def simpan_teks(kunci, nilai):
    st.session_state.data_isian[kunci] = nilai

def panggil_ai(prompt):
    genai.configure(api_key=api_key_guru)
    nama_mesin = None
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            nama_mesin = m.name
            if 'flash' in m.name.lower():
                break
    if not nama_mesin:
        raise Exception("Tidak ada model AI yang tersedia.")
    model = genai.GenerativeModel(nama_mesin)
    return model.generate_content(prompt).text

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 1. Info Umum", "🎯 2. Pemantik", "🏃 3. Kegiatan", "📝 4. Asesmen", "🖨️ 5. Cetak"
])

with tab1:
    st.subheader("Informasi Umum Modul")
    c1, c2 = st.columns(2)
    with c1:
        simpan_teks('MATA_PELAJARAN', st.text_input("Mata Pelajaran:", value="Pendidikan Agama Katolik & Budi Pekerti"))
        simpan_teks('Nama_Penyusun', st.text_input("Nama Penyusun:"))
        simpan_teks('Satuan_Pendidikan', st.text_input("Satuan Pendidikan (Nama Sekolah):"))
    with c2:
        simpan_teks('Fase_Kelas', st.text_input("Fase / Kelas:"))
        simpan_teks('Alokasi_Waktu', st.text_input("Alokasi Waktu (Contoh: 2 x 35 Menit):"))
        simpan_teks('Kompetensi_Awal', st.text_area("Kompetensi Awal:"))
    
    simpan_teks('Profil_Pelajar_Pancasila', st.text_area("Profil Pelajar Pancasila:"))
    
    st.divider()
    st.subheader("📚 Sumber Materi (Wajib untuk AI)")
    file_buku = st.file_uploader("Unggah PDF Buku Ajar / Bab Materi", type=['pdf'])
    if file_buku:
        with st.spinner("Mengekstrak teks dari PDF..."):
            pembaca = PyPDF2.PdfReader(file_buku)
            teks_sementara = ""
            for hal in pembaca.pages:
                t = hal.extract_text()
                if t: teks_sementara += t + "\n"
            st.session_state.teks_buku = teks_sementara
            st.success(f"Teks buku berhasil diserap! ({len(pembaca.pages)} halaman). AI siap digunakan di tab berikutnya.")

with tab2:
    st.subheader("Tujuan & Pemantik")
    tp = st.text_area("Tujuan Pembelajaran (TP):")
    simpan_teks('Tujuan_Pembelajaran', tp)
    
    if st.button("✨ Rumuskan Pemahaman & Pemantik (AI)", key="btn_pemantik"):
        if not api_key_guru or not st.session_state.teks_buku or not tp:
            st.warning("Pastikan Kunci API, PDF Buku di Tab 1, dan TP sudah terisi!")
        else:
            with st.spinner("AI menganalisis buku..."):
                try:
                    prompt = f"Berdasarkan teks buku ini:\n{st.session_state.teks_buku[:15000]}\n\nBuatkan 'Pemahaman Bermakna' (1 paragraf) dan 3 'Pertanyaan Pemantik' yang relevan dengan Tujuan Pembelajaran: {tp}.\n\nATURAN KETAT: Jawab LANGSUNG pada intinya. JANGAN menuliskan identitas modul, salam, atau mengulang TP. Cukup berikan teks untuk Pemahaman Bermakna dan Pertanyaan Pemantik saja."
                    st.session_state.draft_pemantik = panggil_ai(prompt)
                except Exception as e: st.error(e)
                
    simpan_teks('Pemahaman_Bermakna', st.text_area("Pemahaman Bermakna:", value=st.session_state.draft_pemantik, height=100))
    simpan_teks('Pertanyaan_Pemantik', st.text_area("Pertanyaan Pemantik:", height=100))
    gbr_pemantik = st.file_uploader("Gambar Pemantik (Opsional)", type=['png', 'jpg', 'jpeg'], key="g1")

with tab3:
    st.subheader("Kegiatan Pembelajaran (Pendekatan Discovery Learning / 6C)")
    
    if st.button("✨ Rancang Kegiatan Pembelajaran (AI)", key="btn_kegiatan"):
        if not api_key_guru or not st.session_state.teks_buku or not tp:
            st.warning("Pastikan Kunci API, PDF, dan TP terisi!")
        else:
            with st.spinner("AI menyusun langkah pembelajaran..."):
                try:
                    prompt = f"Berdasarkan materi buku ini:\n{st.session_state.teks_buku[:15000]}\n\nRancang 'Kegiatan Pembelajaran' (Pendahuluan, Inti, Penutup) untuk mencapai TP: {tp}.\n\nATURAN KETAT: Jawab LANGSUNG berupa langkah-langkah kegiatannya saja. JANGAN menuliskan judul modul, identitas, atau TP lagi. LANGSUNG mulai dari kata 'A. Kegiatan Pendahuluan', 'B. Kegiatan Inti', dan 'C. Kegiatan Penutup'."
                    st.session_state.draft_kegiatan = panggil_ai(prompt)
                except Exception as e: st.error(e)
                
    simpan_teks('Kegiatan_Pembelajaran', st.text_area("Skenario Kegiatan Pembelajaran:", value=st.session_state.draft_kegiatan, height=300))
    gbr_kegiatan = st.file_uploader("Gambar Kegiatan (Opsional)", type=['png', 'jpg', 'jpeg'], key="g2")

with tab4:
    st.subheader("Asesmen Pembelajaran")
    
    if st.button("✨ Buatkan Soal Asesmen (AI)", key="btn_asesmen"):
        if not api_key_guru or not st.session_state.teks_buku:
            st.warning("Pastikan Kunci API dan PDF terisi!")
        else:
            with st.spinner("AI membuat rubrik dan soal..."):
                try:
                    prompt = f"Dari materi buku ini:\n{st.session_state.teks_buku[:15000]}\n\nBuatkan 3 pertanyaan untuk 'Asesmen Diagnostik' (Awal), panduan observasi 'Asesmen Formatif', dan 5 soal pilihan ganda beserta kunci jawaban untuk 'Asesmen Sumatif'.\n\nATURAN KETAT: Jawab LANGSUNG ke isi asesmen. JANGAN menulis ulang identitas atau memberi kalimat pengantar. Pisahkan dengan jelas bagian Diagnostik, Formatif, dan Sumatif."
                    st.session_state.draft_asesmen = panggil_ai(prompt)
                except Exception as e: st.error(e)
                
    simpan_teks('Asesmen_Diagnostik', st.text_area("Asesmen Diagnostik (Awal):", value=st.session_state.draft_asesmen, height=150))
    gbr_diagnostik = st.file_uploader("Gambar Diagnostik (Opsional)", type=['png', 'jpg', 'jpeg'], key="g3")
    
    simpan_teks('Asesmen_Formatif', st.text_area("Asesmen Formatif (Proses):", height=150))
    gbr_formatif = st.file_uploader("Gambar Formatif (Opsional)", type=['png', 'jpg', 'jpeg'], key="g4")
    
    simpan_teks('Asesmen_Sumatif', st.text_area("Asesmen Sumatif (Akhir):", height=150))
    gbr_sumatif = st.file_uploader("Gambar Sumatif (Opsional)", type=['png', 'jpg', 'jpeg'], key="g5")
    
    st.divider()
    simpan_teks('Lampiran_Pendukung', st.text_area("Lampiran Pendukung / Lembar Kerja:"))
    gbr_pendukung = st.file_uploader("Gambar Lampiran (Opsional)", type=['png', 'jpg', 'jpeg'], key="g6")

with tab5:
    st.subheader("🖨️ Rakit Dokumen Word")
    st.info("Pastikan Anda sudah menyiapkan file 'Template_Modul_Agama.docx'.")
    
    if st.button("Rakit & Unduh Modul", type="primary", use_container_width=True):
        with st.spinner('Merakit dokumen...'):
            try:
                doc = DocxTemplate("Template_Modul_Agama.docx")
                
                if gbr_pemantik: st.session_state.data_isian['Gambar_Pemantik'] = InlineImage(doc, gbr_pemantik, width=Mm(100))
                else: st.session_state.data_isian['Gambar_Pemantik'] = ""
                
                if gbr_kegiatan: st.session_state.data_isian['Gambar_Kegiatan'] = InlineImage(doc, gbr_kegiatan, width=Mm(100))
                else: st.session_state.data_isian['Gambar_Kegiatan'] = ""
                
                if gbr_diagnostik: st.session_state.data_isian['Gambar_Diagnostik'] = InlineImage(doc, gbr_diagnostik, width=Mm(100))
                else: st.session_state.data_isian['Gambar_Diagnostik'] = ""
                
                if gbr_formatif: st.session_state.data_isian['Gambar_Formatif'] = InlineImage(doc, gbr_formatif, width=Mm(100))
                else: st.session_state.data_isian['Gambar_Formatif'] = ""
                
                if gbr_sumatif: st.session_state.data_isian['Gambar_Sumatif'] = InlineImage(doc, gbr_sumatif, width=Mm(100))
                else: st.session_state.data_isian['Gambar_Sumatif'] = ""
                
                if gbr_pendukung: st.session_state.data_isian['Gambar_Pendukung'] = InlineImage(doc, gbr_pendukung, width=Mm(100))
                else: st.session_state.data_isian['Gambar_Pendukung'] = ""
                
                doc.render(st.session_state.data_isian)
                bio = io.BytesIO()
                doc.save(bio)
                
                st.success("✅ Modul berhasil dirakit!")
                st.download_button(
                    label="📥 Download Modul (.docx)",
                    data=bio.getvalue(),
                    file_name=f"Modul_Agama_{st.session_state.data_isian.get('Fase_Kelas', 'Kelas')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Terjadi kesalahan saat merakit: {e}")
