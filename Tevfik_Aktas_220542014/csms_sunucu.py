import asyncio
import logging
from datetime import datetime

from ocpp.routing import on
from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call_result 
from ocpp.v16.enums import Action, RegistrationStatus
from websockets.server import serve

logging.basicConfig(level=logging.INFO)

connected_cps = {}
connected_websockets = {}

class SimpleChargePoint(CP):
    
    # İstek (Action) küçük harfli
    @on(Action.boot_notification)
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        logging.info(f"İstasyon {self.id} bağlandı (BootNotification).")
        connected_cps[self.id] = self
        connected_websockets[self.id] = getattr(self, "_websocket", None)
        
        # DÜZELTME: Cevap (Result) 'call_result' ile ve Büyük Harfli
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=300,
            status=RegistrationStatus.accepted,
        )

    @on(Action.status_notification)
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        logging.info(f"İstasyon {self.id} (Konnektör {connector_id}) yeni durum bildirdi: {status}")
        
        # DÜZELTME: Cevap (Result) 'call_result' ile ve Büyük Harfli
        return call_result.StatusNotification()

    @on(Action.heartbeat)
    async def on_heartbeat(self, **kwargs):
        logging.info(f"İstasyon {self.id} 'den Heartbeat alındı.")
        
        # DÜZELTME: Cevap (Result) 'call_result' ile ve Büyük Harfli
        return call_result.Heartbeat(
            current_time=datetime.utcnow().isoformat()
        )

async def on_connect(websocket):
    try:
        path = getattr(websocket, "path", "/UNKNOWN")
        charge_point_id = path.strip("/")
        if not charge_point_id:
             charge_point_id = "UNKNOWN"

        if charge_point_id in connected_websockets:
            logging.warning(f"UYARI: {charge_point_id} ile yeni bağlantı. Eski bağlantı kapatılıyor.")
            try:
                old_ws = connected_websockets.get(charge_point_id)
                if old_ws:
                    await old_ws.close()
            except Exception as e:
                logging.exception(f"Eski websocket ({charge_point_id}) kapatılırken hata: {e}")
        
        cp_obj = SimpleChargePoint(charge_point_id, websocket)
        logging.info(f"Yeni bağlantı: {charge_point_id} (path={path})")
        await cp_obj.start()

    except Exception as e:
        logging.error(f"Bağlantı hatası: {e}")
    finally:
        cp_id = locals().get('charge_point_id', 'UNKNOWN')
        connected_cps.pop(cp_id, None)
        connected_websockets.pop(cp_id, None)
        logging.info(f"Bağlantı kesildi: {cp_id}")


async def main():
    server = await serve(on_connect, "0.0.0.0", 9000, subprotocols=["ocpp1.6"])
    logging.info("CSMS Sunucusu 9000 portunda başlatıldı...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
