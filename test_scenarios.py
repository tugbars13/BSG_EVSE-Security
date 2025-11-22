#!/usr/bin/env python3
"""
Test Senaryoları ve Örnek Kullanım
Tüm sistemin uçtan uca test edilmesi için senaryolar.
"""

import asyncio
import logging
import time
import json
import websockets
from websockets.client import connect

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def scenario_normal_flow():
    """Senaryo: Normal akış - CSMS → CP → CAN → Charger"""
    logger.info("\n" + "="*60)
    logger.info("SENARYO: Normal Akış Testi")
    logger.info("="*60)
    
    logger.info("\nBu senaryo için 3 terminal açın:")
    logger.info("Terminal 1: python csms_simulator.py")
    logger.info("Terminal 2: python cp_simulator.py CP001")
    logger.info("Terminal 3: python can_bus_simulator.py")
    logger.info("\nBeklenen akış:")
    logger.info("1. CP, CSMS'e BootNotification gönderir")
    logger.info("2. CSMS, CP'ye RemoteStartTransaction gönderir")
    logger.info("3. CP, CAN bus üzerine 0x200 frame'i gönderir")
    logger.info("4. Charger modülü şarjı başlatır ve 0x300 (MeterValues) gönderir")
    logger.info("5. CP, CSMS'e MeterValues iletir")
    logger.info("6. CSMS, CP'ye RemoteStopTransaction gönderir")
    logger.info("7. CP, CAN bus üzerine 0x201 frame'i gönderir")
    logger.info("8. Charger modülü şarjı durdurur\n")


async def scenario_mitm_attack():
    """Senaryo: MitM saldırısı"""
    logger.info("\n" + "="*60)
    logger.info("SENARYO: MitM Saldırısı Testi")
    logger.info("="*60)
    
    logger.info("\nBu senaryo için 4 terminal açın:")
    logger.info("Terminal 1: python csms_simulator.py")
    logger.info("Terminal 2: python attack_scenarios.py --scenario 1")
    logger.info("Terminal 3: python cp_simulator.py CP001 ws://localhost:9001")
    logger.info("Terminal 4: python can_bus_simulator.py")
    logger.info("\nBeklenen davranış:")
    logger.info("1. Normal akış başlar")
    logger.info("2. MitM proxy, RemoteStartTransaction'ı yakalar")
    logger.info("3. Proxy, mesajı RemoteStopTransaction'a çevirir")
    logger.info("4. CP, yanlış komutu alır ve şarjı durdurur")
    logger.info("5. Güvenlik açığı gösterilmiş olur\n")


async def scenario_compromised_firmware():
    """Senaryo: Compromised firmware"""
    logger.info("\n" + "="*60)
    logger.info("SENARYO: Compromised Firmware Testi")
    logger.info("="*60)
    
    logger.info("\nBu senaryo için 4 terminal açın:")
    logger.info("Terminal 1: python csms_simulator.py")
    logger.info("Terminal 2: python cp_simulator.py CP001 ws://localhost:9000 --compromised")
    logger.info("Terminal 3: python can_bus_simulator.py")
    logger.info("Terminal 4: python defense_mechanisms.py --ids")
    logger.info("\nBeklenen davranış:")
    logger.info("1. Normal akış başlar")
    logger.info("2. Compromised CP, ek olarak 0x9FF malicious frame gönderir")
    logger.info("3. CAN-IDS, malicious frame'i tespit eder ve alarm üretir")
    logger.info("4. Charger modülü hatalı davranış moduna geçer")
    logger.info("5. Güvenlik açığı ve savunma mekanizması gösterilmiş olur\n")


async def scenario_defense_comparison():
    """Senaryo: Savunma mekanizmaları karşılaştırması"""
    logger.info("\n" + "="*60)
    logger.info("SENARYO: Savunma Mekanizmaları Karşılaştırması")
    logger.info("="*60)
    
    logger.info("\nBu senaryo için:")
    logger.info("python defense_mechanisms.py --compare")
    logger.info("\nGüvenli ve güvensiz gateway'in farkını gösterir\n")


async def interactive_csms_commands():
    """İnteraktif CSMS komut gönderme"""
    logger.info("\n" + "="*60)
    logger.info("İNTERAKTİF CSMS KOMUTLARI")
    logger.info("="*60)
    
    csms_url = "ws://localhost:9000"
    cp_id = "CP001"
    
    try:
        async with connect(f"{csms_url}/{cp_id}", subprotocols=['ocpp1.6']) as ws:
            logger.info(f"CSMS'e bağlandı: {csms_url}/{cp_id}")
            
            # BootNotification
            logger.info("\n1. BootNotification gönderiliyor...")
            boot_msg = json.dumps([2, "boot-1", "BootNotification", {
                "chargePointModel": "TestModel",
                "chargePointVendor": "TestVendor"
            }])
            await ws.send(boot_msg)
            response = await ws.recv()
            logger.info(f"Yanıt: {response[:200]}...")
            
            await asyncio.sleep(2)
            
            # RemoteStartTransaction
            logger.info("\n2. RemoteStartTransaction gönderiliyor...")
            start_msg = json.dumps([2, "start-1", "RemoteStartTransaction", {
                "connectorId": 1,
                "idTag": "TEST_TAG"
            }])
            await ws.send(start_msg)
            response = await ws.recv()
            logger.info(f"Yanıt: {response[:200]}...")
            
            await asyncio.sleep(5)
            
            # RemoteStopTransaction
            logger.info("\n3. RemoteStopTransaction gönderiliyor...")
            stop_msg = json.dumps([2, "stop-1", "RemoteStopTransaction", {
                "transactionId": 1
            }])
            await ws.send(stop_msg)
            response = await ws.recv()
            logger.info(f"Yanıt: {response[:200]}...")
            
            logger.info("\nTest tamamlandı!")
            
    except Exception as e:
        logger.error(f"Bağlantı hatası: {e}")
        logger.info("CSMS simülatörünün çalıştığından emin olun: python csms_simulator.py")


async def monitor_can_traffic():
    """CAN trafiğini izle"""
    import can
    
    logger.info("\n" + "="*60)
    logger.info("CAN TRAFİK İZLEME")
    logger.info("="*60)
    
    try:
        bus = can.interface.Bus('vcan0', bustype='socketcan')
        logger.info("CAN bus bağlantısı kuruldu: vcan0")
        logger.info("CAN mesajlarını dinliyor... (Ctrl+C ile durdurun)\n")
        
        message_count = 0
        start_time = time.time()
        
        while True:
            msg = bus.recv(timeout=1.0)
            if msg:
                message_count += 1
                elapsed = time.time() - start_time
                rate = message_count / elapsed if elapsed > 0 else 0
                
                logger.info(f"[{message_count}] CAN ID: {hex(msg.arbitration_id)}, "
                          f"Data: {msg.data.hex()}, "
                          f"Rate: {rate:.2f} msg/s")
            else:
                logger.debug("Timeout (normal)")
                
    except KeyboardInterrupt:
        logger.info("\nİzleme durduruldu")
        bus.shutdown()
    except Exception as e:
        logger.error(f"Hata: {e}")


async def main():
    """Ana fonksiyon"""
    import sys
    
    if len(sys.argv) > 1:
        scenario = sys.argv[1]
        
        if scenario == '--normal' or scenario == '-n':
            await scenario_normal_flow()
        elif scenario == '--mitm' or scenario == '-m':
            await scenario_mitm_attack()
        elif scenario == '--compromised' or scenario == '-c':
            await scenario_compromised_firmware()
        elif scenario == '--defense' or scenario == '-d':
            await scenario_defense_comparison()
        elif scenario == '--interactive' or scenario == '-i':
            await interactive_csms_commands()
        elif scenario == '--monitor' or scenario == '-mon':
            await monitor_can_traffic()
        else:
            logger.error(f"Bilinmeyen senaryo: {scenario}")
    else:
        logger.info("Kullanım:")
        logger.info("  python test_scenarios.py --normal        # Normal akış")
        logger.info("  python test_scenarios.py --mitm          # MitM saldırısı")
        logger.info("  python test_scenarios.py --compromised   # Compromised firmware")
        logger.info("  python test_scenarios.py --defense       # Savunma karşılaştırması")
        logger.info("  python test_scenarios.py --interactive   # İnteraktif komutlar")
        logger.info("  python test_scenarios.py --monitor       # CAN trafik izleme")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Kapatılıyor...")

