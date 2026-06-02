import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import io
import PyPDF2
import google.generativeai as genai

st.set_page_config(page_title="Modul AI Agama Katolik", page_icon="🕊️", layout="wide")

st.title("🕊️ Penyusun Modul Ajar Agama Katolik")
st.write("Sistem perancang modul otomatis berbasis dokumen Buku Ajar dengan Memori Rantai Terpusat.")

st.sidebar.subheader("🤖 Pengaturan Asisten AI")
api_key_guru = st.sidebar.text_input("🔑 Kunci API Gemini:", type="password")
st.sidebar.divider()
st.sidebar.write("Unggah PDF Buku Ajar di Tab 1 agar AI bisa membaca materinya.")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f5f9; border-radius: 8px 8px 0px 0px; padding: 10px 20px; box-shadow: inset 0 -2px 0 0 #cbd5e1; transition: all 0.3s ease; }
    .stTabs [aria-selected="true"] { background-color: #1e293b; color: #ffffff !important; box-shadow: 0 -4px 10px rgba(0,0,0,0.1); }
    .stButton > button[kind="primary"] { border-radius: 8px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- INISIALISASI MEMORI STATE ---
if 'data_isian' not in st.session_state: st.session_state.data_isian = {}
if 'teks_buku' not in st.session_state: st.session_state.teks_buku = ""

if 'draft_cp' not in st.session_state: st.session_state.draft_cp = ""
if 'draft_komp_awal' not in st.session_state: st.session_state.draft_komp_awal = ""
if 'draft_tp' not in st.session_state: st.session_state.draft_tp = ""
if 'draft_pemahaman' not in st.session_state: st.session_state.draft_pemahaman = ""
if 'draft_pemantik' not in st.session_state: st.session_state.draft_pemantik = ""
if 'draft_awal' not in st.session_state: st.session_state.draft_awal = ""
if 'draft_inti' not in st.session_state: st.session_state.draft_inti = ""
if 'draft_penutup' not in st.session_state: st.session_state.draft_penutup = ""
if 'draft_diagnostik' not in st.session_state: st.session_state.draft_diagnostik = ""
if 'draft_formatif' not in st.session_state: st.session_state.draft_formatif = ""
if 'draft_sumatif' not in st.session_state: st.session_state.draft_sumatif = ""

def simpan_teks(kunci, nilai):
    st.session_state.data_isian[kunci] = nilai

def panggil_ai(prompt):
    genai.configure(api_key=api_key_guru)
    
    mesin_tersedia = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    mesin_flash = [m for m in mesin_tersedia if 'flash' in m.lower() and 'interactions' not in m.lower()]
    
    if not mesin_flash:
        raise Exception("Kunci API ini tidak memiliki akses ke mesin Gemini Flash.")
        
    nama_mesin = None
    for m in mesin_flash:
        if '1.5' in m:
            nama_mesin = m
            break
            
    if not nama_mesin:
        nama_mesin = mesin_flash[0]
        
    aturan_global = """
    \n\nATURAN FORMATTING WAJIB (PENTING):
    1. WAJIB menggunakan huruf kecil normal dengan kapital di awal kalimat (Sentence Case). DILARANG KERAS teks berhuruf besar semua (UPPERCASE).
    2. JANGAN PERNAH menggunakan simbol tebal bergaya markdown seperti (**). Gunakan tanda petik dua ("...") sebagai penegas.
    3. JANGAN PERNAH membuat tabel horizontal bergaya markdown (|---|). Jabarkan vertikal dengan poin biasa.
    4. Gunakan penomoran lurus (1., 2., 3.) tanpa karakter khusus agar rata kiri-kanan rapi di Word.
    """
    
    model = genai.GenerativeModel(nama_mesin)
    return model.generate_content(prompt + aturan_global).text

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 1. Info Umum", "🎯 2. Pemantik", "🏃 3. Kegiatan", "📝 4. Asesmen", "🖨️ 5. Cetak"
])

# ================= TAB 1 =================
with tab1:
    st.subheader("Informasi Umum Modul")
    c1, c2 = st.columns(2)
    with c1:
        simpan_teks('MATA_PELAJARAN', st.text_input("Mata Pelajaran:", value="Pendidikan Agama Katolik & Budi Pekerti"))
        simpan_teks('Nama_Penyusun', st.text_input("Nama Penyusun:"))
        simpan_teks('Satuan_Pendidikan', st.text_input("Satuan Pendidikan (Nama Sekolah):"))
    with c2:
        peta_fase_kelas = {
            "Fase A": ["Kelas I", "Kelas II"], "Fase B": ["Kelas III", "Kelas IV"],
            "Fase C": ["Kelas V", "Kelas VI"], "Fase D": ["Kelas VII", "Kelas VIII", "Kelas IX"],
            "Fase E": ["Kelas X"], "Fase F": ["Kelas XI", "Kelas XII"]
        }
        kol_fase, kol_kelas = st.columns(2)
        with kol_fase: fase_terpilih = st.selectbox("Fase:", list(peta_fase_kelas.keys()))
        with kol_kelas: kelas_terpilih = st.selectbox("Kelas:", peta_fase_kelas[fase_terpilih])
            
        simpan_teks('Fase_Kelas', f"{fase_terpilih} / {kelas_terpilih}")
        
        pilihan_elemen = ["Pribadi Peserta Didik", "Yesus Kristus", "Gereja", "Masyarakat"]
        elemen = st.selectbox("Elemen:", pilihan_elemen)
        simpan_teks('Elemen', elemen)
        
        simpan_teks('Alokasi_Waktu', st.text_input("Alokasi Waktu (Contoh: 2 x 35 Menit):"))
    
    opsi_ppp = ["Beriman, Bertakwa kepada Tuhan YME, dan Berakhlak Mulia", "Berkebinekaan Global", "Bergotong Royong", "Mandiri", "Bernalar Kritis", "Kreatif"]
    pilihan_ppp = st.multiselect("Profil Pelajar Pancasila:", opsi_ppp)
    simpan_teks('Profil_Pelajar_Pancasila', ", ".join(pilihan_ppp))
    
    st.divider()
    st.subheader("📚 Sumber Materi & Ekstraksi AI")
    file_buku = st.file_uploader("Unggah PDF Buku Ajar / Bab Materi", type=['pdf'])
    
    if file_buku:
        with st.spinner("Mengekstrak teks dari PDF..."):
            pembaca = PyPDF2.PdfReader(file_buku)
            teks_sementara = ""
            for hal in pembaca.pages:
                t = hal.extract_text()
                if t: teks_sementara += t + "\n"
            st.session_state.teks_buku = teks_sementara
            st.success(f"Teks buku berhasil diserap! ({len(pembaca.pages)} halaman).")
            
        if st.button("✨ Rumuskan CP, Kompetensi Awal & TP Otomatis (AI)", key="btn_cptp"):
            if not api_key_guru: st.warning("Pastikan Kunci API terisi di Sidebar!")
            else:
                with st.spinner("AI menganalisis materi untuk merumuskan CP dan TP..."):
                    try:
                        prompt = f"""Berdasarkan materi buku ini:\n{st.session_state.teks_buku[:15000]}\n\n
                        Rumuskan:\n[CP]\n(1 paragraf Capaian Pembelajaran)\n[KOMP_AWAL]\n(Kompetensi Awal)\n[TP]\n(1-3 poin Tujuan Pembelajaran)
                        """
                        respons_ai = panggil_ai(prompt)
                        if "[CP]" in respons_ai and "[KOMP_AWAL]" in respons_ai and "[TP]" in respons_ai:
                            st.session_state.draft_cp = respons_ai.split("[CP]")[1].split("[KOMP_AWAL]")[0].strip()
                            st.session_state.draft_komp_awal = respons_ai.split("[KOMP_AWAL]")[1].split("[TP]")[0].strip()
                            st.session_state.draft_tp = respons_ai.split("[TP]")[1].strip()
                    except Exception as e: st.error(e)

    cp_input = st.text_area("Capaian Pembelajaran (CP):", value=st.session_state.draft_cp, height=100)
    simpan_teks('Capaian_Pembelajaran', cp_input)
    komp_awal_input = st.text_area("Kompetensi Awal:", value=st.session_state.draft_komp_awal, height=100)
    simpan_teks('Kompetensi_Awal', komp_awal_input)

# ================= TAB 2 =================
with tab2:
    st.subheader("Tujuan & Pemantik")
    tp = st.text_area("Tujuan Pembelajaran (TP):", value=st.session_state.draft_tp, height=100)
    simpan_teks('Tujuan_Pembelajaran', tp)
    
    if st.button("✨ Rumuskan Pemahaman & Pemantik (AI)", key="btn_pemantik"):
        if not api_key_guru or not st.session_state.teks_buku or not tp: st.warning("Pastikan Kunci API, PDF, dan TP terisi!")
        else:
            with st.spinner("AI merumuskan komponen inti berdasarkan Tujuan Pembelajaran..."):
                try:
                    # MEMORI: Membawa TP dari Tab 1
                    prompt = f"Berdasarkan buku ini:\n{st.session_state.teks_buku[:15000]}\n\nFOKUS TUJUAN PEMBELAJARAN: {tp}\n\nBuatkan:\n[PEMAHAMAN]\n(1 paragraf pemahaman bermakna yang selaras dengan TP di atas)\n[PEMANTIK]\n(3 pertanyaan pemantik yang memancing nalar kritis terkait TP tersebut)"
                    respons_ai = panggil_ai(prompt)
                    if "[PEMAHAMAN]" in respons_ai and "[PEMANTIK]" in respons_ai:
                        st.session_state.draft_pemahaman = respons_ai.split("[PEMAHAMAN]")[1].split("[PEMANTIK]")[0].strip()
                        st.session_state.draft_pemantik = respons_ai.split("[PEMANTIK]")[1].strip()
                except Exception as e: st.error(e)
                
    simpan_teks('Pemahaman_Bermakna', st.text_area("Pemahaman Bermakna:", value=st.session_state.draft_pemahaman, height=100))
    simpan_teks('Pertanyaan_Pemantik', st.text_area("Pertanyaan Pemantik:", value=st.session_state.draft_pemantik, height=100))
    gbr_pemantik = st.file_uploader("Gambar Pemantik (Opsional)", type=['png', 'jpg', 'jpeg'], key="g1")

# ================= TAB 3 =================
with tab3:
    st.subheader("Kegiatan Pembelajaran")
    
    opsi_model = ["Discovery Learning", "Problem Based Learning (PBL)", "Project Based Learning (PjBL)", "Inquiry Learning", "Cooperative Learning", "Pendekatan Saintifik (5M)"]
    model_belajar = st.selectbox("Pilih Pendekatan/Model Pembelajaran:", opsi_model)
    simpan_teks('Model_Pembelajaran', model_belajar)
    
    jml_pertemuan = st.number_input("Jumlah Pertemuan:", min_value=1, max_value=5, value=1)
    
    if st.button("✨ Rancang Kegiatan Pembelajaran (AI)", key="btn_kegiatan"):
        if not api_key_guru or not st.session_state.teks_buku or not tp: st.warning("Pastikan Kunci API, PDF, dan TP terisi!")
        else:
            with st.spinner(f"AI menyusun sintaks {model_belajar} dengan membaca data Tab 1 & 2..."):
                try:
                    # MEMORI: Membawa TP, Pemahaman, dan Pemantik dari Tab 1 & 2
                    konteks_modul = f"""
                    - Tujuan Pembelajaran: {tp}
                    - Pemahaman Bermakna: {st.session_state.draft_pemahaman}
                    - Pertanyaan Pemantik: {st.session_state.draft_pemantik}
                    """
                    
                    prompt = f"""Dari materi buku ini:\n{st.session_state.teks_buku[:15000]}\n\n
                    INFORMASI MODUL SEJAUH INI (Jadikan acuan utama agar kegiatan nyambung):
                    {konteks_modul}
                    
                    Rancang kegiatan {jml_pertemuan} pertemuan menggunakan sintaks model: {model_belajar}. 
                    Pastikan kegiatan yang dirancang benar-benar menjawab Pertanyaan Pemantik dan mencapai Tujuan Pembelajaran di atas.
                    
                    [AWAL]\n(Pendahuluan)\n[INTI]\n(Sintaks inti rinci)\n[PENUTUP]\n(Penutup)
                    """
                    respons_ai = panggil_ai(prompt)
                    if "[AWAL]" in respons_ai and "[INTI]" in respons_ai and "[PENUTUP]" in respons_ai:
                        st.session_state.draft_awal = respons_ai.split("[AWAL]")[1].split("[INTI]")[0].strip()
                        st.session_state.draft_inti = respons_ai.split("[INTI]")[1].split("[PENUTUP]")[0].strip()
                        st.session_state.draft_penutup = respons_ai.split("[PENUTUP]")[1].strip()
                except Exception as e: st.error(e)
                
    simpan_teks('Kegiatan_Awal', st.text_area("A. Kegiatan Pendahuluan:", value=st.session_state.draft_awal, height=150))
    simpan_teks('Kegiatan_Inti', st.text_area("B. Kegiatan Inti:", value=st.session_state.draft_inti, height=250))
    simpan_teks('Kegiatan_Penutup', st.text_area("C. Kegiatan Penutup:", value=st.session_state.draft_penutup, height=150))
    gbr_kegiatan = st.file_uploader("Gambar Kegiatan (Opsional)", type=['png', 'jpg', 'jpeg'], key="g2")

# ================= TAB 4 =================
with tab4:
    st.subheader("Asesmen Pembelajaran & Penugasan")
    
    st.info("💡 Ketik instruksi di bawah ini agar asesmen yang dibuat AI sesuai dengan gaya mengajar Anda.")
    instruksi_asesmen = st.text_area("Instruksi Khusus Asesmen (Opsional):", 
                                     placeholder="Contoh: Fokuskan penilaian formatif pada rubrik presentasi kelompok, dan soal sumatif berjenis studi kasus hots.")
    
    if st.button("✨ Buatkan Paket Asesmen (AI)", key="btn_asesmen"):
        if not api_key_guru or not st.session_state.teks_buku:
            st.warning("Pastikan Kunci API dan PDF terisi!")
        else:
            with st.spinner("AI menyusun asesmen dengan membaca seluruh aktivitas dari Tab 1, 2, dan 3..."):
                try:
                    # MEMORI: Membawa semua data dari Tab 1, 2, dan 3
                    konteks_modul_lengkap = f"""
                    - Tujuan Pembelajaran: {tp}
                    - Pemahaman Bermakna: {st.session_state.draft_pemahaman}
                    - Skenario Kegiatan Inti: {st.session_state.draft_inti}
                    """
                    
                    prompt = f"""Dari materi buku ini:\n{st.session_state.teks_buku[:15000]}\n\n
                    KONTEKS MODUL YANG SUDAH DIBUAT (Sangat Penting):
                    {konteks_modul_lengkap}
                    
                    Buatkan 3 ragam instrumen penilaian terpisah. 
                    Evaluasi WAJIB mengukur pencapaian 'Tujuan Pembelajaran' di atas dan harus relevan dengan 'Skenario Kegiatan Inti' yang sudah dilakukan siswa.
                    
                    INSTRUKSI KHUSUS DARI GURU: 
                    {instruksi_asesmen if instruksi_asesmen else 'Buatkan formatif berupa rubrik observasi dan sumatif berupa 5 soal pilihan ganda.'}
                    
                    Wajib gunakan tag ini:
                    [DIAGNOSTIK]\n(3 pertanyaan prasyarat)\n[FORMATIF]\n(Penilaian proses sesuai kegiatan inti)\n[SUMATIF]\n(Soal evaluasi akhir + kunci jawaban)
                    """
                    respons_ai = panggil_ai(prompt)
                    if "[DIAGNOSTIK]" in respons_ai and "[FORMATIF]" in respons_ai and "[SUMATIF]" in respons_ai:
                        st.session_state.draft_diagnostik = respons_ai.split("[DIAGNOSTIK]")[1].split("[FORMATIF]")[0].strip()
                        st.session_state.draft_formatif = respons_ai.split("[FORMATIF]")[1].split("[SUMATIF]")[0].strip()
                        st.session_state.draft_sumatif = respons_ai.split("[SUMATIF]")[1].strip()
                except Exception as e: st.error(e)
                
    simpan_teks('Asesmen_Diagnostik', st.text_area("Asesmen Diagnostik (Awal):", value=st.session_state.draft_diagnostik, height=150))
    gbr_diagnostik = st.file_uploader("Gambar Diagnostik (Opsional)", type=['png', 'jpg', 'jpeg'], key="g3")
    simpan_teks('Asesmen_Formatif', st.text_area("Asesmen Formatif (Proses):", value=st.session_state.draft_formatif, height=150))
    gbr_formatif = st.file_uploader("Gambar Formatif (Opsional)", type=['png', 'jpg', 'jpeg'], key="g4")
    simpan_teks('Asesmen_Sumatif', st.text_area("Asesmen Sumatif (Akhir):", value=st.session_state.draft_sumatif, height=150))
    gbr_sumatif = st.file_uploader("Gambar Sumatif (Opsional)", type=['png', 'jpg', 'jpeg'], key="g5")
    st.divider()
    simpan_teks('Lampiran_Pendukung', st.text_area("Lampiran Pendukung / Lembar Kerja:"))
    gbr_pendukung = st.file_uploader("Gambar Lampiran (Opsional)", type=['png', 'jpg', 'jpeg'], key="g6")

# ================= TAB 5 =================
with tab5:
    st.subheader("Lembar Pengesahan & Cetak")
    
    c_sah1, c_sah2 = st.columns(2)
    with c_sah1:
        tempat_terbit = st.text_input("Tempat Penerbitan (Kota):", value="Palangka Raya")
        tgl_terbit = st.text_input("Tanggal Penerbitan:", value="Juli 2026")
        simpan_teks('Tempat_Tanggal', f"{tempat_terbit}, {tgl_terbit}")
    with c_sah2:
        simpan_teks('Nama_Kepala_Sekolah', st.text_input("Nama Kepala Sekolah:"))
    
    st.divider()
    st.info("Pastikan file 'Template_Modul_Agama.docx' sudah Anda mutakhirkan (termasuk {{Elemen}}).")
    if st.button("🖨️ Rakit & Unduh Modul", type="primary", use_container_width=True):
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
                    file_name="Modul_Agama_Katolik.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Terjadi kesalahan saat merakit: {e}")
