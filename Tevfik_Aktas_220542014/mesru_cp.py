# mesru_cp.py
import asyncio
import logging

from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call
from ocpp.v16.enums import ChargePointStatus, ChargePointErrorCode
import websockets

logging.basicConfig(level=logging.INFO)

class MesruChargePoint(CP):

    async def send_boot_notification(self):
        # ocpp 2.0.0: call.BootNotification (önceki BootNotificationPayload yerine)
        req = call.BootNotification(
            charge_point_model="Model-XYZ",
            charge_point_vendor="Vendor-ABC",
        )
        try:
            resp = await self.call(req)

            # resp farklı tiplerde gelebilir -> güvenli şekilde status elde et
            status = None
            if resp is None:
                status = None
            else:
                status = getattr(resp, "status", None)
                if status is None:
                    try:
                        # bazı versiyonlarda dict-benzeri gelebilir
                        status = resp.get("status")
                    except Exception:
                        status = None
                # bazı durumlarda enum veya objeyi string'e çevir
                if status is None:
                    try:
                        status = str(resp).lower()
                    except Exception:
                        status = None

            if isinstance(status, str) and status.lower() == "accepted":
                logging.info("Sunucu bizi kabul etti (BootNotification).")
                # Boot başarılıysa durum gönder
                await self.send_status_notification()
            else:
                logging.warning(f"Sunucu bizi reddetti veya beklenmeyen cevap: {resp}")
        except Exception as e:
            logging.error(f"BootNotification hatası: {e}")

    async def send_status_notification(self):
        try:
            # ocpp 2.0.0: call.StatusNotification
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
    uri = "ws://localhost:9000/CP_001"
    try:
        async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
            cp = MesruChargePoint("CP_001", ws)
            tasks = [
                asyncio.create_task(cp.start()),
                asyncio.create_task(cp.send_boot_notification()),
                asyncio.create_task(cp.heartbeat_loop()),
            ]
            await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Bağlantı hatası veya genel hata: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Meşru CP kapatıldı.")

