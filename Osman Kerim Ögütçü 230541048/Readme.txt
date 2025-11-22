DNS Tünelleme (Tunneling) Yöntemiyle Veri Sızdırma Tespiti ve Davranışsal Analiz Simülasyonu

1. Projenin Amacı
Bu proje, siber güvenlikte sıkça kullanılan ancak tespit edilmesi zor olan DNS Tünelleme saldırılarını simüle etmeyi ve bunları istatistiksel analiz yöntemleriyle tespit etmeyi amaçlar. Saldırganların güvenlik duvarlarını (Firewall) atlatmak için Port 53 (DNS) protokolünü nasıl kötüye kullandığını gösterir ve bu trafiği meşru (normal) trafikten ayıran temel anomalileri görselleştirir.

youtube linki : https://youtu.be/aIfPrqAMuig


2. Kullanılan Senaryo ve Yöntem
Proje, "normal" bir ağ davranışı ile saldırganın "anormal" davranışını karşılaştıran bir vaka analizi üzerine kuruludur.


Saldırı Vektörü: Saldırganın, hassas verileri Base64 ile kodlayıp DNS alt alan adlarına (subdomain) gömmesi ve dışarıya sızdırması senaryosu işlenmiştir.


Komuta Kontrol (C2): Zararlı yazılımın dışarıdaki sunucudan komut almak için TXT kayıtlarını kullanması simüle edilmiştir.


3. Teknik Analiz ve Tespit Metrikleri
Bu çalışmada anomali tespiti için 4 temel metrik kullanılmış ve Python ile görselleştirilmiştir:


Trafik Hacmi (Volume Analysis): Normal kullanıcıların düşük sorgu hacmine karşın, saldırı anında oluşan ani trafik artışları (Spike) tespit edilmiştir.



Yük Analizi (Payload Analysis - Uzunluk): Meşru sorguların (örn: google.com) kısa yapısına karşın, veri kaçırmak için kullanılan sorguların (örn: Z216bGl...) anormal uzunluğu analiz edilmiştir.



Entropi Analizi (Complexity): İnsan tarafından okunabilen alan adları ile şifrelenmiş/kodlanmış verilerin (Yüksek Entropi) karmaşıklık farkı ortaya konmuştur.



Protokol Davranışı (Record Types): Trafiğin çoğunluğunu oluşturan A/AAAA kayıtlarının aksine, tünelleme sırasında artış gösteren TXT kayıtları "anomali" olarak işaretlenmiştir.


4. Kullanılan Teknolojiler
Programlama Dili: Python

Veri Analizi ve Görselleştirme: Matplotlib, Seaborn, NumPy


Analiz Yaklaşımı: UEBA (Kullanıcı ve Varlık Davranış Analitiği) prensiplerine dayalı istatistiksel sapma tespiti.

5. Sonuç
Bu simülasyon, imza tabanlı korumanın yetersiz kaldığı durumlarda, davranışsal profil oluşturmanın (Baselining) ve istatistiksel analizin DNS tünelleme saldırılarını yakalamada ne kadar kritik olduğunu kanıtlamaktadır.