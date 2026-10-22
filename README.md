# FuGu — your personal college partner

FuGu adalah prototipe Streamlit untuk membantu pengguna mengeksplorasi program studi, membandingkan kampus, memahami peluang beasiswa, dan melihat rekomendasi yang bisa dijelaskan.

## Batasan data (baca sebelum dipakai untuk KTI)

Dataset pada proyek ini adalah **katalog awal berukuran kecil**, bukan daftar lengkap seluruh kampus atau seluruh program studi di Indonesia. Nama program, deskripsi umum, serta URL berasal dari laman resmi kampus/penyelenggara yang ditautkan. Tag minat/keterampilan, sebagian ringkasan pembelajaran dan contoh karier disusun sebagai metadata prototipe, bukan klasifikasi resmi kampus. Periksa kembali sumber dan detail kurikulum sebelum mengutipnya.

Data `source_checked_on` mencatat kapan halaman sumber diperiksa saat paket disusun. Tanggal ini bukan jaminan bahwa laman atau ketentuannya tidak berubah setelahnya. FuGu tidak mengambil data secara otomatis dari semua situs dan tidak mengklaim adanya API nasional yang tersedia untuk semua sumber.

## Struktur folder

```text
fugu_rebuild/
├── app.py                     # Antarmuka Streamlit dan semua halaman
├── fugu_logic.py               # Filter, penskoran, dan pemeriksaan data
├── test_fugu_logic.py          # Tes otomatis untuk fungsi inti
├── requirements.txt            # Dependensi Python
├── README.md                   # Panduan ini
├── .gitignore
├── .streamlit/
│   └── config.toml             # Warna tema FuGu
└── data/
    ├── programs.json           # Sampel program studi + sumber resmi
    ├── universities.json       # Sampel kampus + laman resmi
    ├── scholarships.json       # Sumber beasiswa resmi
    └── references.json         # Bacaan ilmiah awal
```

## Fitur

- Home dengan tombol **Mulai Eksplorasi** dan tiga kartu navigasi.
- Survei bertahap: minat, preferensi/keterampilan, refleksi teks opsional, dan wilayah pilihan.
- Eksplorasi program studi dengan pencarian kata kunci, kategori, provinsi, dan kampus.
- Detail program dengan tautan laman program serta situs kampus resmi.
- Direktori universitas dengan pencarian, filter provinsi/jenis kampus, dan detail.
- Informasi beasiswa dengan pencarian, filter penyedia, tautan resmi, dan daftar simpanan untuk dibandingkan.
- Rekomendasi program dengan skor dan alasan yang transparan, serta diagram perbandingan.
- Halaman metode dan sumber data termasuk bacaan ilmiah untuk awal kajian pustaka.
- Transisi masuk halaman menggunakan animasi CSS ringan; perilaku animasi dapat berbeda antar-browser dan tetap tunduk pada pengaturan reduced motion.

## Logika rekomendasi

Skor prototipe membandingkan preferensi yang dinyatakan oleh pengguna dengan tag program:

- Minat: bobot 70.
- Preferensi/keterampilan yang dipilih: bobot 20, hanya bila diisi.
- Provinsi pilihan: bobot 10, hanya bila satu provinsi dipilih.

Bobot aktif dinormalisasi bila kriteria opsional tidak diisi. Ini adalah **bobot desain awal**, bukan bobot yang sudah tervalidasi secara ilmiah. Skor bukan persentase bakat, probabilitas diterima, ukuran psikologis, atau prediksi kelulusan. Evaluasi KTI memerlukan baseline, rubrik relevansi yang didefinisikan, evaluator, pengujian, dan pelaporan keterbatasan.

## Dependensi

- Python 3.10 atau lebih baru (untuk kompatibilitas, gunakan Python 3.11/3.12 jika tersedia di komputer Anda)
- Streamlit
- pandas
- Plotly

## Menjalankan dari nol (Windows)

1. Instal Python dari https://www.python.org/downloads/ jika belum ada. Saat installer menawarkan **Add Python to PATH**, aktifkan.
2. Ekstrak ZIP proyek.
3. Buka folder `fugu_rebuild`.
4. Klik kotak alamat File Explorer, ketik `cmd`, lalu tekan Enter.
5. Buat virtual environment:

   ```bat
   python -m venv .venv
   ```

6. Aktifkan environment:

   ```bat
   .venv\Scripts\activate
   ```

7. Instal paket:

   ```bat
   python -m pip install -r requirements.txt
   ```

8. Jalankan website:

   ```bat
   python -m streamlit run app.py
   ```

9. Buka alamat lokal yang dicetak di terminal, biasanya `http://localhost:8501`.

**Cara lebih mudah untuk penggunaan berikutnya (Windows):** setelah Python sudah terpasang, kamu bisa klik dua kali `run_fugu_windows.bat`. File ini akan membuat virtual environment bila belum ada, memasang dependensi dari `requirements.txt`, lalu menjalankan FuGu. Pada pemakaian pertama dibutuhkan internet untuk mengunduh paket. Jika ada pesan error, baca pesan terminal dan jangan langsung menghapus folder proyek.

Biarkan terminal tetap terbuka selama situs dipakai. Untuk mematikan server, fokus pada terminal lalu tekan `Ctrl+C`.

### macOS / Linux

Dari terminal di folder proyek:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Menjalankan tes otomatis

Saat virtual environment aktif dan paket sudah dipasang:

```bash
python -m unittest -v test_fugu_logic.py
```

Tes ini memeriksa struktur rekaman dasar, pencarian, filter wilayah/kategori, batas skor, pengurutan rekomendasi, dan alasan yang ditampilkan. Tes unit tidak membuktikan bahwa setiap tampilan browser berfungsi sempurna atau bahwa semua isi laman sumber selalu mutakhir.

## Cara tes manual tiap fitur

1. **Home**: klik Mulai Eksplorasi; klik masing-masing kartu Eksplorasi, Beasiswa, dan Kenali Dirimu.
2. **Kenali Dirimu**: coba lanjut tanpa minat (harus muncul peringatan), lalu pilih minat dan lanjutkan tiga langkah. Gunakan tombol kembali dan ubah jawaban.
3. **Eksplorasi**: cari `informatika`; filter kategori Teknologi; filter provinsi; filter satu kampus; hapus filter dan periksa jumlah hasil.
4. **Detail Program**: buka dari kartu; periksa ringkasan, tag, contoh mata kuliah, disclaimer karier, tautan program dan tautan kampus.
5. **Universitas**: cari `Yogyakarta`; filter provinsi DI Yogyakarta; ubah jenis PTN/PTS; buka profil satu kampus dan kembali.
6. **Beasiswa**: cari `KIP`; filter penyedia; buka situs resmi; tekan simpan dan hapus simpanan, lalu periksa daftar perbandingan.
7. **Rekomendasi**: selesaikan survei dengan satu atau lebih minat; amati diagram; buka alasan skor pada kartu; ubah preferensi dan ulangi.
8. **Metode & Sumber**: periksa catatan keterbatasan, tautan sumber program, portal resmi, dan bacaan jurnal.
9. **Responsif/animasi**: ubah ukuran jendela browser dan berpindah menu; efek fade/hover bersifat ringan dan bukan transisi halaman penuh.
10. **Uji link sumber**: buka setiap sumber resmi di tab baru. Situs luar dapat berubah, pindah URL, atau memerlukan akses tertentu.

## Publikasi gratis: GitHub + Streamlit Community Cloud

1. Buat repository di https://github.com/new. Jika ingin website publik, pilih **Public**.
2. Unggah **isi folder proyek** (bukan ZIP saja) supaya `app.py` dan `requirements.txt` berada di root repository. Sertakan folder `data/` dan `.streamlit/`. Jangan unggah `.venv`, kata sandi, token atau file rahasia.
3. Periksa repository memiliki struktur seperti ini:

   ```text
   repository/
   ├── app.py
   ├── fugu_logic.py
   ├── requirements.txt
   ├── data/
   └── .streamlit/config.toml
   ```

4. Buka https://share.streamlit.io/ lalu masuk dengan GitHub.
5. Pilih **Create app** dan **Yup, I have an app**.
6. Pilih repository, branch `main`, dan main file path `app.py`. Pilih subdomain jika tersedia, lalu klik **Deploy**.
7. Tunggu log deployment. Jika berhasil, buka URL `*.streamlit.app` yang diberikan.
8. Periksa setelan Sharing/Privacy. Aplikasi dari repository publik biasanya terbuka untuk umum, tetapi konfirmasikan pengaturan di aplikasi.
9. Uji seluruh fitur lagi dari link publik. Perubahan yang di-commit ke repository biasanya akan dipakai untuk pembaruan aplikasi.

Panduan resmi:
- Deploy: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Struktur file: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization
- Berbagi aplikasi: https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app

## Sumber data awal

### Portal data dan informasi pendidikan
- PDDikti: https://pddikti.kemdiktisaintek.go.id/
- BAN-PT: https://www.banpt.or.id/
- SNPMB: https://www.snpmb.id/jadwal-penting
- KIP Kuliah: https://kip-kuliah.kemdiktisaintek.go.id/

### Bacaan ilmiah awal
- da Silva, F. L., Slodkowski, B. K., da Silva, K. K. A., & Cazella, S. C. (2023). *A systematic literature review on educational recommender systems for teaching and learning: research trends, limitations and opportunities*. Education and Information Technologies, 28, 3289–3328. https://doi.org/10.1007/s10639-022-11341-9
- Deschênes, M. (2020). *Recommender systems to support learners’ Agency in a Learning Context: a systematic review*. International Journal of Educational Technology in Higher Education, 17, 50. https://doi.org/10.1186/s41239-020-00219-w
- *Recommender System in Academic Choices of Higher Education: A Systematic Review* (2024). IEEE Access, 12, 35475–35501. https://doi.org/10.1109/ACCESS.2024.3368058

Referensi ini merupakan titik awal kajian pustaka, bukan pengganti tinjauan literatur sistematis yang mengikuti protokol KTI Anda.

## Batasan yang diketahui

- Dataset belum komprehensif untuk seluruh Indonesia dan harus diperluas secara bertahap.
- Tag minat/preferensi merupakan metadata yang disusun untuk prototipe; perlu rubrik, peninjauan ahli, dan pengukuran konsistensi sebelum dipakai sebagai label penelitian.
- Beberapa daftar mata kuliah/karier adalah ringkasan umum dari orientasi bidang studi, bukan daftar kurikulum otoritatif lengkap.
- Detail jadwal beasiswa, biaya, kuota, akreditasi, dan penerimaan dapat berubah; cek langsung di sumber resmi.
- Tidak ada AI Assistant berbasis LLM dalam paket ini. Fokus versi ini adalah mesin rekomendasi berbobot yang deterministik agar bisa diuji. AI dapat ditambahkan kemudian dengan evaluasi tersendiri.
- Aplikasi tidak menyimpan profil survei ke database atau file; data survei hanya digunakan di sesi browser saat ini.
