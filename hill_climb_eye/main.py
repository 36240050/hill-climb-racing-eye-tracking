# main.py — Final v3: PiP webcam, air physics, fix koin, bensin, exit button

import pygame, sys, cv2, numpy as np, math
import mediapipe as mp

from src.terrain        import Terrain
from src.car            import Mobil
from src.coin           import ManagerKoin
from src.sound_manager  import SoundManager
from src.ui             import UI
from src.jerrycan import ManagerJerryCan

# ── Konfigurasi ─────────────────────────────────────────────
LEBAR, TINGGI   = 1280, 720
FPS             = 60
EAR_GAS         = 0.30
EAR_REM         = 0.22

MENU     = "menu"
BERMAIN  = "bermain"
GAMEOVER = "gameover"

# ── MediaPipe ───────────────────────────────────────────────
mp_mesh    = mp.solutions.face_mesh
MATA_KANAN = [33,  160, 158, 133, 153, 144]
MATA_KIRI  = [362, 385, 387, 263, 373, 380]

def hitung_EAR(lm, titik):
    p = [np.array([lm[i].x, lm[i].y]) for i in titik]
    return ((np.linalg.norm(p[1]-p[5]) + np.linalg.norm(p[2]-p[4]))
            / (2.0 * np.linalg.norm(p[0]-p[3]) + 1e-6))

# ── Konstanta Bensin ─────────────────────────────────────────
BENSIN_MAX      = 100.0
BENSIN_HABIS    = 0.0
BENSIN_DRAIN    = 0.095   # berkurang per frame saat gas
BENSIN_IDLE     = 0.030   # berkurang pelan saat idle

class Game:
    def __init__(self):
        pygame.init()
        self.layar = pygame.display.set_mode((LEBAR, TINGGI))
        pygame.display.set_caption("Hill Climb Eye Racing")
        self.clock = pygame.time.Clock()

        self.ui    = UI(LEBAR, TINGGI)
        self.sound = SoundManager()

        # Webcam & MediaPipe
        self.cap  = cv2.VideoCapture(0)
        self.mesh = mp_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        self.ear         = 0.25
        self.status_mata = "IDLE"
        self.frame_webcam = None   # simpan frame untuk PiP

        self.skor_terbaik = 0
        self.state        = MENU
        self._init_sesi()

    def _init_sesi(self):
        self.terrain    = Terrain(LEBAR, TINGGI)
        self.mobil      = Mobil(200, 300)
        self.koin_mgr   = ManagerKoin(self.terrain)
        self.koin_mgr.spawn_koin_awal(20)
        self.kamera_x   = 0.0
        self.skor_jarak = 0
        self.skor_koin  = 0
        self.bensin     = BENSIN_MAX
        self.alasan_gameover = ""

    # main.py — di dalam _init_sesi()

    def _init_sesi(self):
        self.terrain    = Terrain(LEBAR, TINGGI)
        self.mobil      = Mobil(200, 300)
        self.koin_mgr   = ManagerKoin(self.terrain)
        self.koin_mgr.spawn_koin_awal(20)
        self.jerrycan_mgr = ManagerJerryCan(self.terrain)   # ✅ baru
        self.jerrycan_mgr.spawn_awal(5)                     # ✅ baru
        self.kamera_x   = 0.0
        self.skor_jarak = 0
        self.skor_koin  = 0
        self.bensin     = BENSIN_MAX
        self.alasan_gameover = ""

    # ── Baca Mata ──────────────────────────────────────────
    def baca_mata(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, False

        frame = cv2.flip(frame, 1)
        self.frame_webcam = frame.copy()   # simpan untuk PiP

        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hasil = self.mesh.process(rgb)

        gas = rem = False
        if hasil.multi_face_landmarks:
            lm       = hasil.multi_face_landmarks[0].landmark
            self.ear = (hitung_EAR(lm, MATA_KANAN) +
                        hitung_EAR(lm, MATA_KIRI)) / 2.0
            if self.ear > EAR_GAS:
                gas = True;  self.status_mata = "GAS!"
            elif self.ear < EAR_REM:
                rem = True;  self.status_mata = "REM!"
            else:
                self.status_mata = "IDLE"
        return gas, rem

    # ── Picture-in-Picture Webcam ───────────────────────────
    def gambar_pip(self):
        """Tampilkan feed webcam di pojok kanan bawah."""
        if self.frame_webcam is None:
            return

        PIP_W, PIP_H = 240, 180
        MARGIN       = 12

        # Resize frame webcam
        frame_kecil = cv2.resize(self.frame_webcam, (PIP_W, PIP_H))

        # Gambar landmark titik mata (opsional, biar keliatan deteksinya)
        rgb_kecil = cv2.cvtColor(frame_kecil, cv2.COLOR_BGR2RGB)

        # Konversi BGR → RGB → Surface pygame
        frame_rgb = cv2.cvtColor(frame_kecil, cv2.COLOR_BGR2RGB)
        # Transpose karena OpenCV = (H,W,C), pygame = (W,H,C)
        frame_t   = np.transpose(frame_rgb, (1, 0, 2))
        pip_surf  = pygame.surfarray.make_surface(frame_t)

        # Posisi: pojok kanan bawah
        x_pos = LEBAR - PIP_W - MARGIN
        y_pos = TINGGI - PIP_H - MARGIN

        # Border + background
        border_rect = pygame.Rect(x_pos - 3, y_pos - 3, PIP_W + 6, PIP_H + 6)
        pygame.draw.rect(self.layar, (40, 40, 40), border_rect, border_radius=8)
        self.layar.blit(pip_surf, (x_pos, y_pos))
        pygame.draw.rect(self.layar, (100, 200, 100), border_rect,
                         border_radius=8, width=2)

        # Label status mata di atas PiP
        font_pip = pygame.font.SysFont("Arial", 15, bold=True)
        warna_label = {"GAS!": (80,220,80),
                       "REM!": (220,80,80),
                       "IDLE": (200,200,200)}.get(self.status_mata, (200,200,200))
        label = font_pip.render(f"📷 {self.status_mata}  EAR:{self.ear:.2f}",
                                True, warna_label)
        bg_label = pygame.Surface((label.get_width()+10, label.get_height()+4),
                                  pygame.SRCALPHA)
        bg_label.fill((0, 0, 0, 160))
        self.layar.blit(bg_label, (x_pos, y_pos - 22))
        self.layar.blit(label,    (x_pos + 5, y_pos - 20))

    # ── Tombol Exit In-Game ─────────────────────────────────
    def gambar_tombol_exit(self):
        """Tombol 'Menu' di pojok kanan atas saat sedang bermain."""
        font   = pygame.font.SysFont("Arial", 18, bold=True)
        teks   = font.render("⏹ MENU", True, (255, 255, 255))
        btn_w  = teks.get_width() + 24
        btn_h  = teks.get_height() + 12
        btn_x  = LEBAR - btn_w - 12
        btn_y  = 12

        # Simpan rect untuk deteksi klik
        self.rect_tombol_exit = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        mouse_pos  = pygame.mouse.get_pos()
        hover      = self.rect_tombol_exit.collidepoint(mouse_pos)
        warna_btn  = (180, 60, 60) if hover else (100, 40, 40)

        pygame.draw.rect(self.layar, warna_btn,
                         self.rect_tombol_exit, border_radius=8)
        pygame.draw.rect(self.layar, (220, 100, 100),
                         self.rect_tombol_exit, border_radius=8, width=1)
        self.layar.blit(teks, (btn_x + 12, btn_y + 6))

    # ── Bar Bensin ──────────────────────────────────────────
    def gambar_bar_bensin(self):
        """Bar bensin di pojok kiri bawah."""
        bar_x, bar_y = 14, TINGGI - 40
        bar_w, bar_h = 200, 18
        font = pygame.font.SysFont("Arial", 14, bold=True)

        # Background
        pygame.draw.rect(self.layar, (40, 40, 40),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=6)

        # Isi bensin
        persen  = self.bensin / BENSIN_MAX
        isi_w   = int(bar_w * persen)
        if persen > 0.5:
            warna_bensin = (80, 200, 80)
        elif persen > 0.25:
            warna_bensin = (230, 180, 30)
        else:
            warna_bensin = (220, 60, 60)

        if isi_w > 4:
            pygame.draw.rect(self.layar, warna_bensin,
                             (bar_x, bar_y, isi_w, bar_h), border_radius=6)

        pygame.draw.rect(self.layar, (140, 140, 160),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=6, width=1)

        label = font.render(f"⛽ {int(self.bensin)}%", True, (220, 220, 220))
        self.layar.blit(label, (bar_x + bar_w + 8, bar_y))

    # ── Handle Events ───────────────────────────────────────
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keluar()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == BERMAIN:
                        self.state = MENU       # langsung ke menu
                    else:
                        self.keluar()
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self.state == MENU:
                        self.state = BERMAIN
                    elif self.state == GAMEOVER:
                        self._init_sesi()
                        self.state = MENU       # kembali ke menu setelah game over

            # Klik tombol exit in-game
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == BERMAIN:
                    if hasattr(self, "rect_tombol_exit"):
                        if self.rect_tombol_exit.collidepoint(event.pos):
                            self.state = MENU

    # ── Update Saat Bermain ─────────────────────────────────
    def update_bermain(self):
        gas, rem = self.baca_mata()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]: gas = True
        if keys[pygame.K_LEFT]:  rem = True

        # Bensin habis = tidak bisa gas
        if self.bensin <= BENSIN_HABIS:
            gas = False
            if self.alasan_gameover == "":
                pass  # bensin habis ditangani di bawah

        # Update bensin
        if gas:
            self.bensin = max(0, self.bensin - BENSIN_DRAIN * 60 / FPS)
        else:
            self.bensin = max(0, self.bensin - BENSIN_IDLE  * 60 / FPS)

        self.mobil.set_kontrol(gas, rem)
        self.mobil.update(self.terrain)

        # Kamera smooth follow
        target       = self.mobil.x - LEBAR * 0.3
        self.kamera_x += (target - self.kamera_x) * 0.1

        # Update koin — kirim objek mobil, bukan koordinat
        koin_dapat = self.koin_mgr.update(
            self.mobil, self.kamera_x, LEBAR
        )
        if koin_dapat:
            self.sound.mainkan_koin()
            self.skor_koin += koin_dapat

        self.skor_jarak = max(self.skor_jarak, int(self.mobil.x / 10))
        self.sound.update_engine(self.mobil.kecepatan)

        if self.jerrycan_mgr.update(self.mobil, self.kamera_x, LEBAR):
            # Refill bensin saat diambil
            self.bensin = min(BENSIN_MAX, self.bensin + 10)  # +10%, tidak melebihi max
            self.sound.mainkan_bensin()

        # ── Cek Kondisi Game Over ──────────────────────────
        game_over = False

        if self.mobil.terbalik:
            self.alasan_gameover = "Mobil Terbalik!"
            game_over = True

        if self.bensin <= BENSIN_HABIS:
            # Beri waktu mobil berhenti total
            if abs(self.mobil.kecepatan) < 0.1:
                self.alasan_gameover = "Bensin Habis!"
                game_over = True

        if game_over:
            total = self.skor_jarak + self.skor_koin
            self.skor_terbaik = max(self.skor_terbaik, total)
            self.sound.mainkan_gameover()
            self.state = GAMEOVER

    # ── Gambar Saat Bermain ─────────────────────────────────
    def gambar_bermain(self):
        self.terrain.gambar(self.layar, self.kamera_x)
        self.koin_mgr.gambar(self.layar, self.kamera_x)
        self.jerrycan_mgr.gambar(self.layar, self.kamera_x)
        self.mobil.gambar(self.layar, self.kamera_x)
        self.ui.gambar_hud(
            self.layar, self.skor_jarak, self.skor_koin,
            self.mobil.kecepatan, self.ear, self.status_mata
        )
        self.gambar_bar_bensin()
        self.gambar_tombol_exit()
        self.gambar_pip()           # PiP webcam selalu paling atas

    # ── Main Loop ───────────────────────────────────────────
    def jalankan(self):
        while True:
            self.handle_events()

            if self.state == MENU:
                self.ui.gambar_menu(self.layar)

            elif self.state == BERMAIN:
                self.update_bermain()
                self.gambar_bermain()

            elif self.state == GAMEOVER:
                self.gambar_bermain()
                self.ui.gambar_game_over(
                    self.layar,
                    self.skor_jarak,
                    self.skor_koin,
                    self.skor_terbaik,
                    self.alasan_gameover   # ← kirim alasan ke UI
                )

            pygame.display.flip()
            self.clock.tick(FPS)

    def keluar(self):
        self.cap.release()
        self.mesh.close()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().jalankan()