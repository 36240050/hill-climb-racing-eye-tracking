# 🏎️ Hill Climb Eye Racing: Computer Vision Game

Project inovatif nirsentuh (touchless control) menggunakan gerakan mata (eye tracking) berbasis Computer Vision secara real-time. Game ini dikembangkan untuk memenuhi tugas Ujian Akhir Semester - Machine Learning for Intelligence System (4PDS1) di Universitas Bunda Mulia.

## 👥 Kelompok

* Dosen Pengampu: Eko Wahyu Prasetyo, S.T., M.Eng
* Anggota Kelompok:
  1. Felicia Chelsey Hadi - 36240032
  2. Velicia Christy Yona - 36240050

## 📝 Ringkasan Project

Sistem kontrol pada game ini memanfaatkan kamera webcam untuk memetakan titik landmark wajah menggunakan MediaPipe Face Mesh dan mengalkulasi nilai Eye Aspect Ratio (EAR). Nilai tersebut kemudian dikonversi menjadi instruksi kendali mekanika game secara instan:

1. State GAS (Mata Melotot / Terbuka Lebar):
   * Kondisi: Nilai EAR > 0.30
   * Aksi: Di darat kendaraan berakselerasi maju; di udara badan mobil berotasi searah jarum jam (pitch up).

2. State REM (Mata Sipit / Memejam):
   * Kondisi: Nilai EAR < 0.22
   * Aksi: Di darat kendaraan mengerem aktif; di udara badan mobil berotasi berlawanan arah jarum jam (pitch down).

3. State IDLE (Mata Normal):
   * Kondisi: Nilai EAR antara 0.22 sampai 0.30
   * Aksi: Kendaraan berada dalam kondisi netral (kecepatan berkurang perlahan akibat gaya gesek).

## 🛠️ Teknologi & Library yang Digunakan

* Bahasa Pemrograman: Python 3.11
* Game Engine: Pygame 2.6.1 (rendering visual, input, audio)
* Pemrosesan Citra: OpenCV 4.9.0.80 (akses webcam & cermin horizontal)
* Face Tracking: MediaPipe 0.10.9 (deteksi landmark 468 titik wajah)
* Komputasi: NumPy 1.26.4 (perhitungan matematis EAR & audio prosedural)
* Kompilasi: PyInstaller 6.5.0 (build ke file executable .exe)

## 📊 Parameter Fisika Game

Game ini dikonfigurasi menggunakan nilai parameter fisika berikut untuk menjaga keseimbangan permainan:

* Akselerasi: 0.18 (Pertambahan kecepatan per frame saat state GAS aktif)
* Deselerasi Rem: 0.28 (Pengurangan kecepatan per frame saat state REM aktif)
* Gesekan: 0.025 (Hambatan alami lintasan yang memperlambat mobil secara pasif)
* Gravitasi: 0.22 (Percepatan gaya tarik ke bawah saat mobil melayang di udara)
* Kecepatan Maksimum: 9.0 (Batas puncak kecepatan linier kendaraan)
* Rotasi Udara: 1.1 (Derajat perputaran bodi mobil per frame di udara)
* Konsumsi Bensin (Gas): 0.065 (Pengurasan bensin per frame saat gas)
* Konsumsi Bensin (Idle): 0.018 (Pengurasan bensin per frame saat idle)

## 🗂️ Struktur Direktori Project

```text
MLIS (Root Project)
├── hill_climb_eye/
│   ├── src/
│   │   ├── car.py            # Sistem fisika kendaraan (darat & udara)
│   │   ├── coin.py           # Sistem koin dan deteksi tabrakan
│   │   ├── eye_tracker.py    # Logika ekstraksi landmark MediaPipe
│   │   ├── game.py           # Loop utama manajemen state gameplay
│   │   ├── jerrycan.py       # Manajemen objek bensin langka
│   │   ├── sound_manager.py  # Audio prosedural berbasis NumPy
│   │   └── ui.py             # Render UI: Menu, HUD, & Screen Game Over
│   ├── main.py               # Script eksekusi dalam subfolder
│   ├── requirements.txt      # Dependensi lokal subfolder
│   └── README.md             # Template README internal
├── computervision.py         # Modul pembantu pemrosesan citra
├── main.py                   # Titik masuk utama aplikasi (Root)
├── requirements.txt          # Daftar dependensi library utama
├── .gitignore                # File filter sampah Git
└── README.md                 # Dokumentasi utama ini
```

## 🎮 Cara Menjalankan Aplikasi
1. Menjalankan dari Source Code
Pastikan semua library ter-install sesuai requirements.txt, lalu jalankan perintah:

```Bash
python main.py
```

2. Menjalankan Lewat Aplikasi Jadi (.exe)
* Buka folder hill_climb_eye/HillClimbEyeRacing/HillClimbEyeRacing di komputer kamu.
* Klik dua kali pada file HillClimbEyeRacing.exe.


## ⚠️ Kondisi Game Over
* Permainan akan berakhir secara otomatis jika mendeteksi salah satu kondisi berikut:
* Mobil Terbalik: Sudut rotasi bodi mobil melebihi ambang batas 110 derajat saat menyentuh tanah. (Pesan: "Mobil Terbalik!")
* Bensin Habis: Kapasitas bahan bakar mencapai 0% dan kendaraan berhenti total (kecepatan < 0.1). (Pesan: "Bensin Habis!")

Project ini bersifat Open Source untuk keperluan akademik di bawah lisensi lokal Universitas Bunda Mulia. Seluruh aset grafis visual di dalam game dirender secara prosedural melalui kode pemrograman Pygame tanpa menggunakan gambar eksternal berhak cipta.
