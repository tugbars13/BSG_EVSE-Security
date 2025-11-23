İçeriden Başlatılan Veri Sızıntısı
Toplu Belge İndirme ve Harici Yükleme Anomalisi
1. Anomali Tanımı

İçeriden başlatılan veri sızıntısı anomalisi; bir kullanıcının normal erişim, indirme veya paylaşım alışkanlıklarından saparak hassas verileri yetkisiz ortamlara aktarması, kopyalaması veya dışa sızdırması durumudur. Bu sapma; toplu belge indirme, harici depolama hizmetlerine yükleme veya olağandışı veri aktarım davranışları şeklinde ortaya çıkar.

2. Olası Nedenler
2.1 Kategori – Sebep – Açıklama Tablosu
Kategori	Olası Sebep	Açıklama
İnsan Kaynaklı Hatalar	Yanlışlıkla veri paylaşımı	Kullanıcılar farkında olmadan gizli dosyaları yetkisiz kişilerle paylaşabilir veya yanlış alıcıya gönderebilir.
İnsan Kaynaklı Hatalar	Güvenlik farkındalığı eksikliği	Eğitim eksikliği nedeniyle çalışanlar istemeden veri sızıntısına sebep olabilir.
İç Tehditler	Kötü niyetli çalışan	Bilerek veri kopyalama, dışa aktarma veya paylaşma davranışları gerçekleşebilir.
Dış Tehditler	Kimlik avı / hesap ele geçirme	Saldırganlar ele geçirdikleri hesaplarla hassas verilere erişebilir.
Dış Tehditler	Zararlı yazılım (malware)	Malware, keylogger veya trojan türü yazılımlar sistemden veri çalabilir.
Sistem Zafiyetleri	Yetersiz erişim kontrolleri	Hatalı dosya izinleri veya eksik şifreleme nedeniyle sızıntı gerçekleşebilir.
Sistem Zafiyetleri	Güncellenmemiş yazılım / açıklar	Yazılım açıkları saldırganlara veri çalma imkânı sağlayabilir.
Üçüncü Taraf Riskleri	Tedarikçi / partner yetkileri	Ortak kullanılan bulut ve partner sistemleri yeterince güvenli değilse veri sızabilir.
Teknik Hatalar	Yanlış yapılandırma	Sunucu, veritabanı veya bulut depolama ayarlarının hatalı olması, verilerin yetkisiz erişime açılmasına neden olabilir.
Teknik Hatalar	Log ve izleme eksikliği	Erişim ve indirme aktiviteleri izlenmezse sızıntılar geç fark edilir.
3. Olası Riskler ve Etkiler

Hassas müşteri, çalışan veya finansal bilgilerin sızması sonucu maddi kayıplar, cezai yaptırımlar ortaya çıkabilir.

KVKK, GDPR vb. veri koruma yasalarının ihlal edilmesi kurumun hukuki sorumluluk üstlenmesine yol açar.

Müşteri ve iş ortaklarında güven kaybı, marka değerinde düşüş ve itibar zedelenmesi yaşanabilir.

Sızıntı sonrası sistemlerin geçici olarak kapatılması iş süreçlerini aksatabilir.

Stratejik belgelerin rakiplere ulaşması rekabet gücünü zayıflatır.

Kişisel verilerin sızması müşteri ilişkilerine zarar verir.

İç kullanıcı kaynaklı kötüye kullanım riski artar.

Olay müdahale, iyileştirme ve ek güvenlik yatırımları maliyetleri yükseltir.

4. İlgili Standartlar ve Referanslar

ISO/IEC 27001 – Bilgi güvenliği yönetim sistemi için temel standarttır; politikalar, prosedürler ve kontrol mekanizmalarını tanımlar.

ISO/IEC 27002 – ISO 27001’de uygulanabilir güvenlik kontrollerinin detaylı rehberidir.

NIST SP 800-53 – Veri sızıntısı önleme, erişim yönetimi ve gizlilik kontrolleri için kapsamlı bir çerçeve sunar.

NIST SP 800-61 – Güvenlik olay yönetimi ve olay müdahalesi süreçleri için kılavuz sağlar.

PCI DSS – Ödeme kartı bilgilerinin güvenliğine odaklanır; erişim kontrol ve veri izleme kuralları içerir.

KVKK – Türkiye’de kişisel verilerin korunması ve yetkisiz erişimin önlenmesine ilişkin hukuki çerçeve.

GDPR – Avrupa Birliği kişisel verilerin korunması yasası; veri sızıntısı durumunda bildirim ve güvenlik gereksinimlerini tanımlar.

5. Çözüm Önerileri

Erişim Kontrolleri: Kullanıcıların yalnızca görevleri için gerekli verilere erişmesi sağlanmalıdır.

Veri Sınıflandırması: Hassas veriler etiketlenmeli, koruma seviyelerine göre kontrol edilmelidir.

DLP Sistemleri: Yetkisiz veri aktarımı, kopyalama ve dışa yükleme davranışlarını engelleyen sistemler kullanılmalıdır.

MFA ve Güçlü Parola Politikası: Hesap güvenliği için çok faktörlü kimlik doğrulama zorunlu olmalıdır.

Anomali Tespiti: Toplu indirme, olağandışı erişim veya yüksek hacimli dışa aktarım gibi davranışlar gerçek zamanlı izlenmelidir.

Güvenlik Eğitimi: Çalışanlara düzenli farkındalık ve güvenlik eğitimi verilmelidir.

Sistem Güncellemeleri: Yazılım, işletim sistemi ve altyapılar düzenli olarak güncellenmelidir.

Olay Müdahale Planı: Veri sızıntısı durumunda hızlı müdahale için prosedürler oluşturulmalıdır.

Şifreleme: Veriler hem depolama hem aktarım sırasında güçlü şifreleme teknikleriyle korunmalıdır.

6. Sonuç ve Değerlendirme

İçeriden başlatılan veri sızıntıları, kurumların hassas verilerini ciddi risklerle karşı karşıya bırakır. Bu tür anomaliler; finansal kayıplar, hukuki yaptırımlar, operasyonel kesintiler ve itibar kaybı gibi önemli sonuçlara yol açabilir.

Veri sızıntılarının temel nedenleri arasında insan hataları, kötü niyetli iç kullanıcılar, dış saldırılar, sistem açıkları ve yanlış yapılandırmalar bulunmaktadır. Bu risklerin kontrol altına alınması için erişim kontrolleri, DLP sistemleri, güçlü doğrulama yöntemleri, düzenli eğitimler ve etkin izleme çözümleri uygulanmalıdır.

Erken tespit ve hızlı müdahale mekanizmalarının kurulması; kurumsal veri güvenliğinin sağlanması ve operasyonel risklerin azaltılması açısından kritik önem taşır.

7. Kaynakça

ISO/IEC 27001:2013 – Information Security Management Systems

ISO/IEC 27002:2013 – Information Security Controls

NIST SP 800-53 – Security and Privacy Controls

NIST SP 800-61 – Computer Security Incident Handling Guide

PCI DSS – Payment Card Industry Data Security Standard

KVKK – Kişisel Verilerin Korunması Kanunu

GDPR – General Data Protection Regulation

Whitman, M. E., & Mattord, H. J. Principles of Information Security, Cengage Learning, 2021

Shinder, D. Security Log Management, Syngress, 2010

Kim, D., et al. Insider Threats in Cyber Security, Springer, 2020
