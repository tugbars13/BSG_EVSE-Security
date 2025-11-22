#!/usr/bin/env python3
"""
CSMS (Central System Management System) Simülatörü
OCPP protokolü üzerinden Charge Point'lere komut gönderir.
"""

import asyncio
import logging
from datetime import datetime
from ocpp.v16 import ChargePoint as CP
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.routing import on
from ocpp.v16 import call_result, call

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CentralSystem:
    """Merkezi yönetim sistemi simülatörü"""
    
    def __init__(self):
        self.charge_points = {}
        self.transactions = {}
        
    async def register_charge_point(self, charge_point_id: str, websocket):
        """Charge Point'i kaydet"""
        cp = ChargePoint(charge_point_id, websocket)
        self.charge_points[charge_point_id] = cp
        logger.info(f"Charge Point kaydedildi: {charge_point_id}")
        return cp


class ChargePoint(CP):
    """Charge Point bağlantısını temsil eden sınıf"""
    
    def __init__(self, id, connection):
        super().__init__(id, connection)
        self.id = id
        self.registered = False
        
    @on(Action.boot_notification)
    def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
        """BootNotification mesajını işle"""
        logger.info(f"[{self.id}] BootNotification alındı - Model: {charge_point_model}, Vendor: {charge_point_vendor}")
        self.registered = True
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=300,
            status=RegistrationStatus.accepted
        )
    
    @on(Action.status_notification)
    def on_status_notification(self, connector_id, status, **kwargs):
        """StatusNotification mesajını işle"""
        logger.info(f"[{self.id}] StatusNotification - Connector {connector_id}: {status}")
        return call_result.StatusNotification()
    
    @on(Action.meter_values)
    def on_meter_values(self, connector_id, meter_value, **kwargs):
        """MeterValues mesajını işle"""
        for value in meter_value:
            if 'sampledValue' in value:
                for sv in value['sampledValue']:
                    if 'value' in sv:
                        logger.info(f"[{self.id}] MeterValues - Connector {connector_id}: {sv['value']} {sv.get('unit', 'Wh')}")
        return call_result.MeterValues()
    
    @on(Action.start_transaction)
    def on_start_transaction(self, connector_id, id_tag, meter_start, **kwargs):
        """StartTransaction mesajını işle"""
        transaction_id = kwargs.get('transaction_id', 1)
        logger.info(f"[{self.id}] StartTransaction - Connector {connector_id}, Tag: {id_tag}, Transaction: {transaction_id}")
        return call_result.StartTransaction(
            transaction_id=transaction_id,
            id_tag_info={'status': 'Accepted'}
        )
    
    @on(Action.stop_transaction)
    def on_stop_transaction(self, transaction_id, id_tag, meter_stop, **kwargs):
        """StopTransaction mesajını işle"""
        logger.info(f"[{self.id}] StopTransaction - Transaction: {transaction_id}, Meter: {meter_stop}")
        return call_result.StopTransaction(
            id_tag_info={'status': 'Accepted'}
        )
    
    async def send_remote_start_transaction(self, connector_id, id_tag="TEST_TAG"):
        """RemoteStartTransaction komutu gönder"""
        logger.info(f"[{self.id}] RemoteStartTransaction gönderiliyor - Connector: {connector_id}")
        response = await self.call(call.RemoteStartTransaction(
            connector_id=connector_id,
            id_tag=id_tag
        ))
        logger.info(f"[{self.id}] RemoteStartTransaction yanıtı: {response}")
        return response
    
    async def send_remote_stop_transaction(self, transaction_id):
        """RemoteStopTransaction komutu gönder"""
        logger.info(f"[{self.id}] RemoteStopTransaction gönderiliyor - Transaction: {transaction_id}")
        response = await self.call(call.RemoteStopTransaction(
            transaction_id=transaction_id
        ))
        logger.info(f"[{self.id}] RemoteStopTransaction yanıtı: {response}")
        return response
    
    async def send_set_charging_profile(self, connector_id, charging_profile):
        """SetChargingProfile komutu gönder"""
        logger.info(f"[{self.id}] SetChargingProfile gönderiliyor - Connector: {connector_id}")
        response = await self.call(call.SetChargingProfile(
            connector_id=connector_id,
            cs_charging_profiles=charging_profile
        ))
        logger.info(f"[{self.id}] SetChargingProfile yanıtı: {response}")
        return response


async def on_connect(websocket, path=None):
    """Yeni WebSocket bağlantısı geldiğinde çağrılır"""
    try:
        logger.info(f"Yeni bağlantı: {websocket.remote_address}")
        
        # Charge Point ID'yi path'ten al veya varsayılan oluştur
        if path:
            charge_point_id = path.strip('/') if path else None
        else:
            charge_point_id = None
        
        if not charge_point_id:
            # IP'den CP ID oluştur
            addr = websocket.remote_address[0] if hasattr(websocket, 'remote_address') else '127.0.0.1'
            charge_point_id = f"CP_{addr.replace('.', '_')}"
        
        logger.info(f"Charge Point ID: {charge_point_id}")
        
        cs = CentralSystem()
        cp = await cs.register_charge_point(charge_point_id, websocket)
        
        await cp.start()
        
    except Exception as e:
        logger.error(f"Bağlantı hatası: {e}")
        import traceback
        logger.error(traceback.format_exc())


async def main():
    """Ana fonksiyon - CSMS WebSocket sunucusunu başlat"""
    import websockets
    
    logger.info("CSMS Simülatörü başlatılıyor...")
    logger.info("WebSocket sunucusu: ws://localhost:9000")
    
    server = await websockets.serve(
        on_connect,
        "localhost",
        9000,
        subprotocols=['ocpp1.6']
    )
    
    logger.info("CSMS hazır! Charge Point bağlantılarını bekliyor...")
    
    # Örnek komut gönderme (test için)
    await asyncio.sleep(2)
    logger.info("\n=== Test Senaryosu ===")
    logger.info("Manuel komut göndermek için CP simülatörünü başlatın ve bekleyin...")
    
    await server.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("CSMS simülatörü kapatılıyor...")

