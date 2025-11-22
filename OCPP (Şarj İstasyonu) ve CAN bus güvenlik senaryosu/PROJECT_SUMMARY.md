# Proje Özeti

## Proje: OCPP-CAN Bridge Güvenlik Simülasyonu

Bu proje, elektrikli araç şarj istasyonları (Charge Point) ile merkezi yönetim sistemi (CSMS) arasındaki OCPP protokolü ve CAN-bus köprüsünün güvenlik simülasyonudur.

## Proje Yapısı

### Ana Bileşenler

1. **csms_simulator.py** - Merkezi yönetim sistemi simülatörü
   - OCPP WebSocket sunucusu (port 9000)
   - Charge Point'lerle iletişim
   - RemoteStartTransaction, RemoteStopTransaction komutları

2. **cp_simulator.py** - Charge Point simülatörü
   - CSMS'e OCPP ile bağlanır
   - CAN bus üzerinden charger modülü ile iletişim kurar
   - OCPP mesajlarını CAN frame'lerine dönüştürür
   - Compromised firmware modu desteği

3. **can_gateway.py** - OCPP → CAN Gateway
   - OCPP mesajlarını CAN frame'lerine dönüştürür
   - Whitelist filtreleme desteği
   - İstatistik takibi

4. **can_bus_simulator.py** - CAN Bus ve Charger Modülü Simülatörü
   - CAN mesajlarını dinler ve işler
   - Charger modülü davranışını simüle eder
   - MeterValues ve StatusNotification gönderir
   - Malicious frame (0x9FF) tespiti

5. **attack_scenarios.py** - Saldırı Senaryoları
   - MitM Proxy (mesaj manipülasyonu)
   - Compromised firmware simülasyonu
   - Mesaj enjeksiyonu

6. **defense_mechanisms.py** - Savunma Mekanizmaları
   - CAN-IDS (Intrusion Detection System)
   - Gateway whitelist filtreleme
   - Anomali algılama (frekans, zaman aralığı, bilinmeyen ID)

7. **test_scenarios.py** - Test Senaryoları
   - Normal akış testi
   - Saldırı senaryoları
   - İnteraktif komut gönderme
   - CAN trafik izleme

### Yardımcı Dosyalar

- **setup_vcan.sh** - Sanal CAN (vcan0) kurulum scripti
- **quick_start.sh** - Hızlı başlangıç scripti
- **requirements.txt** - Python bağımlılıkları
- **README.md** - Kullanım kılavuzu

## OCPP → CAN Mapping

| OCPP Action | CAN ID | Açıklama |
|------------|--------|----------|
| RemoteStartTransaction | 0x200 | Şarj başlatma |
| RemoteStopTransaction | 0x201 | Şarj durdurma |
| SetChargingProfile | 0x210 | Şarj profili ayarlama |
| MeterValues | 0x300 | Enerji ölçüm değerleri |
| StatusNotification | 0x301 | Durum bildirimi |
| BootNotification | 0x100 | Başlangıç bildirimi |
| Malicious Frame | 0x9FF | Saldırı frame'i (tespit edilmeli) |

## Saldırı Senaryoları

1. **MitM Saldırısı**: Plain WebSocket üzerinden mesaj manipülasyonu
2. **Compromised Firmware**: CP yazılımının ele geçirilmesi, malicious CAN frame gönderimi
3. **Mesaj Enjeksiyonu**: Sahte OCPP mesajlarının enjekte edilmesi

## Savunma Mekanizmaları

1. **Gateway Whitelist**: Sadece izin verilen CAN ID'lerin geçirilmesi
2. **CAN-IDS**: 
   - Bilinmeyen CAN ID tespiti
   - Frekans anomalisi algılama
   - Zaman aralığı anomalisi algılama
   - Malicious frame tespiti

## Kullanım Senaryoları

### Senaryo 1: Normal Akış
1. CSMS başlatılır
2. CP bağlanır ve BootNotification gönderir
3. CSMS RemoteStartTransaction gönderir
4. CP, CAN bus üzerine 0x200 frame'i gönderir
5. Charger modülü şarjı başlatır ve MeterValues gönderir
6. CSMS RemoteStopTransaction gönderir
7. CP, CAN bus üzerine 0x201 frame'i gönderir
8. Charger modülü şarjı durdurur

### Senaryo 2: MitM Saldırısı
1. MitM proxy başlatılır (port 9001)
2. CP, proxy üzerinden CSMS'e bağlanır
3. Proxy, RemoteStartTransaction'ı yakalar ve RemoteStopTransaction'a çevirir
4. CP yanlış komutu alır ve şarjı durdurur

### Senaryo 3: Compromised Firmware
1. CP compromised mode'da başlatılır
2. Normal akış başlar
3. CP, ek olarak malicious frame (0x9FF) gönderir
4. CAN-IDS malicious frame'i tespit eder ve alarm üretir
5. Charger modülü hatalı davranış moduna geçer

## Teknik Detaylar

- **Protokol**: OCPP 1.6 (WebSocket)
- **CAN Bus**: vcan0 (sanal CAN, donanım gerektirmez)
- **Dil**: Python 3
- **Ana Kütüphaneler**: 
  - ocpp (OCPP protokolü)
  - websockets (WebSocket iletişimi)
  - python-can (CAN bus erişimi)

## Güvenlik Notu

⚠️ **ÖNEMLİ**: Bu simülasyon yalnızca eğitim amaçlıdır. Tüm testler izole ağda ve simüle edilmiş cihazlarla yapılmalıdır. Gerçek sistemlere yönelik testler için yazılı izin gereklidir.

## Geliştirme Notları

- Tüm bileşenler asenkron (async/await) çalışır
- Loglama detaylıdır ve tüm mesajlar kaydedilir
- CAN-IDS istatistiksel analiz kullanır
- Gateway whitelist mekanizması esnektir ve özelleştirilebilir

