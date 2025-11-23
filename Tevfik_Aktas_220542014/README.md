# Hayalet İstasyon Anomalisi (Logical DoS)

**Hazırlayan:** Tevfik Aktaş - 220542014
**Ders:** Bilgi Sistemleri ve Güvenliği

## Proje Tanımı
Bu proje, Elektrikli Araç Şarj İstasyonları (EVCI) yönetiminde kullanılan OCPP protokolündeki kimlik doğrulama zafiyetlerini (Güvenlik Profili 1) ele almaktadır. Projede, fiziksel erişim olmadan bir istasyonun kimliğinin taklit edilerek (Spoofing) nasıl mantıksal olarak hizmet dışı bırakıldığı (Logical DoS) simüle edilmiş ve mTLS (Güvenlik Profili 3) ile savunma geliştirilmiştir.

## 📺 Proje Tanıtım Videosu
Detaylı anlatım ve demo için YouTube videomu izleyebilirsiniz:
https://youtu.be/4UKipVKuVNE

## 📂 Dosya İçeriği
* **csms_sunucu.py:** Zafiyetli Merkezi Yönetim Sistemi simülasyonu.
* **mesru_cp.py:** Normal çalışan meşru şarj istasyonu simülasyonu.
* **saldirgan_cp.py:** Kimlik taklidi yapan saldırı betiği.
* **csms_guvenli_sunucu.py:** mTLS ile güçlendirilmiş güvenli sunucu.
* **mesru_guvenli_cp.py:** mTLS sertifikası kullanan güvenli istasyon.
* **Sunum_Tevfik_Aktas.pdf:** Proje sunum dosyası.
* **Sertifika Dosyaları (.crt, .key):** SSL/TLS el sıkışması için oluşturulan test sertifikaları.

## 🚀 Kurulum ve Çalıştırma

1. **Gereksinimler:**
   Python 3.10+ ve gerekli kütüphaneler:
   ```bash
   pip install ocpp websockets
