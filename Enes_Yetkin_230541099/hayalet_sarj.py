import time

# Enes Yetkin - 230541099
# Bilgi Sistemleri ve Güvenliği Proje Ödevi
# Konu: Şarj İstasyonu Anomali Tespiti (Ghost Charging)

print(f"[{time.strftime('%H:%M:%S')}] Güvenlik Modülü Başlatılıyor...")
print("Senaryo: Hayalet Şarj (Ghost Charging) Tespiti")

# Başlangıç Durumu
transaction_status = "Stopped" # Yazılım: Şarj bitti diyor
current_sensor = 31.5          # Fiziksel: Kablodan hala akım geçiyor (ANOMALİ)

print(f"Durum: {transaction_status}")
print(f"Sensör Okuması: {current_sensor} Amper")
time.sleep(1)

if transaction_status == "Stopped" and current_sensor > 0:
    print("\n!!! KRİTİK UYARI !!!")
    print("Hayalet Şarj Tespit Edildi! (Yazılım durdu ama akım devam ediyor)")
    print("Acil durum protokolü devreye alındı.")
else:
    print("Sistem Normal.")
