# file: test_eye_tracking.py
# Jalankan ini dulu untuk verifikasi setup kamu benar

import mediapipe
print("MediaPipe asli berasal dari:", mediapipe.__file__)

import cv2
import mediapipe as mp
import numpy as np

# Inisialisasi MediaPipe Face Mesh
import mediapipe.python.solutions.face_mesh as face_mesh
import mediapipe.python.solutions.drawing_utils as drawing_utils

mp_face_mesh = face_mesh
mp_drawing = drawing_utils

def hitung_EAR(landmarks, titik_mata, lebar_wajah):
    """
    Hitung Eye Aspect Ratio dari landmark mata.
    titik_mata = list indeks 6 titik landmark mata
    """
    # Ambil koordinat 6 titik landmark mata
    p1 = np.array([landmarks[titik_mata[0]].x, landmarks[titik_mata[0]].y])
    p2 = np.array([landmarks[titik_mata[1]].x, landmarks[titik_mata[1]].y])
    p3 = np.array([landmarks[titik_mata[2]].x, landmarks[titik_mata[2]].y])
    p4 = np.array([landmarks[titik_mata[3]].x, landmarks[titik_mata[3]].y])
    p5 = np.array([landmarks[titik_mata[4]].x, landmarks[titik_mata[4]].y])
    p6 = np.array([landmarks[titik_mata[5]].x, landmarks[titik_mata[5]].y])

    # Tinggi mata (vertikal)
    tinggi_atas  = np.linalg.norm(p2 - p6)
    tinggi_bawah = np.linalg.norm(p3 - p5)

    # Lebar mata (horizontal)
    lebar = np.linalg.norm(p1 - p4)

    # Rumus EAR
    ear = (tinggi_atas + tinggi_bawah) / (2.0 * lebar)
    return ear

# Indeks landmark MediaPipe untuk mata kanan & kiri
MATA_KANAN = [33, 160, 158, 133, 153, 144]
MATA_KIRI  = [362, 385, 387, 263, 373, 380]

# Threshold EAR — nanti kamu bisa sesuaikan!
THRESHOLD_GAS  = 0.44  # Di atas ini = melotot = GAS
THRESHOLD_REM  = 0.28  # Di bawah ini = sipit = REM

# Buka webcam
cap = cv2.VideoCapture(0)

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip biar kayak cermin (lebih natural)
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # Konversi ke RGB untuk MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        status = "IDLE"
        ear_rata = 0.0

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            # Hitung EAR kanan dan kiri, ambil rata-rata
            ear_kanan = hitung_EAR(landmarks, MATA_KANAN, w)
            ear_kiri  = hitung_EAR(landmarks, MATA_KIRI, w)
            ear_rata  = (ear_kanan + ear_kiri) / 2.0

            # Tentukan status berdasarkan EAR
            if ear_rata > THRESHOLD_GAS:
                status = "GAS!"
                warna  = (0, 255, 0)    # Hijau
            elif ear_rata < THRESHOLD_REM:
                status = "REM!"
                warna  = (0, 0, 255)    # Merah
            else:
                status = "IDLE"
                warna  = (200, 200, 200) # Abu-abu

            # Tampilkan nilai EAR dan status di layar
            cv2.putText(frame, f"EAR: {ear_rata:.3f}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, warna, 2)
            cv2.putText(frame, f"STATUS: {status}", (20, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, warna, 3)

        cv2.imshow("Test Eye Tracking - Tekan Q untuk keluar", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()