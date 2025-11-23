import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# ================================================================
# 1) ZAMAN EKSENİ OLUŞTURMA
#    - fs: örnekleme frekansı (Hz)
#    - t : sinyalin zaman çizelgesi (2 saniyelik örnek)
# ================================================================
fs = 2000
t = np.linspace(0, 2, fs*2)


# ================================================================
# 2) NORMAL ENERJİ ŞEBEKE SİNYALİ (50 Hz)
#    - Elektrik şebekesinde temel frekans 50 Hz’dir
#    - 5V genlikli bir sinüs sinyali simüle ediliyor
# ================================================================
normal_freq = 50
normal_load = 5 * np.sin(2 * np.pi * normal_freq * t)


# ================================================================
# 3) EMLR SALDIRI SİNYALİ OLUŞTURMA
#    - "Electro-Mimetic Load Resonance" saldırısı, yüksek frekanslı
#      rezonans dalgalarını normal yük davranışına gizleyerek yapılır.
#    - Saldırı, sinyalin yalnızca belirli bir bölümünde aktif olacak.
# ================================================================

attack_start = int(len(t) * 0.6)   # Saldırının başladığı zaman
attack_end   = int(len(t) * 0.9)   # Saldırının bittiği zaman

# Saldırı için boş bir sinyal oluştur
emlr_signal = np.zeros_like(t)

# EMLR'nin sahte rezonans frekansları
# Bunlar normal şebekede asla oluşmayan harmoniklerdir
resonance_freqs = [150, 350, 760]

# Rezonans sinyallerini zaman aralığında ekle
for f in resonance_freqs:
    emlr_signal[attack_start:attack_end] += 1.7 * np.sin(2 * np.pi * f * t[attack_start:attack_end])


# ================================================================
# 4) TOPLAM SİNYAL (Normal + EMLR)
#    - Gerçek sistemde olduğu gibi saldırı normal sinyale karışıyor
# ================================================================
total_signal = normal_load + emlr_signal


# ================================================================
# 5) FFT (FREQUENCY ANALYSIS)
#    - Anomali tespitinde kullanılan en güçlü yöntemlerden biri
#    - FFT ile sinyalin frekans bileşenleri çıkarılıyor
# ================================================================
fft_vals = np.abs(np.fft.rfft(total_signal))
fft_freqs = np.fft.rfftfreq(len(total_signal), 1/fs)

# Anormal frekansları otomatik tespit et (eşik: height=100)
peaks, _ = find_peaks(fft_vals, height=100)


# ================================================================
# 6) GÖRSELLEŞTİRME
#    - Üst grafik: zaman domeni (normal + saldırı)
#    - Alt grafik: frekans domeni (FFT)
# ================================================================
plt.figure(figsize=(15, 10))

# --- ZAMAN DOMENİ ---
plt.subplot(2,1,1)
plt.plot(t, total_signal, label="Total Signal (Normal + EMLR)")
plt.axvspan(t[attack_start], t[attack_end], color='red', alpha=0.2, label="EMLR Attack Window")
plt.title("EMLR Attack Simulation - Time Domain")
plt.xlabel("Time (sec)")
plt.ylabel("Amplitude")
plt.legend()

# --- FREKANS DOMENİ ---
plt.subplot(2,1,2)
plt.plot(fft_freqs, fft_vals, label="FFT Spectrum")
plt.scatter(fft_freqs[peaks], fft_vals[peaks], color='red', label="Detected Resonance Peaks")
plt.title("FFT Analysis - Resonance Detection")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power")
plt.legend()

plt.tight_layout()
plt.show()


# ================================================================
# 7) ANOMALİ FREKANSLARINI RAPORLA
# ================================================================
print("Detected Anomalous Frequencies:")
for p in peaks:
    print(f"  - {fft_freqs[p]:.2f} Hz")
