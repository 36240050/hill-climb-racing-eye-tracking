=================================================
HILL CLIMB EYE RACING: COMPUTER VISION GAME
=================================================

Version     : 1.0
Language    : Python 3.11
Category    : Computer Vision & 2D Physics Game
Framework   : Pygame, MediaPipe Face Mesh, OpenCV, NumPy

=================================================
PROJECT OVERVIEW
=================================================

Project ini mengimplementasikan teknologi Artificial Intelligence (AI) dan Computer Vision (CV) pada permainan perbukitan 2D yang terinspirasi dari game populer Hill Climb Racing. Inovasi utama dalam proyek ini adalah sistem kontrol inovatif nirsentuh (touchless control) menggunakan gerakan mata (eye tracking) melalui webcam secara real-time.

Sistem kontrol ini memanfaatkan library MediaPipe Face Mesh untuk memetakan titik landmark wajah dan mengalkulasi nilai Eye Aspect Ratio (EAR). Nilai tersebut kemudian dikonversi menjadi instruksi kendali mekanika game (Gas, Rem, atau Idle) secara instan.

Mekanisme Kontrol Terdeteksi:

1. State GAS (Mata Melotot)
   - Terjadi ketika nilai EAR > 0.30.
   - Di darat: Kendaraan berakselerasi maju ke depan.
   - Di udara: Badan mobil berotasi searah jarum jam (pitch up).

2. State REM (Mata Sipit / Memejam)
   - Terjadi ketika nilai EAR < 0.22.
   - Di darat: Kendaraan melakukan pengereman atau perlambatan aktif.
   - Di udara: Badan mobil berotasi berlawanan arah jarum jam (pitch down).

3. State IDLE (Mata Normal)
   - Terjadi ketika nilai 0.22 <= EAR <= 0.30.
   - Kendaraan berada dalam kondisi netral, kecepatan berkurang secara bertahap akibat gaya gesek alami.

=================================================
GAME OBJECTIVE
=================================================

Tujuan utama dalam Hill Climb Eye Racing adalah:

- Mengendarai mobil sejauh mungkin melewati terrain perbukitan yang dinamis.
- Mengumpulkan objek koin sepanjang lintasan untuk memaksimalkan score.
- Mengambil item Jerry Can (jeriken bensin) untuk mengisi ulang bahan bakar.
- Menjaga keseimbangan mobil agar tidak terbalik (terguling).
- Bertahan hidup selama mungkin tanpa kehabisan bensin.

=================================================
PROJECT ARCHITECTURE
=================================================

+-----------------------+
|        main.py        | <--- Entri Utama & Main Loop
+-----------+-----------+
            |
            v
+-----------------------+
|     Pipeline CV       | <--- OpenCV & MediaPipe (Hitung EAR Rata-rata)
+-----------+-----------+
            |
            v
+-----------------------+
|   Agent Controller    | <--- Mengubah State EAR menjadi Input Game
+-----------+-----------+
            |
    +-------+-------+
    |               |
    v               v
Vehicle State   Environment Loop
(src/car.py)    (src/terrain.py & objects)
    |               |
    +-------+-------+
            |
            v
     Game Environment  <--- Render Prosedural Pygame & UI Fitur PiP

=================================================
DIRECTORY STRUCTURE
=================================================

MLIS (Root Project)
│
├── hill_climb_eye/
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── car.py            # Sistem fisika kendaraan (darat & udara)
│   │   ├── coin.py           # Sistem koin dan deteksi tabrakan
│   │   ├── eye_tracker.py    # Logika ekstraksi landmark MediaPipe
│   │   ├── game.py           # Loop utama manajemen state gameplay
│   │   ├── jerrycan.py       # Manajemen objek bensin langka
│   │   ├── sound_manager.py  # Audio prosedural berbasis NumPy
│   │   └── ui.py             # Render UI: Menu, HUD, & Screen Game Over
│   │
│   ├── main.py               # Script eksekusi utama dalam subfolder
│   ├── requirements.txt      # Dependensi lokal subfolder
│   └── README.md             # Template README internal
│
├── computervision.py         # Modul pembantu pemrosesan citra
├── main.py                   # Titik masuk utama aplikasi (Root)
├── requirements.txt          # Daftar dependensi library utama
├── .gitignore                # File filter sampah Git (venv, dist, dll)
├── build.spec                # Konfigurasi kompilasi PyInstaller
└── README.md                 # Dokumentasi utama ini

=================================================
QUICK START
=================================================

Menjalankan game langsung dari source code:

python main.py

Memainkan game lewat file Executable (.exe) hasil build:
1. Buka folder `dist/HillClimbEyeRacing/`
2. Klik dua kali pada file `HillClimbEyeRacing.exe`

=================================================
AI AGENT EXECUTION
=================================================

Sistem berjalan secara otomatis mendeteksi input wajah tunggal (single face detection) dari webcam. Berikut logis pemrosesan matematika Eye Aspect Ratio (EAR) yang dieksekusi:

- Deteksi Wajah: Menggunakan BlazeFace (Detector) dari MediaPipe.
- Prediksi Geometri: Menggunakan Face Mesh Model untuk memetakan koordinat X, Y, Z.
- Ekstraksi Titik: Hanya mengambil 12 titik landmark spesifik (6 mata kiri, 6 mata kanan).
- Kamera Mirroring: Citra dibalik secara horizontal menggunakan `cv2.flip()` agar visualisasi Picture-in-Picture (PiP) terasa natural sebagai cermin pemain.

=================================================
PERFORMANCE EVALUATION
=================================================

Fitur performa dan indikator Heads-Up Display (HUD) yang dievaluasi secara real-time pada layar game:

- MATA   : Menampilkan klasifikasi state aktif (GAS / REM / IDLE).
- EAR    : Menampilkan nilai numerik keterbukaan mata saat ini.
- JARAK  : Jarak tempuh mobil dalam satuan meter (m).
- KOIN   : Jumlah skor poin terkumpul (1 koin = 10 pts).
- SPEED  : Kecepatan linier kendaraan (km/h).
- BENSIN : Indikator bar kapasitas bahan bakar (Maksimal 100%).

=================================================
DEBUGGING & GAME OVER LOGIC
=================================================

Permainan akan memicu layar GAME OVER berdasarkan dua logika kondisi kegagalan:

1. Mobil Terbalik:
   Sistem membaca sudut rotasi bodi mobil. Jika sudut rotasi melebihi ambang batas 110 derajat saat kendaraan berada di darat, game over akan dipicu (Pesan: "Mobil Terbalik!").

2. Bensin Habis:
   Sistem memantau kapasitas bensin. Jika bensin mencapai 0% dan kecepatan mobil menurun mendekati nol (< 0.1), game over dipicu (Pesan: "Bensin Habis!").

=================================================
REINFORCEMENT LEARNING & COMPUTER VISION CONCEPT
=================================================

Sistem Eye Tracking dihitung menggunakan rumus Jarak Euclidean antara titik kontur kelopak mata vertikal dan horizontal:

EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)

Dimana:
- p1, p4         = Titik sudut mata bagian horizontal (kiri & kanan).
- p2, p3, p5, p6 = Titik kontur kelopak mata bagian vertikal (atas & bawah).
- || . ||        = Jarak Euclidean antara dua koordinat titik spasial.

=================================================
FUTURE IMPROVEMENTS
=================================================

Beberapa pengembangan yang direkomendasikan untuk masa depan:

[AI]
- Implementasi mekanisme kalibrasi EAR otomatis di menu awal untuk menyesuaikan karakteristik fisik mata unik setiap pengguna.

[GAMEPLAY]
- Implementasi sistem level dinamis dengan tingkat kesulitan perbukitan (terrain) yang meningkat secara progresif seiring jarak.
- Penambahan sistem upgrade performa kendaraan (mesin, suspensi, kapasitas bensin) menggunakan koin yang berhasil dikumpulkan.

[ANALYTICS]
- Fitur penyimpanan catatan High Score lokal yang persisten, sehingga rekor pemain tidak hilang saat aplikasi ditutup.

[ENGINEERING]
- Eksplorasi porting aplikasi ke platform mobile (Android/iOS) memanfaatkan framework seperti Kivy atau BeeWare agar jangkauannya luas.

=================================================
SYSTEM REQUIREMENTS
=================================================

Minimum:

CPU      : Intel Core i3 / AMD Ryzen 3 atau setara
RAM      : 4 GB RAM
Webcam   : Kamera Webcam terintegrasi atau eksternal (720p)
Python   : Python 3.11 dengan kondisi ruangan cukup cahaya (well-lit)

Recommended:

CPU      : Intel Core i5 / AMD Ryzen 5 atau lebih tinggi
RAM      : 8 GB RAM atau lebih
Webcam   : HD Webcam dengan pencahayaan merata dari depan wajah
Python   : Python 3.11 (Aplikasi mandiri `.exe` berjalan di Windows 64-bit)

=================================================
REFERENCES
=================================================

- Soukupova, T. and Cech, J. (2016). Real-Time Eye Blink Detection Using Facial Landmarks.
- Google MediaPipe Face Mesh Documentation.
- Pygame Engine Community Documentation (SDL Architecture).

=================================================
LICENSE
=================================================

Project ini bersifat Open Source untuk keperluan akademik dan edukasi di bawah lisensi lokal Universitas Bunda Mulia. Seluruh aset grafis visual di dalam game dirender secara prosedural melalui kode pemrograman Pygame tanpa menggunakan file gambar eksternal berhak cipta.

=================================================
AUTHOR & CREDITS
=================================================

Universitas Bunda Mulia - Kampus Ancol
Ujian Akhir Semester - Machine Learning for Intelligence System (4PDS1)
Dosen Pengampu: Eko Wahyu Prasetyo, S.T., M.Eng

Disusun Oleh Kelompok Pengembangan:
1. Felicia Chelsey Hadi - 36240032
2. Velicia Christy Yona  - 36240050

Purpose : Inovasi interaksi manusia dan komputer (Human-Computer Interaction) memanfaatkan teknologi Computer Vision gratis dan open-source untuk hiburan lokal.
=================================================
