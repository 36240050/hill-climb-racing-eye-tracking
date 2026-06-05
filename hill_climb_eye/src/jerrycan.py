# src/jerrycan.py
# Objek Jerry Can yang bisa diambil untuk refill bensin

import pygame
import math
import random

class JerryCan:
    def __init__(self, x, y):
        self.x        = x
        self.y        = y
        self.y_render = y
        self.aktif    = True
        self.animasi  = 0.0

        # Ukuran kotak jerry can
        self.lebar  = 28
        self.tinggi = 36
        # Hitbox radius (untuk deteksi tabrakan)
        self.radius = 22

    def update(self):
        # Efek mengambang naik-turun (sama kayak koin)
        self.animasi  += 0.06
        self.y_render  = self.y + math.sin(self.animasi) * 6

    def gambar(self, surface, kamera_x):
        if not self.aktif:
            return

        x_layar = int(self.x - kamera_x)
        y_layar = int(self.y_render)

        # Hanya gambar kalau terlihat di layar
        if not (-40 < x_layar < surface.get_width() + 40):
            return

        # ── Gambar jerry can pakai shape ──────────────────
        # Body utama (kotak hijau tua)
        body = pygame.Rect(x_layar - self.lebar//2,
                           y_layar - self.tinggi,
                           self.lebar, self.tinggi)
        pygame.draw.rect(surface, (30, 140, 50),  body, border_radius=4)
        pygame.draw.rect(surface, (20,  90, 30),  body, border_radius=4, width=2)

        # Corong di atas
        corong_x = x_layar + 4
        corong_y = y_layar - self.tinggi
        pygame.draw.rect(surface, (20, 100, 35),
                         (corong_x, corong_y - 8, 8, 10), border_radius=2)

        # Tanda bensin "⛽" atau tulisan "BBM"
        font = pygame.font.SysFont("Arial", 11, bold=True)
        teks = font.render("BBM", True, (180, 255, 180))
        surface.blit(teks, (x_layar - teks.get_width()//2,
                            y_layar - self.tinggi + 8))

        # Garis horizontal dekoratif
        garis_y = y_layar - self.tinggi//2
        pygame.draw.line(surface, (20, 90, 30),
                         (x_layar - self.lebar//2 + 3, garis_y),
                         (x_layar + self.lebar//2 - 3, garis_y), 2)

    def cek_tabrak(self, mobil):
        """Sama persis logikanya dengan koin."""
        if not self.aktif:
            return False

        sudut_rad = math.radians(mobil.sudut)

        def rot(ox, oy):
            rx = ox * math.cos(sudut_rad) - oy * math.sin(sudut_rad)
            ry = ox * math.sin(sudut_rad) + oy * math.cos(sudut_rad)
            return (mobil.x + rx, mobil.y + ry)

        titik_cek = [
            (mobil.x, mobil.y),
            rot( mobil.offset_ban_depan,    0),
            rot( mobil.offset_ban_belakang, 0),
        ]

        radius_gabung = self.radius + mobil.radius_ban + 15

        for (px, py) in titik_cek:
            if math.hypot(self.x - px, self.y_render - py) < radius_gabung:
                return True
        return False


class ManagerJerryCan:
    """Atur spawn, update, dan render semua jerry can."""

    def __init__(self, terrain):
        self.terrain       = terrain
        self.semua_jerrycan = []
        self.jarak_spawn_berikutnya = 2000

    def spawn_awal(self, jumlah=1):
        """Spawn jerry can pertama, lebih jarang dari koin."""
        for i in range(jumlah):
            # Jarak antar jerry can lebih jauh dari koin
            x = 2000 + i * 1500 + random.randint(-200, 200)
            y = self.terrain.tinggi_di_x(x) - random.randint(25, 60)
            self.semua_jerrycan.append(JerryCan(x, y))

    def spawn_baru(self, kamera_x, layar_w):
        """Spawn otomatis di depan kamera, tapi lebih jarang."""
        batas_kanan = kamera_x + layar_w + 800
        paling_kanan = max(
            (j.x for j in self.semua_jerrycan), default=0
        )
        # Jarak antar spawn ~700px (lebih jarang dari koin)
        if paling_kanan < batas_kanan:
            x = batas_kanan + random.randint(300, 700)
            y = self.terrain.tinggi_di_x(x) - random.randint(25, 65)
            self.semua_jerrycan.append(JerryCan(x, y))
            
        # ── Lapis 1: Cek jarak minimum ──────────────────────
        JARAK_MINIMUM = random.randint(5000, 8000)  # tiap spawn jaraknya beda-beda
        if paling_kanan > batas_kanan - JARAK_MINIMUM:
            return  # belum waktunya, skip dulu

        # ── Lapis 2: Random chance 15% ──────────────────────
        # Artinya: dari 100 kali kondisi jarak terpenuhi,
        # hanya ~15 kali jerry can benar-benar muncul
        PELUANG_SPAWN = 0.7
        if random.random() > PELUANG_SPAWN:
            return  # sial, tidak jadi spawn kali ini

        # Kalau lolos dua filter di atas, baru spawn!
        x = batas_kanan + random.randint(200, 600)
        y = self.terrain.tinggi_di_x(x) - random.randint(25, 65)
        self.semua_jerrycan.append(JerryCan(x, y))

    def update(self, mobil, kamera_x, layar_w):
        """
        Update semua jerry can.
        Return True kalau ada yang berhasil diambil.
        """
        ada_yang_diambil = False

        for jc in self.semua_jerrycan:
            if jc.aktif:
                jc.update()
                if jc.cek_tabrak(mobil):
                    jc.aktif        = False
                    ada_yang_diambil = True

        self.spawn_baru(kamera_x, layar_w)

        # Bersihkan yang sudah jauh ke kiri
        self.semua_jerrycan = [
            j for j in self.semua_jerrycan if j.x > kamera_x - 500
        ]

        return ada_yang_diambil

    def gambar(self, surface, kamera_x):
        for jc in self.semua_jerrycan:
            jc.gambar(surface, kamera_x)