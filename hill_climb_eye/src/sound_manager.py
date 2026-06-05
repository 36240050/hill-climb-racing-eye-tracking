# src/sound_manager.py — Fixed: stereo-compatible

import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.volume = 0.5

        self.suara_koin     = self._buat_suara_koin()
        self.suara_engine   = self._buat_suara_engine()
        self.suara_gameover = self._buat_suara_gameover()
        self.suara_bensin = self._buat_suara_bensin()
        self.channel_engine = pygame.mixer.Channel(0)

    def _ke_stereo(self, mono):
        """Ubah array 1D mono → 2D stereo (wajib untuk pygame mixer stereo)."""
        return np.column_stack((mono, mono))

    def _buat_gelombang(self, frekuensi, durasi, volume=0.5, bentuk="sine"):
        sample_rate = 44100
        n           = int(sample_rate * durasi)
        t           = np.linspace(0, durasi, n, False)

        if bentuk == "sine":
            g = np.sin(2 * np.pi * frekuensi * t)
        elif bentuk == "square":
            g = np.sign(np.sin(2 * np.pi * frekuensi * t))
        elif bentuk == "sawtooth":
            g = 2 * (t * frekuensi - np.floor(t * frekuensi + 0.5))
        else:
            g = np.sin(2 * np.pi * frekuensi * t)

        fade = np.linspace(1, 0, n // 4)
        g[-len(fade):] *= fade
        mono = (g * volume * 32767).astype(np.int16)
        return self._ke_stereo(mono)

    def _buat_suara_koin(self):
        sample_rate = 44100
        durasi      = 0.15
        n           = int(sample_rate * durasi)
        t           = np.linspace(0, durasi, n, False)

        nada1    = np.sin(2 * np.pi * 1200 * t) * 0.5
        nada2    = np.sin(2 * np.pi * 1600 * t) * 0.3
        envelope = np.exp(-t * 20)
        mono     = ((nada1 + nada2) * envelope * 32767).astype(np.int16)

        suara = pygame.sndarray.make_sound(self._ke_stereo(mono))
        suara.set_volume(self.volume)
        return suara

    def _buat_suara_engine(self):
        data  = self._buat_gelombang(80, 0.5, volume=0.3, bentuk="sawtooth")
        suara = pygame.sndarray.make_sound(data)
        suara.set_volume(0.2)
        return suara

    def _buat_suara_gameover(self):
        sample_rate = 44100
        durasi      = 0.8
        n           = int(sample_rate * durasi)
        t           = np.linspace(0, durasi, n, False)

        frek_turun = 400 * np.exp(-t * 2)
        envelope   = np.exp(-t * 1.5)
        mono       = (np.sin(2 * np.pi * frek_turun * t) * envelope * 0.5 * 32767).astype(np.int16)

        suara = pygame.sndarray.make_sound(self._ke_stereo(mono))
        suara.set_volume(self.volume)
        return suara
    
    # src/sound_manager.py — tambah fungsi baru ini

    def _buat_suara_bensin(self):
        """
        Suara 'glug glug' saat ambil jerry can.
        Efek: dua nada rendah berurutan, kayak suara cairan tuang.
        """
        sample_rate = 44100
        durasi      = 0.4
        n           = int(sample_rate * durasi)
        t           = np.linspace(0, durasi, n, False)

        # Dua gelombang nada rendah bergantian
        nada1    = np.sin(2 * np.pi * 280 * t) * np.exp(-t * 8)
        nada2    = np.sin(2 * np.pi * 220 * t) * np.exp(-(t - 0.2) * 8)
        nada2   *= (t > 0.15).astype(float)   # nada2 mulai setelah 0.15 detik

        mono = ((nada1 + nada2) * 0.6 * 32767).astype(np.int16)
        suara = pygame.sndarray.make_sound(self._ke_stereo(mono))
        suara.set_volume(self.volume)
        return suara

    def mainkan_bensin(self):
        self.suara_bensin.play()

    def mainkan_koin(self):
        self.suara_koin.play()

    def update_engine(self, kecepatan_mobil):
        if kecepatan_mobil > 0.5:
            if not self.channel_engine.get_busy():
                self.channel_engine.play(self.suara_engine, loops=-1)
            self.channel_engine.set_volume(min(0.4, kecepatan_mobil / 20.0))
        else:
            self.channel_engine.fadeout(200)

    def mainkan_gameover(self):
        self.channel_engine.stop()
        self.suara_gameover.play()