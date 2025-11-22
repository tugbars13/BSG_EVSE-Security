#!/usr/bin/env python3
"""
Charge Point (CP) Simülatörü
OCPP protokolü ile CSMS'e bağlanır ve CAN bus üzerinden charger modülü ile iletişim kurar.
"""

import asyncio
import logging
import websockets
from datetime import datetime
from ocpp.v16 import ChargePoint as CP
from ocpp.v16.enums import Action, RegistrationStatus, ChargePointStatus
from ocpp.routing import on
from ocpp.v16 import call_result, call
import can
from can_gateway import CANGateway

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ChargePointSimulator(CP):
    """Charge Point simülatörü - OCPP ve CAN entegrasyonu"""
    
    def __init__(self, id: str, connection, can_bus: str = 'vcan0', compromised: bool = False):
        super().__init__(id, connection)
        self.id = id
        self.can_bus_name = can_bus
        self.can_bus = None
        self.gateway = CANGateway(whitelist_enabled=False)
        self.connectors = {1: {'status': 'Available', 'transaction_id': None, 'energy': 0}}
        self.compromised = compromised  # Firmware compromise simülasyonu
        self.running = False
        
    async def start(self):
        """CP'yi başlat - CAN bus bağlantısını kur"""
        try:
            self.can_bus = can.interface.Bus(self.can_bus_name, bustype='socketcan')
            logger.info(f"[{self.id}] CAN bus bağlantısı kuruldu: {self.can_bus_name}")
            self.running = True
            
            # CAN mesajlarını dinle
            asyncio.create_task(self._listen_can_messages())
            
            # OCPP mesajlarını dinle
            await super().start()
        except Exception as e:
            logger.error(f"[{self.id}] CAN bus bağlantı hatası: {e}")
            logger.info("vcan0 oluşturulmuş mu kontrol edin: sudo ./setup_vcan.sh")
            raise
    
    async def _listen_can_messages(self):
        """CAN bus üzerindeki mesajları dinle"""
        logger.info(f"[{self.id}] CAN mesaj dinleyici başlatıldı")
        
        while self.running:
            try:
                # CAN mesajını al (non-blocking)
                msg = self.can_bus.recv(timeout=0.1)
                if msg:
                    await self._handle_can_message(msg)
            except can.CanError as e:
                if self.running:
                    logger.error(f"[{self.id}] CAN hata: {e}")
            except Exception as e:
                if self.running:
                    logger.error(f"[{self.id}] CAN dinleme hatası: {e}")
    
    async def _handle_can_message(self, msg: can.Message):
        """CAN mesajını işle"""
        can_id = msg.arbitration_id
        payload = msg.data
        
        logger.info(f"[{self.id}] CAN mesajı alındı: ID={hex(can_id)}, Data={payload.hex()}")
        
        # MeterValues mesajı (0x300) - charger modülünden gelir
        if can_id == 0x300:
            ocpp_payload = self.gateway.can_to_ocpp(can_id, payload)
            if ocpp_payload:
                connector_id = ocpp_payload.get('connector_id', 1)
                energy = ocpp_payload.get('energy', 0)
                self.connectors[connector_id]['energy'] = energy
                
                # CSMS'e MeterValues gönder
                await self._send_meter_values(connector_id, energy)
        
        # StatusNotification mesajı (0x301)
        elif can_id == 0x301:
            ocpp_payload = self.gateway.can_to_ocpp(can_id, payload)
            if ocpp_payload:
                connector_id = ocpp_payload.get('connector_id', 1)
                status = ocpp_payload.get('status', 'Available')
                self.connectors[connector_id]['status'] = status
                
                # CSMS'e StatusNotification gönder
                await self._send_status_notification(connector_id, status)
    
    async def _send_can_message(self, can_id: int, payload: bytes):
        """CAN bus üzerine mesaj gönder"""
        try:
            msg = can.Message(arbitration_id=can_id, data=payload, is_extended_id=False)
            self.can_bus.send(msg)
            logger.info(f"[{self.id}] CAN mesajı gönderildi: ID={hex(can_id)}, Data={payload.hex()}")
        except Exception as e:
            logger.error(f"[{self.id}] CAN gönderme hatası: {e}")
    
    async def _send_meter_values(self, connector_id: int, energy: int):
        """CSMS'e MeterValues gönder"""
        try:
            meter_value = [{
                'timestamp': datetime.utcnow().isoformat(),
                'sampledValue': [{
                    'value': str(energy),
                    'context': 'Sample.Periodic',
                    'format': 'Raw',
                    'measurand': 'Energy.Active.Import.Register',
                    'unit': 'Wh'
                }]
            }]
            
            await self.call(call.MeterValues(
                connector_id=connector_id,
                meter_value=meter_value
            ))
        except Exception as e:
            logger.error(f"[{self.id}] MeterValues gönderme hatası: {e}")
    
    async def _send_status_notification(self, connector_id: int, status: str):
        """CSMS'e StatusNotification gönder"""
        try:
            status_enum = ChargePointStatus[status] if hasattr(ChargePointStatus, status) else ChargePointStatus.available
            await self.call(call.StatusNotification(
                connector_id=connector_id,
                error_code='NoError',
                status=status_enum
            ))
        except Exception as e:
            logger.error(f"[{self.id}] StatusNotification gönderme hatası: {e}")
    
    # OCPP Message Handlers
    
    @on(Action.remote_start_transaction)
    def on_remote_start_transaction(self, connector_id, id_tag, **kwargs):
        """RemoteStartTransaction mesajını işle ve CAN'a gönder"""
        logger.info(f"[{self.id}] RemoteStartTransaction alındı - Connector: {connector_id}, Tag: {id_tag}")
        
        # OCPP → CAN dönüşümü
        can_frame = self.gateway.ocpp_to_can('RemoteStartTransaction', {
            'cp_id': int(self.id.split('_')[-1]) if '_' in self.id else 1,
            'connector_id': connector_id
        })
        
        if can_frame:
            can_id, payload = can_frame
            asyncio.create_task(self._send_can_message(can_id, payload))
            
            # Compromised firmware simülasyonu
            if self.compromised:
                logger.warning(f"[{self.id}] ⚠️ COMPROMISED: Ek CAN frame gönderiliyor (0x9FF)")
                malicious_payload = b'\xFF' * 8
                asyncio.create_task(self._send_can_message(0x9FF, malicious_payload))
        
        # Transaction başlat
        transaction_id = len(self.connectors) + 1
        self.connectors[connector_id]['transaction_id'] = transaction_id
        self.connectors[connector_id]['status'] = 'Charging'
        
        return call_result.RemoteStartTransaction(status='Accepted')
    
    @on(Action.remote_stop_transaction)
    def on_remote_stop_transaction(self, transaction_id, **kwargs):
        """RemoteStopTransaction mesajını işle ve CAN'a gönder"""
        logger.info(f"[{self.id}] RemoteStopTransaction alındı - Transaction: {transaction_id}")
        
        # OCPP → CAN dönüşümü
        can_frame = self.gateway.ocpp_to_can('RemoteStopTransaction', {
            'transaction_id': transaction_id
        })
        
        if can_frame:
            can_id, payload = can_frame
            asyncio.create_task(self._send_can_message(can_id, payload))
        
        # Transaction durdur
        for conn_id, conn in self.connectors.items():
            if conn['transaction_id'] == transaction_id:
                conn['transaction_id'] = None
                conn['status'] = 'Available'
                break
        
        return call_result.RemoteStopTransaction(status='Accepted')
    
    @on(Action.set_charging_profile)
    def on_set_charging_profile(self, connector_id, cs_charging_profiles, **kwargs):
        """SetChargingProfile mesajını işle ve CAN'a gönder"""
        logger.info(f"[{self.id}] SetChargingProfile alındı - Connector: {connector_id}")
        
        # Charging profile'dan max_current'ı al
        max_current = 16.0  # Default
        if cs_charging_profiles and 'chargingSchedule' in cs_charging_profiles:
            schedule = cs_charging_profiles['chargingSchedule']
            if 'chargingRateUnit' in schedule and schedule['chargingRateUnit'] == 'A':
                if 'chargingSchedulePeriod' in schedule and len(schedule['chargingSchedulePeriod']) > 0:
                    max_current = schedule['chargingSchedulePeriod'][0].get('limit', 16.0)
        
        # OCPP → CAN dönüşümü
        can_frame = self.gateway.ocpp_to_can('SetChargingProfile', {
            'profile_id': cs_charging_profiles.get('chargingProfileId', 1),
            'max_current': max_current
        })
        
        if can_frame:
            can_id, payload = can_frame
            asyncio.create_task(self._send_can_message(can_id, payload))
        
        return call_result.SetChargingProfile(status='Accepted')
    
    async def send_boot_notification(self):
        """CSMS'e BootNotification gönder"""
        logger.info(f"[{self.id}] BootNotification gönderiliyor...")
        
        response = await self.call(call.BootNotification(
            charge_point_model="Simulator",
            charge_point_vendor="TestVendor"
        ))
        
        logger.info(f"[{self.id}] BootNotification yanıtı: {response}")
        
        # BootNotification'ı CAN'a da gönder (opsiyonel)
        can_frame = self.gateway.ocpp_to_can('BootNotification', {
            'cp_id': int(self.id.split('_')[-1]) if '_' in self.id else 1,
            'model': 'Simulator'
        })
        
        if can_frame:
            can_id, payload = can_frame
            await self._send_can_message(can_id, payload)
        
        return response
    
    def stop(self):
        """CP'yi durdur"""
        self.running = False
        if self.can_bus:
            self.can_bus.shutdown()
        logger.info(f"[{self.id}] Charge Point durduruldu")


async def main():
    """Ana fonksiyon - CP simülatörünü başlat"""
    import sys
    
    cp_id = sys.argv[1] if len(sys.argv) > 1 else "CP001"
    csms_url = sys.argv[2] if len(sys.argv) > 2 else "ws://localhost:9000"
    compromised = '--compromised' in sys.argv
    
    logger.info(f"Charge Point Simülatörü başlatılıyor...")
    logger.info(f"CP ID: {cp_id}")
    logger.info(f"CSMS URL: {csms_url}")
    logger.info(f"Compromised mode: {compromised}")
    
    try:
        async with websockets.connect(
            f"{csms_url}/{cp_id}",
            subprotocols=['ocpp1.6']
        ) as ws:
            cp = ChargePointSimulator(cp_id, ws, compromised=compromised)
            
            # BootNotification gönder
            await asyncio.sleep(1)
            await cp.send_boot_notification()
            
            # StatusNotification gönder
            await cp._send_status_notification(1, 'Available')
            
            # CP'yi başlat
            await cp.start()
            
    except KeyboardInterrupt:
        logger.info("CP simülatörü kapatılıyor...")
        cp.stop()
    except Exception as e:
        logger.error(f"Bağlantı hatası: {e}")
        logger.info("CSMS simülatörünün çalıştığından emin olun: python csms_simulator.py")


if __name__ == "__main__":
    asyncio.run(main())

