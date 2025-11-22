#!/usr/bin/env python3
"""
CAN Bus ve Charger Modülü Simülatörü
CP'den gelen CAN mesajlarını dinler ve charger modülü davranışını simüle eder.
"""

import asyncio
import logging
import struct
import can
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChargerModule:
    """Charger modülü simülatörü"""
    
    def __init__(self, connector_id: int = 1):
        self.connector_id = connector_id
        self.charging = False
        self.transaction_id = None
        self.energy_wh = 0
        self.max_current = 16.0  # Amper
        self.faulty = False  # Hatalı davranış simülasyonu (0x9FF mesajı alındığında)
        
    def start_charging(self, transaction_id: int):
        """Şarjı başlat"""
        self.charging = True
        self.transaction_id = transaction_id
        self.energy_wh = 0
        logger.info(f"[Charger {self.connector_id}] Şarj başlatıldı - Transaction: {transaction_id}")
        
    def stop_charging(self):
        """Şarjı durdur"""
        self.charging = False
        logger.info(f"[Charger {self.connector_id}] Şarj durduruldu - Toplam enerji: {self.energy_wh} Wh")
        self.transaction_id = None
        
    def set_max_current(self, current: float):
        """Maksimum akımı ayarla"""
        self.max_current = current
        logger.info(f"[Charger {self.connector_id}] Maksimum akım ayarlandı: {current} A")
        
    def update_energy(self):
        """Enerji değerini güncelle (şarj sırasında)"""
        if self.charging:
            # Simülasyon: Her saniye ~100W ekle (max_current'e göre)
            power_w = self.max_current * 230  # 230V varsayımı
            self.energy_wh += int(power_w / 3600)  # Wh cinsinden
            
    def set_faulty(self, faulty: bool):
        """Hatalı davranış modunu ayarla"""
        self.faulty = faulty
        if faulty:
            logger.warning(f"[Charger {self.connector_id}] ⚠️ HATALI MOD: Röle sürekli açık!")
            # Hatalı modda şarjı durdur
            self.stop_charging()
        else:
            logger.info(f"[Charger {self.connector_id}] Normal moda döndü")


class CANBusSimulator:
    """CAN bus simülatörü - charger modüllerini yönetir"""
    
    def __init__(self, can_bus: str = 'vcan0'):
        self.can_bus_name = can_bus
        self.can_bus = None
        self.chargers: Dict[int, ChargerModule] = {}
        self.running = False
        
    async def start(self):
        """CAN bus simülatörünü başlat"""
        try:
            self.can_bus = can.interface.Bus(self.can_bus_name, bustype='socketcan')
            logger.info(f"CAN Bus Simülatörü başlatıldı: {self.can_bus_name}")
            self.running = True
            
            # Varsayılan charger modülü
            self.chargers[1] = ChargerModule(connector_id=1)
            
            # CAN mesajlarını dinle
            asyncio.create_task(self._listen_can_messages())
            
            # Periyodik enerji güncellemesi
            asyncio.create_task(self._periodic_updates())
            
            logger.info("Charger modülü hazır ve CAN mesajlarını dinliyor...")
            
        except Exception as e:
            logger.error(f"CAN bus bağlantı hatası: {e}")
            logger.info("vcan0 oluşturulmuş mu kontrol edin: sudo ./setup_vcan.sh")
            raise
    
    async def _listen_can_messages(self):
        """CAN bus üzerindeki mesajları dinle ve işle"""
        logger.info("CAN mesaj dinleyici başlatıldı")
        
        while self.running:
            try:
                msg = self.can_bus.recv(timeout=0.1)
                if msg:
                    await self._handle_can_message(msg)
            except can.CanError as e:
                if self.running:
                    logger.error(f"CAN hata: {e}")
            except Exception as e:
                if self.running:
                    logger.error(f"CAN dinleme hatası: {e}")
    
    async def _handle_can_message(self, msg: can.Message):
        """CAN mesajını işle ve charger modülüne ilet"""
        can_id = msg.arbitration_id
        payload = msg.data
        
        logger.info(f"CAN mesajı alındı: ID={hex(can_id)}, Data={payload.hex()}")
        
        # RemoteStartTransaction (0x200)
        if can_id == 0x200:
            await self._handle_start_transaction(payload)
        
        # RemoteStopTransaction (0x201)
        elif can_id == 0x201:
            await self._handle_stop_transaction(payload)
        
        # SetChargingProfile (0x210)
        elif can_id == 0x210:
            await self._handle_set_charging_profile(payload)
        
        # Malicious frame (0x9FF) - Compromised firmware simülasyonu
        elif can_id == 0x9FF:
            logger.warning("⚠️ MALICIOUS CAN FRAME TESPİT EDİLDİ (0x9FF)!")
            logger.warning("Charger modülü hatalı davranış moduna geçiyor...")
            for charger in self.chargers.values():
                charger.set_faulty(True)
        
        # Diğer mesajlar
        else:
            logger.debug(f"İşlenmeyen CAN ID: {hex(can_id)}")
    
    async def _handle_start_transaction(self, payload: bytes):
        """RemoteStartTransaction mesajını işle"""
        if len(payload) >= 3:
            cp_id, connector_id, start_cmd = struct.unpack('BBB', payload[:3])
            
            if connector_id not in self.chargers:
                self.chargers[connector_id] = ChargerModule(connector_id=connector_id)
            
            charger = self.chargers[connector_id]
            transaction_id = len(self.chargers) + 1
            charger.start_charging(transaction_id)
            
            # StatusNotification gönder (Charging)
            await self._send_status_notification(connector_id, 'Charging')
            
            logger.info(f"Transaction başlatıldı: Connector {connector_id}, Transaction {transaction_id}")
    
    async def _handle_stop_transaction(self, payload: bytes):
        """RemoteStopTransaction mesajını işle"""
        if len(payload) >= 4:
            tx_id = struct.unpack('<I', payload[:4])[0]
            
            # Transaction ID'ye göre charger bul
            for charger in self.chargers.values():
                if charger.transaction_id == tx_id:
                    charger.stop_charging()
                    await self._send_status_notification(charger.connector_id, 'Available')
                    await self._send_meter_values(charger.connector_id, charger.energy_wh)
                    break
    
    async def _handle_set_charging_profile(self, payload: bytes):
        """SetChargingProfile mesajını işle"""
        if len(payload) >= 4:
            profile_id, max_current_raw = struct.unpack('<HH', payload[:4])
            max_current = max_current_raw / 10.0  # 0.1A resolution
            
            # Tüm charger'lara uygula (veya profile_id'ye göre)
            for charger in self.chargers.values():
                charger.set_max_current(max_current)
            
            logger.info(f"Charging profile ayarlandı: Profile {profile_id}, Max Current {max_current} A")
    
    async def _send_meter_values(self, connector_id: int, energy_wh: int):
        """MeterValues mesajını CAN'a gönder (CAN ID 0x300)"""
        timestamp = int(datetime.now().timestamp()) % 0xFFFF
        payload = struct.pack('<BIBH', connector_id, energy_wh, timestamp)
        
        msg = can.Message(arbitration_id=0x300, data=payload, is_extended_id=False)
        self.can_bus.send(msg)
        logger.info(f"MeterValues gönderildi: Connector {connector_id}, Energy {energy_wh} Wh")
    
    async def _send_status_notification(self, connector_id: int, status: str):
        """StatusNotification mesajını CAN'a gönder (CAN ID 0x301)"""
        status_map = {'Available': 0x01, 'Preparing': 0x02, 'Charging': 0x03,
                     'SuspendedEVSE': 0x04, 'SuspendedEV': 0x05, 'Finishing': 0x06,
                     'Reserved': 0x07, 'Unavailable': 0x08, 'Faulted': 0x09}
        status_byte = status_map.get(status, 0x00)
        
        payload = struct.pack('BB', connector_id, status_byte) + b'\x00' * 6
        
        msg = can.Message(arbitration_id=0x301, data=payload, is_extended_id=False)
        self.can_bus.send(msg)
        logger.info(f"StatusNotification gönderildi: Connector {connector_id}, Status {status}")
    
    async def _periodic_updates(self):
        """Periyodik olarak enerji değerlerini güncelle ve MeterValues gönder"""
        while self.running:
            await asyncio.sleep(5)  # Her 5 saniyede bir
            
            for charger in self.chargers.values():
                if charger.charging:
                    charger.update_energy()
                    await self._send_meter_values(charger.connector_id, charger.energy_wh)
    
    def stop(self):
        """CAN bus simülatörünü durdur"""
        self.running = False
        if self.can_bus:
            self.can_bus.shutdown()
        logger.info("CAN Bus Simülatörü durduruldu")


async def main():
    """Ana fonksiyon"""
    import sys
    
    can_bus = sys.argv[1] if len(sys.argv) > 1 else 'vcan0'
    
    logger.info("CAN Bus ve Charger Modülü Simülatörü")
    logger.info(f"CAN Bus: {can_bus}")
    
    simulator = CANBusSimulator(can_bus=can_bus)
    
    try:
        await simulator.start()
        
        # Sonsuz döngü
        while simulator.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Simülatör kapatılıyor...")
        simulator.stop()
    except Exception as e:
        logger.error(f"Hata: {e}")
        simulator.stop()


if __name__ == "__main__":
    asyncio.run(main())

