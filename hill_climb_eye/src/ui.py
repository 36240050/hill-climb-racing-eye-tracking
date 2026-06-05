# src/ui.py
# Semua tampilan UI: menu, HUD in-game, dan game over screen

import pygame
import math

class UI:
    def __init__(self, layar_w, layar_h):
        self.w = layar_w
        self.h = layar_h

        # Font
        self.font_besar  = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_sedang = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_kecil  = pygame.font.SysFont("Arial", 22)
        self.font_hud    = pygame.font.SysFont("Arial", 24, bold=True)

        # Animasi
        self.waktu = 0

    def gambar_menu(self, surface):
        """Layar menu utama."""
        self.waktu += 0.03

        # Background gradient sederhana
        surface.fill((20, 40, 80))

        # Bukit dekorasi di belakang
        for i in range(5):
            cx  = self.w * (i + 0.5) / 5
            cy  = self.h * 0.65
            rad = 180 + i * 20
            pygame.draw.circle(surface, (15, 90, 45), (int(cx), int(cy)), rad)

        # Judul dengan efek "bounce"
        bounce = math.sin(self.waktu * 2) * 6
        judul  = self.font_besar.render("HILL CLIMB", True, (255, 220, 50))
        sub    = self.font_besar.render("EYE RACING", True, (255, 255, 255))
        surface.blit(judul, (self.w//2 - judul.get_width()//2, 120 + bounce))
        surface.blit(sub,   (self.w//2 - sub.get_width()//2,   200 + bounce))

        # Panduan kontrol
        panduan = [
            ("👁  Mata MELOTOT", "= Gas / Tancap"),
            ("😑  Mata SIPIT",   "= Rem / Berhenti"),
            ("😐  Mata NORMAL",  "= Idle"),
        ]
        y_start = 310
        for label, aksi in panduan:
            bg = pygame.Surface((460, 38), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 100))
            surface.blit(bg, (self.w//2 - 230, y_start - 4))
            teks_l = self.font_kecil.render(label, True, (200, 240, 255))
            teks_r = self.font_kecil.render(aksi,  True, (100, 255, 150))
            surface.blit(teks_l, (self.w//2 - 210, y_start))
            surface.blit(teks_r, (self.w//2 + 60,  y_start))
            y_start += 48

        # Tombol mulai (berkedip)
        alpha_tombol = int(180 + math.sin(self.waktu * 4) * 75)
        tombol_surf  = pygame.Surface((320, 60), pygame.SRCALPHA)
        tombol_surf.fill((50, 200, 80, alpha_tombol))
        pygame.draw.rect(tombol_surf, (80, 255, 120, alpha_tombol),
                         (0, 0, 320, 60), border_radius=12)
        surface.blit(tombol_surf, (self.w//2 - 160, 490))

        teks_mulai = self.font_sedang.render("TEKAN SPASI / ENTER", True, (255, 255, 255))
        surface.blit(teks_mulai, (self.w//2 - teks_mulai.get_width()//2, 503))

        # Kredit kecil
        kredit = self.font_kecil.render("Gunakan webcam untuk kontrol mata!", True, (150, 200, 255))
        surface.blit(kredit, (self.w//2 - kredit.get_width()//2, self.h - 50))

    def gambar_hud(self, surface, skor, koin_skor, kecepatan, ear, status_mata):
        """HUD saat bermain."""
        # Panel kiri atas
        panel = pygame.Surface((260, 130), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 150))
        pygame.draw.rect(panel, (80, 80, 100, 200), (0, 0, 260, 130),
                         border_radius=10, width=1)
        surface.blit(panel, (10, 10))

        # Warna status
        warna = {"GAS!": (80, 220, 80),
                 "REM!": (220, 80, 80),
                 "IDLE": (200, 200, 200)}.get(status_mata, (200, 200, 200))

        # Teks HUD
        baris = [
            (f"MATA : {status_mata}",         warna),
            (f"EAR  : {ear:.3f}",             (255, 255, 255)),
            (f"JARAK: {skor} m",              (255, 220, 50)),
            (f"KOIN : {koin_skor} pts",       (255, 200, 0)),
            (f"SPEED: {kecepatan:.1f} km/h",  (180, 180, 255)),
        ]
        for i, (teks, warna_teks) in enumerate(baris):
            rendered = self.font_hud.render(teks, True, warna_teks)
            surface.blit(rendered, (22, 18 + i * 22))

        # Bar EAR visual
        self._gambar_bar_ear(surface, ear)

    def _gambar_bar_ear(self, surface, ear):
        """Bar visual yang menunjukkan level keterbukaan mata."""
        bar_x, bar_y = self.w - 180, 20
        bar_w, bar_h = 160, 18

        # Background bar
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h),
                         border_radius=6)

        # Isi bar (hijau = gas, merah = rem, abu = idle)
        persen = min(1.0, max(0.0, (ear - 0.15) / 0.25))
        if ear > 0.30:
            warna_bar = (80, 220, 80)
        elif ear < 0.22:
            warna_bar = (220, 80, 80)
        else:
            warna_bar = (180, 180, 180)

        isi_w = int(bar_w * persen)
        if isi_w > 4:
            pygame.draw.rect(surface, warna_bar,
                             (bar_x, bar_y, isi_w, bar_h), border_radius=6)

        # Border dan label
        pygame.draw.rect(surface, (120, 120, 140), (bar_x, bar_y, bar_w, bar_h),
                         border_radius=6, width=1)
        label = self.font_kecil.render("EYE OPEN", True, (180, 180, 200))
        surface.blit(label, (bar_x, bar_y + 22))

    def gambar_game_over(self, surface, skor_jarak, skor_koin, skor_terbaik, alasan=""):
        """Layar game over dengan rekap skor."""
        # Overlay gelap
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Panel tengah
        panel_w, panel_h = 500, 380
        panel_x = self.w//2 - panel_w//2
        panel_y = self.h//2 - panel_h//2
        panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((20, 20, 50, 230))
        pygame.draw.rect(panel, (100, 100, 180, 255),
                         (0, 0, panel_w, panel_h), border_radius=16, width=2)
        surface.blit(panel, (panel_x, panel_y))

        # Judul
        go_teks = self.font_besar.render("GAME OVER", True, (220, 60, 60))
        surface.blit(go_teks, (self.w//2 - go_teks.get_width()//2, panel_y + 30))

        if alasan:
            teks_alasan = self.font_sedang.render(
                f"💀  {alasan}", True, (255, 120, 120)
        )
            surface.blit(teks_alasan,
                         (self.w//2 - teks_alasan.get_width()//2,
                        panel_y + 100))  # tepat di bawah judul

        # Skor
        baris_skor = [
            ("Jarak Tempuh", f"{skor_jarak} m",    (255, 220, 50)),
            ("Koin Dikumpul", f"{skor_koin} pts",  (255, 200, 0)),
            ("Total Skor",   f"{skor_jarak + skor_koin}", (100, 255, 150)),
            ("REKOR",        f"{skor_terbaik}",    (255, 150, 50)),
        ]
        for i, (label, nilai, warna) in enumerate(baris_skor):
            y = panel_y + 130 + i * 50
            teks_l = self.font_sedang.render(label, True, (180, 180, 200))
            teks_n = self.font_sedang.render(nilai, True, warna)
            surface.blit(teks_l, (panel_x + 40, y))
            surface.blit(teks_n, (panel_x + panel_w - teks_n.get_width() - 40, y))

        # Tombol restart
        restart = self.font_sedang.render("SPASI = Main Lagi   ESC = Keluar",
                                          True, (200, 240, 255))
        surface.blit(restart, (self.w//2 - restart.get_width()//2, panel_y + 340))