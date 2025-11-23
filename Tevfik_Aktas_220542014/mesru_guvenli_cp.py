import asyncio
import logging
import ssl # GÜVENLİK İÇİN BU MODÜL EKLENDİ

from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call
from ocpp.v16.enums import ChargePointStatus, ChargePointErrorCode
import websockets

logging.basicConfig(level=logging.INFO)

class MesruGuvenliChargePoint(CP): # İsim değişikliği

    async def send_boot_notification(self):
        req = call.BootNotification(
            charge_point_model="Model-XYZ",
            charge_point_vendor="Vendor-ABC",
        )
        try:
            resp = await self.call(req)
            status = getattr(resp, "status", None)

            if isinstance(status, str) and status.lower() == "accepted":
                logging.info("Sunucu bizi kabul etti (BootNotification).")
                await self.send_status_notification()
            else:
                logging.warning(f"Sunucu bizi reddetti veya beklenmeyen cevap: {resp}")
        except Exception as e:
            logging.error(f"BootNotification hatası: {e}")

    async def send_status_notification(self):
        try:
            await self.call(call.StatusNotification(
                connector_id=1,
                error_code=ChargePointErrorCode.no_error,
                status=ChargePointStatus.available
            ))
            logging.info("Durum bildirimi (Available) gönderildi.")
        except Exception as e:
            logging.error(f"StatusNotification hatası: {e}")

    async def heartbeat_loop(self):
        while True:
            await asyncio.sleep(30)
            try:
                await self.call(call.Heartbeat())
                logging.info("Heartbeat gönderildi.")
            except Exception as e:
                logging.error(f"Heartbeat hatası: {e}")
                break

async def main():
    # --- GÜVENLİK (mTLS) KONFİGÜRASYONU BAŞLANGIÇ ---
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

    # 1. Sunucuyu doğrulamak için "Pasaport Ofisi"ni (CA) yükle
    ssl_context.load_verify_locations(cafile="ca.crt")

    # 2. Sunucuya sunmak için KENDİ kimliğimizi (client.crt) yükle
    ssl_context.load_cert_chain(certfile="client.crt", keyfile="client.key")
    # --- GÜVENLİK KONFİGÜRASYONU BİTİŞ ---

    uri = "wss://localhost:9000/CP_001" # PROTOKOL 'wss://' OLARAK DEĞİŞTİ
    try:
        # Güvenli 'wss://' ve 'ssl=ssl_context' ile bağlan
        async with websockets.connect(uri, 
                                      subprotocols=["ocpp1.6"], 
                                      ssl=ssl_context) as ws:

            cp = MesruGuvenliChargePoint("CP_001", ws)
            tasks = [
                asyncio.create_task(cp.start()),
                asyncio.create_task(cp.send_boot_notification()),
                asyncio.create_task(cp.heartbeat_loop()),
            ]
            await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"GÜVENLİ CP: Bağlantı hatası veya genel hata: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Meşru Güvenli CP kapatıldı.")
