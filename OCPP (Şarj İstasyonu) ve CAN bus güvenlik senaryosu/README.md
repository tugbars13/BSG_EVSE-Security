# OCPP-CAN Bridge Güvenlik Simülasyonu
## Elektrikli Araç Şarj İstasyonlarında Ağ ve Fiziksel Katman Köprüsü Güvenlik Analizi

---

## 📋 İçindekiler

1. [Özet](#özet)
2. [Giriş ve Amaç](#giriş-ve-amaç)
3. [Problem Tanımı ve Tehdit Modeli](#problem-tanımı-ve-tehdit-modeli)
4. [Sistem Mimarisi](#sistem-mimarisi)
5. [Teknik Detaylar](#teknik-detaylar)
6. [Saldırı Senaryoları](#saldırı-senaryoları)
7. [Savunma Mekanizmaları](#savunma-mekanizmaları)
8. [Kurulum Kılavuzu](#kurulum-kılavuzu)
9. [Kullanım Senaryoları](#kullanım-senaryoları)
10. [Test ve Değerlendirme](#test-ve-değerlendirme)
11. [Sonuç ve Öneriler](#sonuç-ve-öneriler)
12. [Güvenlik ve Etik Notları](#güvenlik-ve-etik-notları)
13. [Referanslar](#referanslar)

---

## 📝 Özet

Bu proje, elektrikli araç şarj istasyonları (Electric Vehicle Supply Equipment - EVSE) ve merkezi yönetim sistemleri (Central System Management System - CSMS) arasındaki OCPP (Open Charge Point Protocol) protokolü ile CAN-bus (Controller Area Network) köprüsünün güvenlik açıklarını analiz eden kapsamlı bir simülasyon ortamıdır.

Proje, IoT (Internet of Things) ve otomotiv güvenliği alanlarının kesişim noktasında yer alan kritik bir güvenlik sorununu ele almaktadır: **Ağ katmanındaki (OCPP) güvenlik zafiyetlerinin fiziksel cihaz kontrolüne (CAN-bus) dönüşme riski**. Bu çalışma, eğitim amaçlı olarak tasarlanmış bir laboratuvar ortamında gerçek saldırı ve savunma senaryolarını simüle etmektedir.

### Temel Bulgular

- **Tehdit Senaryoları**: MitM (Man-in-the-Middle) saldırıları, firmware compromise, mesaj manipülasyonu ve CAN frame enjeksiyonu
- **Savunma Mekanizmaları**: Gateway whitelist filtreleme, CAN-IDS (Intrusion Detection System), anomali algılama algoritmaları
- **Pratik Çıktılar**: Eğitim amaçlı simülasyon ortamı, test senaryoları ve güvenlik farkındalığı kazandırma araçları

---

## 🎯 Giriş ve Amaç

### Proje Kapsamı

Elektrikli araç şarj altyapısı, modern ulaşım sistemlerinin kritik bir parçasıdır. Bu altyapıda, şarj istasyonları (Charge Point - CP) merkezi bir yönetim sistemi (CSMS) ile OCPP protokolü üzerinden iletişim kurmaktadır. Ancak, CP içerisinde bulunan kontrol birimleri (power electronics, metering, relay kontrol, kullanıcı arayüzü) arasındaki iletişim CAN-bus protokolü ile sağlanmaktadır.

Bu iki protokol arasındaki **köprü yapısı**, potansiyel bir güvenlik açığı oluşturmaktadır: Bir saldırgan, OCPP kanalındaki zafiyetleri kullanarak (ör. zayıf şifreleme, MitM saldırıları), CP üzerindeki yazılımı manipüle ederek CAN-bus üzerinden fiziksel cihaz kontrolüne erişebilir.

### Proje Amaçları

1. **Güvenlik Açıklarının Tespiti**: OCPP-CAN köprüsündeki potansiyel güvenlik zafiyetlerini belirlemek
2. **Saldırı Senaryolarının Simülasyonu**: Gerçekçi saldırı senaryolarını güvenli bir ortamda simüle etmek
3. **Savunma Mekanizmalarının Geliştirilmesi**: Etkili savunma stratejileri önermek ve uygulamak
4. **Eğitim ve Farkındalık**: IoT ve otomotiv güvenliği konularında eğitim materyali sağlamak

---

## 🔒 Problem Tanımı ve Tehdit Modeli

### Mantıksal İlişki ve Köprü Yapısı

**OCPP Protokolü:**
- Şarj istasyonu (Charge Point) ile merkezi yönetim (CSMS) arasındaki ağ protokolü
- WebSocket üzerinden JSON tabanlı mesajlaşma
- Uzaktan kontrol, durum izleme ve fatura entegrasyonu sağlar

**CAN-bus Protokolü:**
- CP içindeki kontrol birimleri arasındaki lokal haberleşme protokolü
- Power electronics, metering, relay kontrol ve kullanıcı arayüzü modülleri arasında iletişim
- Düşük seviyeli, gerçek zamanlı kontrol mesajları içerir

**Köprü Problemi:**
Bir saldırgan OCPP kanalını ele geçirirse (ör. zayıf şifreleme/MitM), CP üzerindeki yazılımı manipüle ederek CAN-bus üzerinden yerel kontrol mesajları gönderebilir veya değiştirebilir. Bu durumda OCPP zafiyetleri fiziksel işlem/cihaz kontrolü ile sonuçlanabilir:
- Şarjı kesme/başlatma
- Güç parametrelerini değiştirme
- Ölçüm manipülasyonu (faturalama hilesi)

### Tehdit Modeli

#### 1. Uzaktan Komut Taklidi
**Tehdit**: Saldırgan, CSMS'e sahte `RemoteStartTransaction` veya `RemoteStopTransaction` mesajları gönderir. CP bu komutu CAN aracılığıyla gerçek röle/şarj kontrol modülüne iletir.

**Etki**: İzinsiz şarj başlatma/durdurma, kullanıcı deneyimi bozulması

#### 2. Mesaj Değiştirme / MitM Saldırısı
**Tehdit**: Zayıf TLS/WebSocket ile trafiği yakalayıp OCPP mesajlarını değiştirerek CP'ye hatalı parametreler gönderme.

**Etki**: Şarj parametrelerinin manipülasyonu, güvenli olmayan çalışma koşulları

#### 3. Firmware/Konfigürasyon Enjeksiyonu
**Tehdit**: Zayıf kimlik doğrulama varsa CP'ye zararlı firmware gönderilip CAN seviyesinde davranış değiştirilir.

**Etki**: Kalıcı sistem compromise, arka kapı yerleştirme

#### 4. CAN Frame Enjeksiyonu
**Tehdit**: CP'nin yazılımı ele geçirilmişse, CP içinden CAN üzerinde sahte/ani frame'ler üretilerek bağlı cihazlar karıştırılır.

**Etki**: Cihaz arızaları, güvenlik mekanizmalarının bypass edilmesi

#### 5. Sensör/Veri Manipülasyonu
**Tehdit**: `MeterValues` gibi enerji ölçümlerini değiştirme.

**Etki**: Faturalama hilesi, mali zarar

### Köprü Bileşenleri

Projede simüle edilen kritik bileşenler:

- **CP Main Controller (MCU/SoC)**: OCPP agent burada çalışır ve CAN transceiver ile arabirim kurar
- **Gateway Bileşeni**: OCPP → application logic → CAN frame mapping (örn: `RemoteStopTransaction` → CAN ID `0x201`)
- **HSM/Secure Element**: Güvenli anahtar yönetimi (yoksa risk artar)

---

## 🏗️ Sistem Mimarisi

### Bileşen Diyagramı

```
┌─────────────┐         OCPP (WebSocket)         ┌─────────────┐
│             │  ←──────────────────────────────→ │             │
│     CSMS    │                                    │      CP     │
│  (Central   │                                    │  (Charge    │
│  System)    │                                    │   Point)    │
│             │                                    │             │
└─────────────┘                                    └──────┬──────┘
                                                           │
                                                           │ CAN Gateway
                                                           │ OCPP → CAN
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │   CAN Bus       │
                                                  │   (vcan0)       │
                                                  └────────┬────────┘
                                                           │
                                                           │ CAN Frames
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ Charger Module  │
                                                  │ (Simulated)     │
                                                  └─────────────────┘
```

### Ana Bileşenler

#### 1. CSMS Simülatörü (`csms_simulator.py`)
**Görev**: Merkezi yönetim sistemi simülasyonu
- OCPP 1.6 WebSocket sunucusu (port 9000)
- Charge Point'lerle iletişim kurma
- RemoteStartTransaction, RemoteStopTransaction komutları
- StatusNotification, MeterValues mesajlarını alma
- BootNotification işleme

**Özellikler**:
- Asenkron WebSocket server
- OCPP mesaj routing ve handling
- Çoklu Charge Point desteği

#### 2. Charge Point Simülatörü (`cp_simulator.py`)
**Görev**: Şarj istasyonu simülasyonu
- CSMS'e OCPP ile bağlanma
- CAN bus üzerinden charger modülü ile iletişim
- OCPP mesajlarını CAN frame'lerine dönüştürme
- CAN'dan gelen mesajları OCPP'ye dönüştürme

**Özellikler**:
- OCPP-CAN köprü fonksiyonu
- Compromised firmware modu (saldırı simülasyonu için)
- Çoklu connector desteği
- Transaction yönetimi

#### 3. CAN Gateway (`can_gateway.py`)
**Görev**: Protokol dönüşümü ve filtreleme
- OCPP mesajlarını CAN frame'lerine dönüştürme
- CAN frame'lerini OCPP mesajlarına dönüştürme
- Whitelist filtreleme (savunma mekanizması)
- İstatistik takibi

**Mapping Tablosu**:
| OCPP Action | CAN ID | Payload Format |
|------------|--------|----------------|
| RemoteStartTransaction | 0x200 | [cp_id, connector_id, start_cmd] |
| RemoteStopTransaction | 0x201 | [tx_id, stop_cmd] |
| SetChargingProfile | 0x210 | [profile_id, max_current] |
| MeterValues | 0x300 | [connector_id, energy, timestamp] |
| StatusNotification | 0x301 | [connector_id, status] |
| BootNotification | 0x100 | [cp_id, model] |

#### 4. CAN Bus Simülatörü (`can_bus_simulator.py`)
**Görev**: CAN bus ve charger modülü simülasyonu
- CAN mesajlarını dinleme ve işleme
- Charger modülü davranışını simüle etme
- MeterValues ve StatusNotification gönderme
- Malicious frame (0x9FF) tespiti ve hatalı davranış

**Özellikler**:
- Gerçek zamanlı CAN trafik simülasyonu
- Enerji ölçümü simülasyonu
- Transaction yönetimi
- Hata durumu simülasyonu

#### 5. Saldırı Senaryoları Modülü (`attack_scenarios.py`)
**Görev**: Güvenlik testleri ve saldırı simülasyonu
- MitM Proxy (mesaj manipülasyonu)
- Compromised firmware simülasyonu
- Mesaj enjeksiyonu

**Saldırı Modları**:
- `modify_stop`: RemoteStartTransaction → RemoteStopTransaction
- `modify_start`: RemoteStopTransaction → RemoteStartTransaction
- `inject_fake`: Sahte mesaj enjeksiyonu

#### 6. Savunma Mekanizmaları Modülü (`defense_mechanisms.py`)
**Görev**: Güvenlik savunma stratejileri
- CAN-IDS (Intrusion Detection System)
- Gateway whitelist filtreleme
- Anomali algılama (frekans, zaman aralığı, bilinmeyen ID)

**CAN-IDS Özellikleri**:
- İstatistiksel analiz
- Frekans anomalisi tespiti
- Zaman aralığı anomalisi tespiti
- Bilinmeyen CAN ID tespiti
- Malicious frame (0x9FF) tespiti

---

## 🔧 Teknik Detaylar

### Protokol Detayları

**OCPP (Open Charge Point Protocol) 1.6:**
- WebSocket üzerinden JSON-RPC 2.0
- Asenkron mesajlaşma
- Heartbeat mekanizması
- Transaction yönetimi

**CAN-bus (Controller Area Network):**
- Sanal CAN arayüzü (vcan0) - donanım gerektirmez
- 11-bit standard ID formatı
- 8-byte payload limiti
- Broadcast mesajlaşma

### Teknoloji Yığını

- **Programlama Dili**: Python 3.8+
- **Asenkron Framework**: asyncio
- **Ana Kütüphaneler**:
  - `ocpp` (v0.20.0+): OCPP protokol implementasyonu
  - `websockets` (v12.0+): WebSocket iletişimi
  - `python-can` (v4.3.0+): CAN bus erişimi
  - `cantools` (v39.0.0+): CAN mesaj decode/encode (opsiyonel)
  - `aiohttp`: HTTP/WebSocket desteği

### Sistem Gereksinimleri

**Yazılım:**
- Linux işletim sistemi (Ubuntu 20.04+ önerilir)
- Python 3.8 veya üzeri
- pip paket yöneticisi
- virtualenv (önerilir)

**Donanım:**
- Minimum: Herhangi bir Linux sistem (VM yeterli)
- Sanal CAN (vcan0) kullanımı - fiziksel donanım gerektirmez
- Opsiyonel: USB-CAN adaptör (Peak, Kvaser, PCAN) - gerçek hardware testleri için

### Mimari Tasarım İlkeleri

1. **Modüler Yapı**: Her bileşen bağımsız çalışabilir
2. **Asenkron İşlem**: Tüm bileşenler async/await kullanır
3. **Genişletilebilirlik**: Yeni saldırı/savunma senaryoları kolayca eklenebilir
4. **Loglama**: Detaylı loglama ve mesaj takibi
5. **Güvenlik**: Tüm testler izole ortamda yapılır

---

## ⚔️ Saldırı Senaryoları

### Senaryo 1: MitM (Man-in-the-Middle) Saldırısı

**Amaç**: OCPP trafiğini yakalama ve mesaj manipülasyonu

**Adımlar**:
1. MitM proxy başlatılır (port 9001)
2. CP, proxy üzerinden CSMS'e bağlanır
3. CSMS'den `RemoteStartTransaction` gönderilir
4. Proxy mesajı yakalar ve `RemoteStopTransaction`'a çevirir
5. CP yanlış komutu alır ve şarjı durdurur

**Simülasyon Komutları**:
```bash
# Terminal 1: CSMS
python3 csms_simulator.py

# Terminal 2: MitM Proxy
python3 attack_scenarios.py --scenario 1

# Terminal 3: CP (proxy üzerinden)
python3 cp_simulator.py CP001 ws://localhost:9001

# Terminal 4: CAN Bus
python3 can_bus_simulator.py
```

**Gözlemlenen Davranış**:
- Proxy loglarında mesaj manipülasyonu görülür
- CP, şarj başlatma yerine durdurma komutu alır
- CAN bus üzerinde beklenmeyen trafik oluşur

### Senaryo 2: Compromised Firmware

**Amaç**: CP yazılımının ele geçirilmesi simülasyonu

**Adımlar**:
1. CP compromised mode'da başlatılır (`--compromised` flag)
2. Normal akış başlar
3. CP, normal mesajlara ek olarak malicious CAN frame (0x9FF) gönderir
4. CAN-IDS malicious frame'i tespit eder ve alarm üretir
5. Charger modülü hatalı davranış moduna geçer

**Simülasyon Komutları**:
```bash
# Terminal 1: CSMS
python3 csms_simulator.py

# Terminal 2: CP (compromised mode)
python3 cp_simulator.py CP001 ws://localhost:9000 --compromised

# Terminal 3: CAN Bus
python3 can_bus_simulator.py

# Terminal 4: CAN-IDS (savunma)
python3 defense_mechanisms.py --ids
```

**Gözlemlenen Davranış**:
- CAN-IDS loglarında malicious frame alarmı
- Charger modülü anormal davranış gösterir
- Sistem güvenlik mekanizması devreye girer

### Senaryo 3: Mesaj Enjeksiyonu

**Amaç**: Sahte OCPP mesajlarının enjekte edilmesi

**Adımlar**:
1. MitM proxy, mesaj enjeksiyonu modunda başlatılır
2. BootNotification'dan sonra sahte `RemoteStartTransaction` enjekte edilir
3. CP sahte komutu alır ve işler

**Etki**: İzinsiz şarj başlatma denemesi

---

## 🛡️ Savunma Mekanizmaları

### 1. Gateway Whitelist Filtreleme

**Prensip**: OCPP'den gelen komutların yalnızca izin verilen CAN ID/payload formatına dönüştürülmesi

**Uygulama**:
- Gateway, sadece whitelist'teki CAN ID'lere izin verir
- Malicious frame'ler (örn: 0x9FF) otomatik olarak engellenir
- İstatistik takibi ile bloke edilen mesajlar loglanır

**Kullanım**:
```python
from can_gateway import SecureGateway

gateway = SecureGateway()
gateway.enable_whitelist({0x200, 0x201, 0x210, 0x300, 0x301})
```

**Etkililik**: 
- Bilinen malicious ID'leri %100 engeller
- Payload formatı kontrolü ile ek güvenlik sağlar

### 2. CAN-IDS (Intrusion Detection System)

**Prensip**: İstatistiksel analiz ile anomali algılama

**Algılama Metrikleri**:

1. **Bilinmeyen CAN ID Tespiti**
   - Normal ID'ler: {0x200, 0x201, 0x210, 0x300, 0x301, 0x100}
   - Bilinmeyen ID'ler alarm üretir

2. **Frekans Anomalisi Algılama**
   - Aynı CAN ID'nin yüksek frekansla gönderilmesi
   - Eşik değer: %50'den fazla aynı ID

3. **Zaman Aralığı Anomalisi Algılama**
   - 3-sigma kuralı ile zaman aralığı analizi
   - Beklenmeyen zamanlarda gelen mesajlar

4. **Malicious Frame Tespiti**
   - 0x9FF gibi bilinen malicious ID'ler
   - Anında alarm üretimi

**Kullanım**:
```bash
python3 defense_mechanisms.py --ids
```

**İstatistikler**:
- Toplam mesaj sayısı
- Farklı CAN ID sayısı
- Toplam alarm sayısı
- En sık görülen ID'ler
- Son alarmlar

### 3. Mutual TLS ve Güçlü Anahtar Yönetimi

**Prensip**: OCPP kanalının kriptografik olarak korunması

**Uygulama**: 
- WSS (WebSocket Secure) kullanımı
- Mutual TLS ile kimlik doğrulama
- Güçlü anahtar yönetimi protokolleri

**Not**: Bu projede simüle edilmemiştir, ancak gerçek sistemlerde kritiktir.

### 4. CAN Segregasyonu

**Prensip**: Kritik CAN segmentlerini yalnızca güvenilir donanımla bağlamak

**Uygulama**:
- Yönetim trafiği ile kontrol trafiğinin ayrılması
- Fiziksel veya mantıksal ağ segmentasyonu

### 5. Uçta Doğrulama (MAC/HMAC)

**Prensip**: CAN uygulama katmanında mesaj düzeyinde doğrulama

**Uygulama**:
- Her CAN frame'e MAC (Message Authentication Code) eklenmesi
- HMAC ile mesaj bütünlüğü kontrolü

---

## 📦 Kurulum Kılavuzu

### Adım 1: Sistem Gereksinimlerini Kontrol Edin

```bash
# Python versiyonunu kontrol edin
python3 --version  # 3.8+ olmalı

# pip yüklü mü kontrol edin
pip3 --version
```

### Adım 2: Bağımlılıkları Yükleyin

```bash
# Proje dizinine gidin
cd /home/ffurkan/Belgeler/new1

# Virtual environment oluşturun (önerilir)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

**Gerekli Paketler**:
- `ocpp>=0.20.0`: OCPP protokol desteği
- `websockets>=12.0`: WebSocket iletişimi
- `aiohttp>=3.9.0`: Asenkron HTTP/WebSocket
- `python-can>=4.3.0`: CAN bus erişimi
- `cantools>=39.0.0`: CAN mesaj araçları (opsiyonel)

### Adım 3: Sanal CAN Arayüzünü Oluşturun

**Otomatik Kurulum**:
```bash
sudo ./setup_vcan.sh
```

**Manuel Kurulum**:
```bash
# vcan modülünü yükle
sudo modprobe vcan

# vcan0 arayüzünü oluştur
sudo ip link add dev vcan0 type vcan

# vcan0 arayüzünü aktif et
sudo ip link set up vcan0

# Durumu kontrol et
ip link show vcan0
```

**Kontrol**:
```bash
# vcan0'ın UP durumunda olduğunu kontrol edin
ip link show vcan0 | grep UP
```

### Adım 4: Kurulumu Test Edin

```bash
# Python importlarını test edin
python3 -c "import ocpp, websockets, can; print('Tüm modüller yüklü!')"

# vcan0 erişimini test edin
python3 -c "import can; bus = can.interface.Bus('vcan0', bustype='socketcan'); print('CAN bus hazır!')"
```

---

## 🚀 Kullanım Senaryoları

### Senaryo A: Normal Akış Testi

**Amaç**: Sistemin normal çalışma akışını gözlemleme

**Adımlar**:

1. **Terminal 1 - CSMS Başlat**:
```bash
python3 csms_simulator.py
```
Beklenen çıktı:
```
INFO:__main__:CSMS Simülatörü başlatılıyor...
INFO:__main__:WebSocket sunucusu: ws://localhost:9000
INFO:websockets.server:server listening on 127.0.0.1:9000
INFO:__main__:CSMS hazır! Charge Point bağlantılarını bekliyor...
```

2. **Terminal 2 - CP Başlat**:
```bash
python3 cp_simulator.py CP001
```
Beklenen çıktı:
```
INFO: Charge Point Simülatörü başlatılıyor...
INFO: CP ID: CP001
INFO: CSMS URL: ws://localhost:9000
INFO: [CP001] BootNotification gönderiliyor...
```

3. **Terminal 3 - CAN Bus Başlat**:
```bash
python3 can_bus_simulator.py
```
Beklenen çıktı:
```
INFO: CAN Bus Simülatörü başlatıldı: vcan0
INFO: Charger modülü hazır ve CAN mesajlarını dinliyor...
```

**Gözlemlenen Akış**:
1. CP, CSMS'e BootNotification gönderir
2. CSMS yanıt verir (Accepted)
3. CSMS RemoteStartTransaction gönderir
4. CP, CAN bus üzerine 0x200 frame'i gönderir
5. Charger modülü şarjı başlatır ve MeterValues (0x300) gönderir
6. CP, CSMS'e MeterValues iletir
7. CSMS RemoteStopTransaction gönderir
8. CP, CAN bus üzerine 0x201 frame'i gönderir
9. Charger modülü şarjı durdurur

### Senaryo B: MitM Saldırısı Testi

**Amaç**: Mesaj manipülasyonu saldırısını gözlemleme

**Adımlar**:

1. **Terminal 1 - CSMS**:
```bash
python3 csms_simulator.py
```

2. **Terminal 2 - MitM Proxy**:
```bash
python3 attack_scenarios.py --scenario 1
```
Beklenen çıktı:
```
INFO: MitM Proxy başlatılıyor...
INFO: Listen: ws://localhost:9001
INFO: Attack Mode: modify_stop
WARNING: ⚠️ Bu bir saldırı simülasyonudur - yalnızca eğitim amaçlıdır!
```

3. **Terminal 3 - CP (Proxy Üzerinden)**:
```bash
python3 cp_simulator.py CP001 ws://localhost:9001
```

4. **Terminal 4 - CAN Bus**:
```bash
python3 can_bus_simulator.py
```

**Test Komutu Gönder**:
```bash
python3 test_scenarios.py --interactive
```

**Gözlemlenen Davranış**:
- Proxy loglarında mesaj manipülasyonu görülür
- RemoteStartTransaction → RemoteStopTransaction'a dönüşür
- CP yanlış komutu alır ve şarjı durdurur

### Senaryo C: Compromised Firmware Testi

**Amaç**: Firmware compromise ve CAN-IDS algılamasını test etme

**Adımlar**:

1. **Terminal 1 - CSMS**:
```bash
python3 csms_simulator.py
```

2. **Terminal 2 - CP (Compromised Mode)**:
```bash
python3 cp_simulator.py CP001 ws://localhost:9000 --compromised
```

3. **Terminal 3 - CAN Bus**:
```bash
python3 can_bus_simulator.py
```

4. **Terminal 4 - CAN-IDS**:
```bash
python3 defense_mechanisms.py --ids
```

**Gözlemlenen Davranış**:
- CP, ek olarak malicious CAN frame (0x9FF) gönderir
- CAN-IDS, malicious frame'i tespit eder ve alarm üretir:
```
🚨 ALARM [MALICIOUS_FRAME]: Malicious CAN frame tespit edildi: 0x9ff
```
- Charger modülü hatalı davranış moduna geçer

### Senaryo D: Savunma Mekanizmaları Karşılaştırması

**Amaç**: Güvenli ve güvensiz gateway'in farkını gösterme

```bash
python3 defense_mechanisms.py --compare
```

**Gösterilen Farklar**:
- Güvensiz Gateway: Tüm CAN ID'lere izin verir (malicious frame'ler geçer)
- Güvenli Gateway: Whitelist ile malicious frame'leri engeller

### Senaryo E: CAN Trafik İzleme

**Amaç**: CAN bus üzerindeki trafiği gerçek zamanlı izleme

```bash
python3 test_scenarios.py --monitor
```

**Gösterilen Bilgiler**:
- CAN ID
- Payload (hex format)
- Mesaj oranı (msg/s)

---

## 🧪 Test ve Değerlendirme

### Test Senaryoları Modülü

Proje, kapsamlı test senaryoları içeren bir modül (`test_scenarios.py`) ile gelmektedir:

```bash
# Tüm test senaryolarını görüntüle
python3 test_scenarios.py

# Normal akış testi
python3 test_scenarios.py --normal

# MitM saldırısı
python3 test_scenarios.py --mitm

# Compromised firmware
python3 test_scenarios.py --compromised

# İnteraktif komut gönderme
python3 test_scenarios.py --interactive

# CAN trafik izleme
python3 test_scenarios.py --monitor
```

### Değerlendirme Kriterleri

Projenin başarılı kabul edilmesi için gerekli kriterler:

1. **Teknik Başarı (30%)**
   - Sistemi uçtan uca çalıştırma
   - Tüm bileşenlerin entegrasyonu
   - Log kayıtları ve raporlama

2. **Güvenlik Farkındalığı (30%)**
   - Saldırı senaryolarını doğru analiz etme
   - Savunma mekanizmalarının etkililiğini değerlendirme
   - Güvenlik açıklarını belirleme

3. **Rapor & Sunum (20%)**
   - Sonuçların açık ve teknik doğrulukta raporlanması
   - Log analizi ve yorumlama
   - Görselleştirme ve örnekler

4. **Yenilik/Ek Özellikler (20%)**
   - Basit CAN-IDS veya gateway whitelist uygulaması
   - Yeni saldırı/savunma senaryoları
   - İyileştirme önerileri

### Log Analizi

Tüm bileşenler detaylı log kaydı yapar:

**CSMS Logları** (`/tmp/csms.log`):
- Bağlantı olayları
- Gelen OCPP mesajları
- Gönderilen komutlar

**CP Logları** (`/tmp/cp.log` veya `/tmp/cp_attack.log`):
- OCPP-CAN dönüşümleri
- CAN mesaj gönderimleri
- Transaction durumları

**CAN Bus Logları** (`/tmp/can_bus.log`):
- Alınan CAN mesajları
- Charger modülü davranışları
- Enerji ölçümleri

**MitM Proxy Logları** (`/tmp/mitm_proxy.log`):
- Yakalanan mesajlar
- Mesaj manipülasyonları
- Saldırı göstergeleri

**CAN-IDS Logları**:
- Algılanan anomaliler
- Alarm kayıtları
- İstatistiksel analizler

---

## 📊 Sonuç ve Öneriler

### Temel Bulgular

Bu proje, elektrikli araç şarj istasyonlarında OCPP-CAN köprüsünün potansiyel güvenlik açıklarını başarıyla göstermiştir:

1. **Ağ Katmanı Zafiyetleri Fiziksel Kontrole Dönüşebilir**: OCPP protokolündeki güvenlik açıkları (ör. MitM), CAN-bus üzerinden fiziksel cihaz kontrolüne yol açabilir.

2. **Köprü Bileşenleri Kritik Noktalardır**: Gateway ve CP controller, saldırıların hedef noktalarıdır ve güçlü koruma gerektirir.

3. **Savunma Mekanizmaları Etkilidir**: Gateway whitelist ve CAN-IDS gibi mekanizmalar, saldırıları tespit edip engelleyebilir.

### Öneriler

#### Kısa Vadeli Öneriler

1. **Mutual TLS Uygulaması**: OCPP kanalında güçlü kriptografik koruma
2. **Gateway Whitelist**: Zorunlu olarak aktif edilmeli
3. **CAN-IDS Entegrasyonu**: Gerçek zamanlı anomali algılama
4. **Firmware İmzalama**: Secure boot mekanizmaları

#### Uzun Vadeli Öneriler

1. **CAN Segregasyonu**: Kritik ve yönetim trafiğinin ayrılması
2. **MAC/HMAC Uygulaması**: CAN uygulama katmanında mesaj doğrulama
3. **HSM/Secure Element**: Güvenli anahtar yönetimi
4. **Sürekli İzleme**: SIEM entegrasyonu ve merkezi log yönetimi

### Proje Başarı Kriterleri

✅ **Başarıyla Tamamlanan**:
- OCPP-CAN köprü simülasyonu
- MitM saldırı senaryosu
- Compromised firmware simülasyonu
- Gateway whitelist filtreleme
- CAN-IDS implementasyonu
- Kapsamlı test senaryoları

🎯 **Gelecek Geliştirmeler**:
- Gerçek donanım entegrasyonu (USB-CAN adaptör)
- WSS (WebSocket Secure) simülasyonu
- Daha gelişmiş istatistiksel analiz
- Görselleştirme ve dashboard

---

## ⚠️ Güvenlik ve Etik Notları

### Önemli Uyarılar

⚠️ **Bu simülasyon yalnızca eğitim amaçlıdır.**

- Tüm testler izole ağda yapılmalıdır
- Sadece simüle edilmiş cihazlar kullanılmalıdır
- Gerçek şarj istasyonlarına veya araçlara test yapılmamalıdır
- Gerçek sistemlere yönelik testler için yazılı izin gereklidir

### Etik Kurallar

1. **Sorumluluk**: Tüm testler yalnızca sahip olunan veya izin alınmış sistemlerde yapılmalıdır
2. **Paylaşım Kısıtları**: Loglar ve sonuçlar anonimleştirilmeli, kişisel veriler paylaşılmamalıdır
3. **Yasal Uyum**: Yerel yasalara ve düzenlemelere uyulmalıdır
4. **Bildirim**: Gerçek sistemlerde bulunan güvenlik açıkları uygun kanallardan bildirilmelidir

### Kullanım Koşulları

Bu projeyi kullanarak:
- Eğitim ve araştırma amaçlı simülasyonlar yapabilirsiniz
- Güvenlik farkındalığı eğitimleri düzenleyebilirsiniz
- Akademik çalışmalarda referans olarak kullanabilirsiniz

**Ancak**:
- Saldırı amaçlı kullanım yasaktır
- Gerçek sistemlere zarar verme amaçlı kullanım yasaktır
- Yasadışı faaliyetlerde kullanım yasaktır

---

## 📚 Referanslar

### Standartlar ve Protokoller

1. **OCPP (Open Charge Point Protocol)**
   - OCPP 1.6 Specification
   - [Open Charge Alliance](https://www.openchargealliance.org/)

2. **CAN-bus (Controller Area Network)**
   - ISO 11898 Standard
   - CAN 2.0 Specification

### Kütüphaneler ve Araçlar

1. **Python OCPP Library**
   - [ocpp-py](https://github.com/mobilityhouse/ocpp)
   - Documentation: https://ocpp.readthedocs.io/

2. **python-can**
   - [python-can Documentation](https://python-can.readthedocs.io/)
   - CAN bus interface library

3. **websockets**
   - [websockets Documentation](https://websockets.readthedocs.io/)
   - Asynchronous WebSocket library

### Akademik Kaynaklar

1. **IoT Güvenliği**
   - Vehicular Network Security
   - Industrial Control Systems Security

2. **CAN Bus Güvenliği**
   - Automotive Security Research
   - Intrusion Detection for CAN Networks

### Ek Kaynaklar

- **CAN Utilities**: `can-utils` Linux paketi
- **CAN Tools**: `cantools` Python kütüphanesi
- **USB-CAN Adaptörler**: Peak Systems, Kvaser, Lawicel

---


*Bu belge, projenin kapsamlı bir teknik raporu olarak hazırlanmıştır. Daha fazla bilgi için proje dosyalarına ve kaynak kodlara bakabilirsiniz.*
