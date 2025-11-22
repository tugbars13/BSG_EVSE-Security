import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# --- 1. AYARLAR VE VERİ SİMÜLASYONU ---
# Sonuçların her seferinde aynı çıkması için
np.random.seed(42) 
n_samples = 200

# A) Trafik Analizi Verisi (Zaman Serisi)
time_slots = np.arange(0, 50)
# Normal trafik: Dakikada 10-20 arası rastgele sorgu
normal_traffic = np.random.randint(10, 20, size=50)
# Anomali: 30-40. dakikalar arası ani artış (Saldırı)
anomaly_traffic = normal_traffic.copy()
anomaly_traffic[30:40] = np.random.randint(100, 150, size=10) 

# B) Yük Analizi Verisi (Sorgu Uzunluğu)
# Normal: Kısa domainler (Ortalama 15 karakter)
normal_lengths = np.random.normal(loc=15, scale=5, size=n_samples)
# Anomali: Uzun şifreli veri (Ortalama 60 karakter)
anomaly_lengths = np.random.normal(loc=60, scale=10, size=n_samples)

# C) Entropi Verisi (Karmaşıklık)
# Normal: Düşük entropi (2.5)
normal_entropy = np.random.normal(loc=2.5, scale=0.5, size=n_samples)
# Anomali: Yüksek entropi (4.5)
anomaly_entropy = np.random.normal(loc=4.5, scale=0.5, size=n_samples)

# --- 2. GÖRSELLEŞTİRME ---
# Grafik stili ayarı
sns.set_style("darkgrid")

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('DNS Tünelleme (Tunneling) Anomali Tespit Analizi', fontsize=18, fontweight='bold', color='#333333')

# GRAFİK 1: Zaman İçinde Sorgu Hacmi
axes[0, 0].plot(time_slots, anomaly_traffic, color='#d62728', label='Saldırı Trafiği', linewidth=2.5)
axes[0, 0].plot(time_slots, normal_traffic, color='#2ca02c', linestyle='--', label='Normal Baseline', alpha=0.7)
axes[0, 0].set_title('1. Trafik Analizi: Sorgu Hacmi (Spike)', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Zaman (Dakika)')
axes[0, 0].set_ylabel('Sorgu Sayısı')
axes[0, 0].legend(loc='upper left')
axes[0, 0].axvspan(30, 40, color='red', alpha=0.15) # Anomali alanını boya

# GRAFİK 2: Sorgu Uzunluğu Dağılımı
sns.kdeplot(normal_lengths, ax=axes[0, 1], color='green', fill=True, label='Normal (Kısa)')
sns.kdeplot(anomaly_lengths, ax=axes[0, 1], color='red', fill=True, label='Tünelleme (Uzun)')
axes[0, 1].set_title('2. Yük Analizi: Sorgu Uzunluğu', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('Karakter Sayısı')
axes[0, 1].legend()

# GRAFİK 3: Entropi vs Uzunluk
axes[1, 0].scatter(normal_lengths[:50], normal_entropy[:50], color='green', label='Normal', alpha=0.6)
axes[1, 0].scatter(anomaly_lengths[:50], anomaly_entropy[:50], color='red', marker='X', label='Saldırgan', s=60)
axes[1, 0].set_title('3. Karmaşıklık Analizi (Entropi)', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('Uzunluk')
axes[1, 0].set_ylabel('Entropi Değişimi')
axes[1, 0].axhline(y=3.5, color='gray', linestyle='--', label='Eşik Değeri')
axes[1, 0].legend()

# GRAFİK 4: Kayıt Tipleri
record_types = ['A (IPv4)', 'TXT (Veri)', 'AAAA', 'CNAME']
normal_counts = [85, 2, 10, 3]
anomaly_counts = [10, 75, 5, 10]

x = np.arange(len(record_types))
width = 0.35
axes[1, 1].bar(x - width/2, normal_counts, width, label='Normal', color='#2ca02c')
axes[1, 1].bar(x + width/2, anomaly_counts, width, label='Saldırı', color='#d62728')
axes[1, 1].set_title('4. Protokol Analizi: Kayıt Tipleri', fontsize=12, fontweight='bold')
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(record_types)
axes[1, 1].legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
print("Grafikler oluşturuldu. Açılan pencereyi kontrol edin.")
plt.show()
