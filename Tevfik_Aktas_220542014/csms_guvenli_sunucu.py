import asyncio
import logging
import ssl # GÜVENLİK İÇİN BU MODÜL EKLENDİ
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

    @on(Action.boot_notification)
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        logging.info(f"İstasyon {self.id} bağlandı (BootNotification).")
        connected_cps[self.id] = self
        connected_websockets[self.id] = getattr(self, "_websocket", None)

        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=300,
            status=RegistrationStatus.accepted,
        )

    @on(Action.status_notification)
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        logging.info(f"İstasyon {self.id} (Konnektör {connector_id}) yeni durum bildirdi: {status}")
        return call_result.StatusNotification()

    @on(Action.heartbeat)
    async def on_heartbeat(self, **kwargs):
        logging.info(f"İstasyon {self.id} 'den Heartbeat alındı.")
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
        logging.info(f"Yeni GÜVENLİ bağlantı: {charge_point_id} (path={path})")
        await cp_obj.start()

    except Exception as e:
        logging.error(f"Bağlantı hatası: {e}")
    finally:
        cp_id = locals().get('charge_point_id', 'UNKNOWN')
        connected_cps.pop(cp_id, None)
        connected_websockets.pop(cp_id, None)
        logging.info(f"Bağlantı kesildi: {cp_id}")

async def main():
    # --- GÜVENLİK (mTLS) KONFİGÜRASYONU BAŞLANGIÇ ---
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    # 1. Sunucu kendi sertifikasını (kimliğini) yüklesin
    ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    # 2. İstemcileri doğrulamak için "Pasaport Ofisi"ni (CA) yükle
    ssl_context.load_verify_locations(cafile="ca.crt")

    # 3. İstemciden sertifika İSTE (Karşılıklı TLS - mTLS)
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    # --- GÜVENLİK KONFİGÜRASYONU BİTİŞ ---

    # Sunucuyu 'ssl=ssl_context' ile (Güvenli WSS) başlat
    server = await serve(on_connect, "0.0.0.0", 9000, 
                         subprotocols=["ocpp1.6"],
                         ssl=ssl_context)

    logging.info("GÜVENLİ CSMS Sunucusu 9000 portunda başlatıldı (wss://)...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
