# src/coin.py — Fixed collision detection

import pygame
import math
import random

class Koin:
    def __init__(self, x, y):
        self.x       = x
        self.y       = y
        self.y_render = y
        self.radius  = 14
        self.nilai   = 10
        self.aktif   = True
        self.animasi = 0.0
        self.warna      = (255, 215, 0)
        self.warna_rim  = (200, 160, 0)

    def update(self):
        self.animasi  += 0.08
        self.y_render  = self.y + math.sin(self.animasi) * 5

    def gambar(self, surface, kamera_x):
        if not self.aktif:
            return
        x_layar = int(self.x - kamera_x)
        y_layar = int(self.y_render)
        if -30 < x_layar < surface.get_width() + 30:
            pygame.draw.circle(surface, self.warna,    (x_layar, y_layar), self.radius)
            pygame.draw.circle(surface, self.warna_rim,(x_layar, y_layar), self.radius, 3)
            font = pygame.font.SysFont("Arial", 14, bold=True)
            teks = font.render("$", True, (180, 120, 0))
            surface.blit(teks, (x_layar - 5, y_layar - 8))

    def cek_tabrak(self, mobil):
        if not self.aktif:
            return False

        import math as m
        sudut_rad = m.radians(mobil.sudut)

        def rotasi(ox, oy):
            rx = ox * m.cos(sudut_rad) - oy * m.sin(sudut_rad)
            ry = ox * m.sin(sudut_rad) + oy * m.cos(sudut_rad)
            return (mobil.x + rx, mobil.y + ry)

        titik_cek = [
            (mobil.x, mobil.y),
            rotasi( mobil.offset_ban_depan,    0),
            rotasi( mobil.offset_ban_belakang, 0),
            # ✅ BARU: tambah titik tengah-depan dan tengah-belakang body
            rotasi( mobil.lebar // 2,  -mobil.tinggi // 2),
            rotasi(-mobil.lebar // 2,  -mobil.tinggi // 2),
        ]

        # ✅ Perbesar radius dari (radius_ban) jadi +20 ekstra
        radius_gabung = self.radius + mobil.radius_ban + 20

        for (px, py) in titik_cek:
            jarak = m.hypot(self.x - px, self.y_render - py)
            if jarak < radius_gabung:
                return True
        return False

class ManagerKoin:
    def __init__(self, terrain):
        self.terrain      = terrain
        self.semua_koin   = []
        self.total_skor   = 0
        self.efek_popup   = []

    def spawn_koin_awal(self, jumlah=15):
        for i in range(jumlah):
            x = 300 + i * 220 + random.randint(-50, 50)
            y = self.terrain.tinggi_di_x(x) - random.randint(30, 80)
            self.semua_koin.append(Koin(x, y))

    def spawn_koin_baru(self, kamera_x, layar_w):
        batas_kanan = kamera_x + layar_w + 400
        koin_paling_kanan = max(
            (k.x for k in self.semua_koin if k.aktif), default=0
        )
        if koin_paling_kanan < batas_kanan:
            x = batas_kanan + random.randint(0, 200)
            y = self.terrain.tinggi_di_x(x) - random.randint(30, 90)
            self.semua_koin.append(Koin(x, y))

    def update(self, mobil, kamera_x, layar_w):
        """Sekarang terima objek mobil langsung, bukan koordinat saja."""
        koin_diambil = 0
        for koin in self.semua_koin:
            if koin.aktif:
                koin.update()
                # Kirim seluruh objek mobil ke cek_tabrak
                if koin.cek_tabrak(mobil):
                    koin.aktif   = False
                    koin_diambil += koin.nilai
                    self.efek_popup.append({
                        "x": koin.x, "y": koin.y,
                        "alpha": 255, "teks": f"+{koin.nilai}"
                    })

        self.total_skor += koin_diambil

        for efek in self.efek_popup[:]:
            efek["y"]    -= 1.5
            efek["alpha"] -= 8          # ← akan difix di bawah
            if efek["alpha"] <= 0:
                self.efek_popup.remove(efek)

        self.spawn_koin_baru(kamera_x, layar_w)
        self.semua_koin = [k for k in self.semua_koin
                           if k.x > kamera_x - 500]
        return koin_diambil

    def gambar(self, surface, kamera_x):
        for koin in self.semua_koin:
            koin.gambar(surface, kamera_x)
        font = pygame.font.SysFont("Arial", 20, bold=True)
        for efek in self.efek_popup:
            x_layar = int(efek["x"] - kamera_x)
            teks    = font.render(efek["teks"], True, (255, 220, 50))
            teks.set_alpha(max(0, int(efek["alpha"])))
            surface.blit(teks, (x_layar - 10, int(efek["y"])))