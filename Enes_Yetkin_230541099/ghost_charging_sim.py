import pandas as pd
import matplotlib.pyplot as plt
import random
import time

# --- ENES YETKİN - 230541099 ---
# GHOST CHARGING ANOMALİ SİMÜLASYONU

def generate_charging_session():
    print("Simülasyon başlatılıyor...")
    data = []
    
    # 0 ile 20. dakikalar arası simülasyon
    for minute in range(0, 25):
        timestamp = f"2025-11-23 14:{minute:02d}:00"
        
        # SENARYO:
        # Dakika 0-5: Araç bağlanıyor (Idle)
        # Dakika 5-15: Şarj oluyor (Active)
        # Dakika 15: KULLANICI DURDURUYOR (Stop Command)
        # Dakika 15-25: ANOMALİ! Yazılım durdu sanıyor ama elektrik akıyor.
        
        if minute < 5:
            software_status = "Connected"
            relay_status = 0 # Açık (Akım yok)
            current_amps = random.uniform(0.0, 0.5) # Gürültü
            
        elif 5 <= minute < 15:
            software_status = "Charging"
            relay_status = 1 # Kapalı (Akım var)
            current_amps = random.uniform(31.5, 32.5) # 32A civarı
            
        else: # Dakika 15 ve sonrası (KRİTİK AN)
            software_status = "Stopped" 
            # NORMALDE relay_status 0 olmalıydı.
            # AMA ANOMALİ VAR: Röle yapıştı!
            relay_status = 1 
            current_amps = random.uniform(31.0, 32.0) # Akım hala akıyor!

        # Veriyi kaydet
        data.append({
            "Time": minute,
            "Timestamp": timestamp,
            "Software_State": software_status,
            "Relay_Physical_State": "STUCK_CLOSED" if (minute >= 15) else ("CLOSED" if relay_status else "OPEN"),
            "Current_Amps": current_amps,
            "Anomaly_Detected": 1 if (software_status == "Stopped" and current_amps > 10) else 0
        })

    return pd.DataFrame(data)

# Veriyi Üret
df = generate_charging_session()

# --- 1. ÇIKTI: LOG DOSYASI OLUŞTUR (CSV) ---
df.to_csv("ghost_charging_logs.csv", index=False)
print("Log dosyası oluşturuldu: ghost_charging_logs.csv")

# --- 2. ÇIKTI: GRAFİK ÇİZ (Görsel Kanıt) ---
plt.figure(figsize=(12, 6))

# Grafik 1: Akım Değeri (Amper)
plt.plot(df['Time'], df['Current_Amps'], label='Fiziksel Akım (Amper)', color='red', linewidth=3)

# Grafik 2: Anomali Bölgesini Boya
plt.axvspan(15, 24, color='yellow', alpha=0.3, label='ANOMALİ BÖLGESİ (Ghost Charging)')

# İşaretler
plt.axvline(x=15, color='black', linestyle='--', label='Yazılım "DUR" Komutu')
plt.text(15.5, 15, 'Yazılım Durdurdu\nAMA Akım Devam Ediyor!', color='red', fontweight='bold')

plt.title('Hayalet Şarj (Ghost Charging) Simülasyonu - Enes Yetkin', fontsize=14)
plt.xlabel('Zaman (Dakika)')
plt.ylabel('Akım Şiddeti (Amper)')
plt.legend()
plt.grid(True)

# Grafiği Kaydet
plt.savefig("ghost_charging_graph.png")
print("Grafik oluşturuldu: ghost_charging_graph.png")
plt.show()
