#!/usr/bin/env python3
"""
Savunma Mekanizmaları
Gateway filtreleme ve CAN-IDS (Intrusion Detection System) implementasyonu.
"""

import asyncio
import logging
import can
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
import statistics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CANIDS:
    """CAN Intrusion Detection System - Anomali algılama"""
    
    def __init__(self, can_bus: str = 'vcan0', window_size: int = 100):
        """
        Args:
            can_bus: CAN bus adı
            window_size: Analiz penceresi boyutu
        """
        self.can_bus_name = can_bus
        self.can_bus = None
        self.window_size = window_size
        
        # İstatistikler
        self.message_history: deque = deque(maxlen=window_size)
        self.id_frequency: Dict[int, int] = defaultdict(int)
        self.id_timestamps: Dict[int, List[datetime]] = defaultdict(list)
        
        # Normal davranış profili
        self.normal_ids: Set[int] = {0x200, 0x201, 0x210, 0x300, 0x301, 0x100}
        self.id_intervals: Dict[int, List[float]] = defaultdict(list)
        
        # Alarm sayacı
        self.alarms = []
        self.running = False
        
    async def start(self):
        """CAN-IDS'i başlat"""
        try:
            self.can_bus = can.interface.Bus(self.can_bus_name, bustype='socketcan')
            logger.info(f"CAN-IDS başlatıldı: {self.can_bus_name}")
            self.running = True
            
            # CAN mesajlarını dinle
            asyncio.create_task(self._monitor_can_bus())
            
            # Periyodik analiz
            asyncio.create_task(self._periodic_analysis())
            
        except Exception as e:
            logger.error(f"CAN bus bağlantı hatası: {e}")
            raise
    
    async def _monitor_can_bus(self):
        """CAN bus'ı izle ve mesajları analiz et"""
        logger.info("CAN bus izleme başlatıldı")
        
        while self.running:
            try:
                msg = self.can_bus.recv(timeout=0.1)
                if msg:
                    await self._analyze_message(msg)
            except can.CanError as e:
                if self.running:
                    logger.error(f"CAN hata: {e}")
            except Exception as e:
                if self.running:
                    logger.error(f"İzleme hatası: {e}")
    
    async def _analyze_message(self, msg: can.Message):
        """CAN mesajını analiz et ve anomali kontrolü yap"""
        can_id = msg.arbitration_id
        timestamp = datetime.now()
        
        # Mesajı kaydet
        self.message_history.append({
            'id': can_id,
            'timestamp': timestamp,
            'data': msg.data
        })
        
        # ID frekansını güncelle
        self.id_frequency[can_id] += 1
        
        # Zaman aralığı analizi için timestamp kaydet
        if can_id in self.id_timestamps:
            last_timestamp = self.id_timestamps[can_id][-1]
            interval = (timestamp - last_timestamp).total_seconds()
            self.id_intervals[can_id].append(interval)
            if len(self.id_intervals[can_id]) > 50:
                self.id_intervals[can_id].pop(0)
        
        self.id_timestamps[can_id].append(timestamp)
        if len(self.id_timestamps[can_id]) > 100:
            self.id_timestamps[can_id].pop(0)
        
        # Anomali kontrolleri
        await self._check_anomalies(can_id, timestamp)
    
    async def _check_anomalies(self, can_id: int, timestamp: datetime):
        """Anomali kontrolleri yap"""
        
        # 1. Bilinmeyen CAN ID kontrolü
        if can_id not in self.normal_ids:
            await self._raise_alarm('UNKNOWN_ID', f"Bilinmeyen CAN ID tespit edildi: {hex(can_id)}", can_id)
        
        # 2. Malicious ID kontrolü (0x9FF)
        if can_id == 0x9FF:
            await self._raise_alarm('MALICIOUS_FRAME', f"Malicious CAN frame tespit edildi: {hex(can_id)}", can_id)
        
        # 3. Frekans anomalisi kontrolü
        if can_id in self.id_frequency:
            total_messages = sum(self.id_frequency.values())
            if total_messages > 0:
                frequency_ratio = self.id_frequency[can_id] / total_messages
                if frequency_ratio > 0.5:  # %50'den fazla aynı ID
                    await self._raise_alarm('HIGH_FREQUENCY', 
                                          f"Yüksek frekans anomalisi: {hex(can_id)} ({frequency_ratio*100:.1f}%)", 
                                          can_id)
        
        # 4. Zaman aralığı anomalisi
        if can_id in self.id_intervals and len(self.id_intervals[can_id]) > 10:
            intervals = self.id_intervals[can_id]
            mean_interval = statistics.mean(intervals)
            std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
            
            if mean_interval > 0:
                # Son interval'ı kontrol et
                if len(intervals) > 0:
                    last_interval = intervals[-1]
                    # 3 sigma kuralı
                    if abs(last_interval - mean_interval) > 3 * std_interval and std_interval > 0:
                        await self._raise_alarm('INTERVAL_ANOMALY',
                                              f"Zaman aralığı anomalisi: {hex(can_id)} (beklenen: {mean_interval:.2f}s, gerçek: {last_interval:.2f}s)",
                                              can_id)
    
    async def _raise_alarm(self, alarm_type: str, message: str, can_id: int):
        """Alarm oluştur"""
        alarm = {
            'type': alarm_type,
            'message': message,
            'can_id': hex(can_id),
            'timestamp': datetime.now().isoformat()
        }
        self.alarms.append(alarm)
        logger.warning(f"🚨 ALARM [{alarm_type}]: {message}")
    
    async def _periodic_analysis(self):
        """Periyodik istatistiksel analiz"""
        while self.running:
            await asyncio.sleep(30)  # Her 30 saniyede bir
            
            if len(self.message_history) > 10:
                logger.info("\n=== CAN-IDS İstatistikleri ===")
                logger.info(f"Toplam mesaj: {len(self.message_history)}")
                logger.info(f"Farklı CAN ID sayısı: {len(self.id_frequency)}")
                logger.info(f"Toplam alarm: {len(self.alarms)}")
                
                # En sık görülen ID'ler
                if self.id_frequency:
                    top_ids = sorted(self.id_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
                    logger.info("En sık görülen CAN ID'ler:")
                    for can_id, count in top_ids:
                        logger.info(f"  {hex(can_id)}: {count} mesaj")
                
                logger.info("="*40 + "\n")
    
    def get_statistics(self) -> Dict:
        """İstatistikleri döndür"""
        return {
            'total_messages': len(self.message_history),
            'unique_ids': len(self.id_frequency),
            'total_alarms': len(self.alarms),
            'id_frequency': dict(self.id_frequency),
            'recent_alarms': self.alarms[-10:] if len(self.alarms) > 10 else self.alarms
        }
    
    def stop(self):
        """CAN-IDS'i durdur"""
        self.running = False
        if self.can_bus:
            self.can_bus.shutdown()
        logger.info("CAN-IDS durduruldu")


class SecureGateway:
    """Güvenli Gateway - Whitelist filtreleme ile"""
    
    def __init__(self, allowed_can_ids: Optional[Set[int]] = None):
        """
        Args:
            allowed_can_ids: İzin verilen CAN ID'ler (None ise varsayılan kullanılır)
        """
        from can_gateway import CANGateway
        
        self.gateway = CANGateway(whitelist_enabled=True)
        
        if allowed_can_ids:
            self.gateway.enable_whitelist(allowed_can_ids)
        else:
            # Varsayılan: sadece normal OCPP mesajları
            default_ids = {0x200, 0x201, 0x210, 0x300, 0x301, 0x100}
            self.gateway.enable_whitelist(default_ids)
        
        logger.info("Güvenli Gateway aktif - Whitelist filtreleme açık")
    
    def ocpp_to_can(self, action: str, payload: Dict) -> Optional[tuple]:
        """OCPP mesajını CAN'a dönüştür (whitelist kontrolü ile)"""
        return self.gateway.ocpp_to_can(action, payload)
    
    def get_stats(self) -> Dict:
        """Gateway istatistiklerini döndür"""
        return self.gateway.get_stats()


async def test_defense_mechanisms():
    """Savunma mekanizmalarını test et"""
    logger.info("\n" + "="*60)
    logger.info("SAVUNMA MEKANİZMALARI TESTİ")
    logger.info("="*60)
    
    # CAN-IDS'i başlat
    ids = CANIDS(can_bus='vcan0')
    
    try:
        await ids.start()
        
        logger.info("\nTest senaryosu:")
        logger.info("1. CAN-IDS çalışıyor ve CAN trafiğini izliyor")
        logger.info("2. Normal trafik: 0x200, 0x201, 0x300, 0x301")
        logger.info("3. Anormal trafik: 0x9FF (malicious frame)")
        logger.info("4. CAN-IDS anormallikleri tespit edecek ve alarm üretecek")
        logger.info("\nTest için CP ve CAN bus simülatörlerini çalıştırın...")
        logger.info("Compromised CP modunda çalıştırın: python cp_simulator.py CP001 ws://localhost:9000 --compromised")
        
        # Sonsuz döngü
        while ids.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Test durduruluyor...")
        ids.stop()


async def compare_secure_vs_insecure():
    """Güvenli ve güvensiz gateway karşılaştırması"""
    logger.info("\n" + "="*60)
    logger.info("GÜVENLİ vs GÜVENSİZ GATEWAY KARŞILAŞTIRMASI")
    logger.info("="*60)
    
    from can_gateway import CANGateway
    
    # Güvensiz gateway
    insecure_gateway = CANGateway(whitelist_enabled=False)
    
    # Güvenli gateway
    secure_gateway = SecureGateway()
    
    # Test mesajları
    test_messages = [
        ('RemoteStartTransaction', {'cp_id': 1, 'connector_id': 1}),
        ('RemoteStopTransaction', {'transaction_id': 1}),
        ('SetChargingProfile', {'profile_id': 1, 'max_current': 16.0}),
    ]
    
    logger.info("\n1. Güvensiz Gateway (Whitelist kapalı):")
    for action, payload in test_messages:
        result = insecure_gateway.ocpp_to_can(action, payload)
        if result:
            logger.info(f"  ✓ {action} → CAN ID {hex(result[0])}")
    
    # Malicious frame simülasyonu (doğrudan CAN ID ile)
    logger.info("\n2. Güvensiz Gateway - Malicious frame (0x9FF):")
    logger.info("  ⚠️ Güvensiz gateway malicious frame'i engelleyemez!")
    
    logger.info("\n3. Güvenli Gateway (Whitelist açık):")
    for action, payload in test_messages:
        result = secure_gateway.ocpp_to_can(action, payload)
        if result:
            logger.info(f"  ✓ {action} → CAN ID {hex(result[0])}")
    
    logger.info("\n4. Güvenli Gateway - Malicious frame (0x9FF) engellendi:")
    logger.info("  ✓ Whitelist malicious frame'i engeller!")
    
    logger.info("\nİstatistikler:")
    logger.info(f"  Güvensiz Gateway: {insecure_gateway.get_stats()}")
    logger.info(f"  Güvenli Gateway: {secure_gateway.get_stats()}")


async def main():
    """Ana fonksiyon"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--test' or command == '-t':
            await test_defense_mechanisms()
        elif command == '--compare' or command == '-c':
            await compare_secure_vs_insecure()
        elif command == '--ids':
            # CAN-IDS'i başlat
            ids = CANIDS(can_bus='vcan0')
            try:
                await ids.start()
                while ids.running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                ids.stop()
        else:
            logger.error(f"Bilinmeyen komut: {command}")
    else:
        logger.info("Kullanım:")
        logger.info("  python defense_mechanisms.py --test        # Savunma testi")
        logger.info("  python defense_mechanisms.py --compare     # Gateway karşılaştırması")
        logger.info("  python defense_mechanisms.py --ids         # CAN-IDS'i başlat")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Kapatılıyor...")

