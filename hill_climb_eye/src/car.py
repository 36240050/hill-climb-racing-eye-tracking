# src/car.py — v2: air physics + flip detection

import pygame, math

class Mobil:
    def __init__(self, x, y):
        self.x          = float(x)
        self.y          = float(y)
        self.vel_x      = 0.0   # kecepatan horizontal
        self.vel_y      = 0.0   # kecepatan vertikal (untuk lompat)
        self.sudut      = 0.0   # rotasi visual (derajat)
        self.kecepatan  = 0.0   # alias vel_x untuk kompatibilitas HUD

        # Konstanta fisika
        self.AKSELERASI      = 0.18
        self.DESELERASI_REM  = 0.28
        self.GESEKAN         = 0.025
        self.GRAVITASI       = 0.22   # lebih terasa dari sebelumnya
        self.KECEPATAN_MAX   = 9.0
        self.ROTASI_UDARA    = 3.5    # derajat per frame saat di udara

        # State
        self.gas_aktif  = False
        self.rem_aktif  = False
        self.di_tanah   = True    # True = roda menyentuh tanah
        self.terbalik   = False   # True = game over condition

        # Ukuran
        self.lebar              = 80
        self.tinggi             = 35
        self.radius_ban         = 14
        self.offset_ban_depan   =  25
        self.offset_ban_belakang= -25

    def set_kontrol(self, gas, rem):
        self.gas_aktif = gas
        self.rem_aktif = rem

    def update(self, terrain):
        tinggi_tanah = terrain.tinggi_di_x(self.x)
        batas_tanah  = tinggi_tanah - self.radius_ban

        # ── Deteksi apakah roda menyentuh tanah ──────────────
        self.di_tanah = (self.y >= batas_tanah - 2)

        if self.di_tanah:
            # ── FISIKA DARAT ──────────────────────────────────
            self.y     = batas_tanah
            self.vel_y = 0.0

            sudut_terrain = terrain.dapatkan_sudut_di_x(self.x)
            kemiringan    = math.sin(math.radians(sudut_terrain))

            if self.gas_aktif and not self.rem_aktif:
                self.vel_x += self.AKSELERASI
            elif self.rem_aktif:
                self.vel_x -= self.DESELERASI_REM

            # Gravitasi di tanjakan
            self.vel_x -= kemiringan * 0.12

            # Gesekan
            if abs(self.vel_x) > 0.01:
                self.vel_x -= math.copysign(self.GESEKAN, self.vel_x)
            else:
                self.vel_x = 0.0

            self.vel_x = max(-2.5, min(self.KECEPATAN_MAX, self.vel_x))

            # Rotasi body ikut terrain (smooth)
            self.sudut += (sudut_terrain - self.sudut) * 0.15

        else:
            # ── FISIKA UDARA ──────────────────────────────────
            # Gravitasi tarik ke bawah
            self.vel_y += self.GRAVITASI

            # Gas = rotasi searah jarum jam (pitch up)
            # Rem = rotasi berlawanan jarum jam (pitch down)
            if self.gas_aktif:
                self.sudut += self.ROTASI_UDARA
            if self.rem_aktif:
                self.sudut -= self.ROTASI_UDARA

        # Gerakkan mobil
        self.x += self.vel_x
        self.y += self.vel_y

        # Update alias kecepatan untuk HUD
        self.kecepatan = self.vel_x

        # ── Deteksi terbalik ─────────────────────────────────
        # Mobil dianggap terbalik jika sudut > 100 atau < -100 derajat
        sudut_norm = self.sudut % 360
        if sudut_norm > 180:
            sudut_norm -= 360
        if abs(sudut_norm) > 110 and self.di_tanah:
            self.terbalik = True

    def gambar(self, surface, kamera_x):
        x_layar = int(self.x - kamera_x)
        y_layar = int(self.y)
        self._gambar_placeholder(surface, x_layar, y_layar)

    def _gambar_placeholder(self, surface, x, y):
        sudut_rad = math.radians(self.sudut)

        def rot(px, py):
            rx = px * math.cos(sudut_rad) - py * math.sin(sudut_rad)
            ry = px * math.sin(sudut_rad) + py * math.cos(sudut_rad)
            return (x + rx, y + ry)

        # Body
        corners = [rot(-self.lebar//2, -self.tinggi),
                   rot( self.lebar//2, -self.tinggi),
                   rot( self.lebar//2,  0),
                   rot(-self.lebar//2,  0)]
        pygame.draw.polygon(surface, (220, 60, 60), corners)
        pygame.draw.polygon(surface, (150, 20, 20), corners, 2)

        # Kabin
        atap = [rot(-self.lebar//4,  -self.tinggi),
                rot( self.lebar//4,  -self.tinggi),
                rot( self.lebar//3,  -self.tinggi - 18),
                rot(-self.lebar//3,  -self.tinggi - 18)]
        pygame.draw.polygon(surface, (180, 220, 255), atap)  # kaca biru muda
        pygame.draw.polygon(surface, (120, 160, 200), atap, 2)

        # Ban
        for offset in [self.offset_ban_depan, self.offset_ban_belakang]:
            bx, by = rot(offset, 0)
            pygame.draw.circle(surface, (30,  30,  30),  (int(bx), int(by)), self.radius_ban)
            pygame.draw.circle(surface, (80,  80,  80),  (int(bx), int(by)), self.radius_ban, 2)
            pygame.draw.circle(surface, (200, 200, 200), (int(bx), int(by)), self.radius_ban // 2)