import streamlit as st
import PyPDF2
import google.generativeai as genai

st.set_page_config(page_title="Generator Modul AI", page_icon="📖")

st.title("📖 AI Peracik Buku Ajar (Pendidikan Agama Katolik)")
st.write("Unggah PDF Buku Ajar (atau satu bab spesifik), dan AI akan meracik modul berdasarkan isi buku tersebut.")

api_key_guru = st.text_input("🔑 Masukkan Kunci API Gemini:", type="password")
st.divider()

file_buku = st.file_uploader("📂 Unggah File PDF Buku Ajar (Maks 200MB):", type=['pdf'])

instruksi_guru = st.text_area(
    "🎯 Apa yang Anda inginkan dari buku ini?", 
    placeholder="Contoh: Buatkan 3 langkah kegiatan inti yang seru dan 5 pertanyaan formatif untuk anak SD Kelas 4 berdasarkan teks di atas."
)

if st.button("✨ Analisis Buku & Buat Modul", type="primary"):
    if not api_key_guru:
        st.error("⚠️ Masukkan Kunci API terlebih dahulu!")
    elif not file_buku:
        st.warning("⚠️ Mohon unggah file PDF buku ajar terlebih dahulu!")
    elif not instruksi_guru:
        st.warning("⚠️ Mohon ketikkan instruksi untuk AI!")
    else:
        with st.spinner("AI sedang membaca halaman demi halaman buku Anda... (Ini mungkin memakan waktu beberapa detik)"):
            try:
                
                pembaca_pdf = PyPDF2.PdfReader(file_buku)
                teks_buku = ""
                for halaman in pembaca_pdf.pages:
                    teks = halaman.extract_text()
                    if teks:
                        teks_buku += teks + "\n"
                
                st.success(f"✅ Berhasil membaca {len(pembaca_pdf.pages)} halaman. Mengirim teks ke AI...")
                
                
                genai.configure(api_key=api_key_guru)
                
                
                nama_mesin = None
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        nama_mesin = m.name
                        if 'flash' in m.name.lower():
                            break
                
                if not nama_mesin:
                    raise Exception("Tidak ada model AI yang diizinkan untuk Kunci API ini.")
                    
                model = genai.GenerativeModel(nama_mesin)
                
                
                prompt = f"""
                Anda adalah ahli pembuat modul pembelajaran Agama Katolik.
                
                BERIKUT ADALAH ISI BUKU AJAR SUMBER (Jadikan ini sebagai satu-satunya referensi materi Anda, jangan mengarang materi di luar buku ini):
                {teks_buku}
                
                INSTRUKSI TUGAS DARI GURU: 
                {instruksi_guru}
                """
                
                respon = model.generate_content(prompt)
                
                
                st.subheader("💡 Hasil Racikan AI:")
                st.write(respon.text)
                
            except Exception as e:
                st.error(f"⚠️ Terjadi kesalahan: {e}")
