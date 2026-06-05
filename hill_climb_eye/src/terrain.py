# src/terrain.py
# Modul untuk generate dan menggambar terrain bukit secara procedural

import pygame
import math
import random

class Terrain:
    def __init__(self, screen_width, screen_height):
        self.screen_w = screen_width
        self.screen_h = screen_height

        # Warna tanah (nanti bisa diganti texture/gambar)
        self.warna_tanah    = (101, 67, 33)   # Coklat
        self.warna_rumput   = (34, 139, 34)   # Hijau
        self.warna_langit   = (135, 206, 235) # Biru muda

        # Parameter bukit — coba ubah-ubah nilai ini buat variasi!
        self.amplitude  = 80    # Seberapa tinggi bukit
        self.frekuensi  = 0.008 # Seberapa rapat bukit (makin besar = makin rapat)
        self.offset_x   = 0     # Bergeser seiring kamera scroll

        # Seed random buat variasi terrain unik tiap main
        self.seed = random.randint(0, 1000)

    def tinggi_di_x(self, x_dunia):
        """
        Hitung tinggi terrain pada posisi X tertentu di dunia.
        Pakai kombinasi beberapa gelombang sinus buat tampilan natural.
        """
        # Titik acuan tengah layar (terrain dimulai dari sini ke bawah)
        tengah = self.screen_h * 0.6

        # Kombinasi 3 gelombang buat terrain yang lebih alami
        gelombang1 = math.sin(x_dunia * self.frekuensi + self.seed) * self.amplitude
        gelombang2 = math.sin(x_dunia * self.frekuensi * 2.3 + self.seed) * (self.amplitude * 0.4)
        gelombang3 = math.sin(x_dunia * self.frekuensi * 0.5 + self.seed) * (self.amplitude * 0.6)

        return tengah + gelombang1 + gelombang2 + gelombang3

    def gambar(self, surface, kamera_x):
        """
        Gambar terrain ke layar.
        kamera_x = posisi kamera (bergeser ke kanan seiring mobil maju)
        """
        # Gambar langit dulu sebagai background
        surface.fill(self.warna_langit)

        # Buat titik-titik polygon terrain
        titik_terrain = []

        # Mulai dari kiri layar, gambar tiap 5 pixel
        for x_layar in range(0, self.screen_w + 10, 5):
            x_dunia = x_layar + kamera_x
            y = self.tinggi_di_x(x_dunia)
            titik_terrain.append((x_layar, y))

        # Tutup polygon ke bawah layar
        titik_terrain.append((self.screen_w + 10, self.screen_h))
        titik_terrain.append((0, self.screen_h))

        # Gambar tanah (bagian bawah)
        pygame.draw.polygon(surface, self.warna_tanah, titik_terrain)

        # Gambar garis rumput di atas tanah (lebih tipis, warna berbeda)
        titik_rumput = titik_terrain[:-2]  # Ambil hanya titik garis atas
        if len(titik_rumput) >= 2:
            pygame.draw.lines(surface, self.warna_rumput, False, titik_rumput, 4)

    def dapatkan_sudut_di_x(self, x_dunia):
        """
        Hitung sudut kemiringan terrain pada posisi X.
        Berguna untuk rotasi mobil mengikuti kontur bukit.
        """
        delta = 5  # Selisih kecil untuk hitung kemiringan
        y1 = self.tinggi_di_x(x_dunia - delta)
        y2 = self.tinggi_di_x(x_dunia + delta)
        sudut_radian = math.atan2(y2 - y1, delta * 2)
        return math.degrees(sudut_radian)