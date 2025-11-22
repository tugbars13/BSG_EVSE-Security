# Kimlik Klonlama Tespit Simülasyonu

## Proje Özeti

Bu proje, elektrikli araç şarj istasyonları için kimlik klonlama saldırılarını tespit eden ve engelleyen bir güvenlik simülasyon sistemidir. Sistem, aynı kullanıcı kimliğinin farklı konumlardaki şarj istasyonlarında aynı anda kullanılmasını tespit ederek kimlik klonlama saldırılarını önlemeyi amaçlamaktadır.

https://youtu.be/-w5ffUp7sHE

## Amaç ve Kapsam

Elektrikli araç şarj altyapılarında RFID veya benzeri kimlik doğrulama sistemleri kullanılmaktadır. Bu sistemler, kötü niyetli kişiler tarafından klonlanabilir ve aynı kimlik birden fazla yerde kullanılabilir. Bu proje, bu tür saldırıları gerçek zamanlı olarak tespit eden bir mekanizma sunmaktadır.

### Temel Özellikler

- **Aktif Oturum Takibi**: Her kullanıcı kimliği için aktif şarj oturumlarını izleme
- **Anomali Tespiti**: Aynı kimliğin farklı istasyonlarda eşzamanlı kullanımını tespit etme
- **Otomatik Engelleme**: Şüpheli aktiviteleri otomatik olarak engelleme
- **İstasyon Yönetimi**: Şarj istasyonlarının durumunu ve kullanılabilirliğini yönetme

## Teknik Mimari

### Proje Yapısı

Proje, .NET 6.0 platformu üzerinde geliştirilmiş bir konsol uygulamasıdır. Aşağıdaki ana bileşenlerden oluşmaktadır:

#### 1. Models.cs
Veri modellerini içerir:
- **ChargePoint**: Şarj istasyonu bilgileri (ID, konum, kullanım durumu)
- **ChargeSession**: Aktif şarj oturumu bilgileri (oturum ID, kullanıcı ID, istasyon ID, başlangıç zamanı)
- **ChargeResponse**: Şarj talebi yanıt bilgileri (başarı durumu, mesaj, oturum)

#### 2. ChargePointOperator.cs
Şarj istasyonu operatörü mantığını içerir:
- **RequestCharge()**: Yeni şarj talebi işleme ve anomali kontrolü
- **StopCharge()**: Aktif şarj oturumunu sonlandırma
- Aktif oturum listesi yönetimi
- İstasyon durumu takibi

#### 3. Program.cs
Test senaryolarını ve uygulama giriş noktasını içerir.

### Güvenlik Mekanizması

Sistem, aşağıdaki mantıkla çalışmaktadır:

1. **Oturum Kontrolü**: Yeni bir şarj talebi geldiğinde, aynı kullanıcı kimliği için aktif bir oturum olup olmadığı kontrol edilir.
2. **Anomali Tespiti**: Eğer aynı kimlik başka bir istasyonda aktif bir oturuma sahipse, bu durum anomali olarak işaretlenir.
3. **Engelleme**: Anomali tespit edildiğinde, yeni talep reddedilir ve detaylı bir uyarı mesajı üretilir.
4. **Oturum Sonlandırma**: Kullanıcı şarjını tamamladığında, oturum sonlandırılır ve istasyon tekrar kullanılabilir hale gelir.

## Test Senaryoları

Proje, üç ana senaryo ile test edilmektedir:

### Senaryo 1: Meşru Kullanım
Meşru bir kullanıcı (Ahmet) İstanbul'daki bir şarj istasyonunda şarj başlatır. Sistem bu talebi başarıyla işler ve oturum oluşturur.

### Senaryo 2: Kimlik Klonlama Anomalisi
Ahmet İstanbul'da şarjdayken, kötü niyetli bir kişi Ahmet'in klonlanmış kimliğini kullanarak Ankara'daki başka bir istasyonda şarj başlatmayı dener. Sistem bu anomaliyi tespit eder ve talebi engeller.

### Senaryo 3: Meşru Kullanımın Devamı
İlk şarj oturumu sonlandırıldıktan sonra, Ahmet Ankara'ya gidip orada şarj başlatmayı dener. Bu durumda sistem normal şekilde çalışır ve şarj başlatılır.

## Çalıştırma Talimatları

### Gereksinimler
- .NET 6.0 SDK veya üzeri
- Windows, Linux veya macOS işletim sistemi

### Kurulum ve Çalıştırma

1. Proje dizinine gidin:
```bash
cd IdentityCloningSim
```

2. Projeyi çalıştırın:
```bash
dotnet run
```

### Beklenen Çıktı

Program çalıştırıldığında, üç test senaryosu sırayla uygulanır ve sonuçlar konsola yazdırılır:
- Başarılı işlemler yeşil renkte gösterilir
- Anomali tespitleri kırmızı renkte vurgulanır
- Her senaryo için detaylı bilgi mesajları üretilir

## Sonuç ve Değerlendirme

Bu simülasyon, kimlik klonlama saldırılarını tespit etmek için basit ancak etkili bir yaklaşım sunmaktadır. Sistem, aynı kullanıcı kimliğinin farklı konumlarda eşzamanlı kullanımını tespit ederek güvenlik açıklarını kapatmaktadır.

### Avantajlar
- Gerçek zamanlı anomali tespiti
- Basit ve anlaşılır mimari
- Düşük performans maliyeti
- Kolay entegrasyon potansiyeli

### Sınırlamalar ve Geliştirme Önerileri
- Coğrafi mesafe kontrolü eklenebilir (kısa sürede uzak mesafe hareketi kontrolü)
- Zaman bazlı analiz geliştirilebilir (şüpheli zaman aralıkları)
- Çoklu istasyon kullanımı için daha gelişmiş kurallar tanımlanabilir
- Veritabanı entegrasyonu ile kalıcı kayıt tutulabilir
- API arayüzü eklenerek gerçek sistemlerle entegrasyon sağlanabilir


