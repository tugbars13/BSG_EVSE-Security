#!/usr/bin/env python3
"""
OCPP → CAN Gateway
OCPP mesajlarını CAN frame'lerine dönüştürür.
"""

import logging
import struct
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CANGateway:
    """OCPP mesajlarını CAN frame'lerine dönüştüren gateway"""
    
    # CAN ID mapping (belgede belirtilen örnek ID'ler)
    CAN_IDS = {
        'RemoteStartTransaction': 0x200,
        'RemoteStopTransaction': 0x201,
        'SetChargingProfile': 0x210,
        'MeterValues': 0x300,
        'StatusNotification': 0x301,
        'BootNotification': 0x100,
    }
    
    def __init__(self, whitelist_enabled: bool = False):
        """
        Args:
            whitelist_enabled: Gateway filtreleme aktif mi?
        """
        self.whitelist_enabled = whitelist_enabled
        self.allowed_can_ids = set(self.CAN_IDS.values()) if whitelist_enabled else None
        self.stats = {
            'messages_processed': 0,
            'messages_blocked': 0,
            'messages_sent': 0
        }
        
    def ocpp_to_can(self, action: str, payload: Dict[str, Any]) -> Optional[tuple]:
        """
        OCPP mesajını CAN frame'ine dönüştür
        
        Returns:
            (can_id, payload_bytes) tuple veya None
        """
        self.stats['messages_processed'] += 1
        
        if action not in self.CAN_IDS:
            logger.warning(f"Bilinmeyen OCPP action: {action}")
            return None
        
        can_id = self.CAN_IDS[action]
        
        # Whitelist kontrolü
        if self.whitelist_enabled and can_id not in self.allowed_can_ids:
            logger.warning(f"CAN ID {hex(can_id)} whitelist'te değil, bloklandı!")
            self.stats['messages_blocked'] += 1
            return None
        
        try:
            payload_bytes = self._encode_payload(action, payload)
            self.stats['messages_sent'] += 1
            logger.info(f"OCPP → CAN: {action} → CAN ID {hex(can_id)}, Payload: {payload_bytes.hex()}")
            return (can_id, payload_bytes)
        except Exception as e:
            logger.error(f"Payload encoding hatası: {e}")
            return None
    
    def _encode_payload(self, action: str, payload: Dict[str, Any]) -> bytes:
        """OCPP payload'ını CAN frame payload'ına dönüştür"""
        
        if action == 'RemoteStartTransaction':
            # CAN ID 0x200: [cp_id (1 byte), connector_id (1 byte), start_cmd (1 byte)]
            cp_id = payload.get('cp_id', 1) & 0xFF
            connector_id = payload.get('connector_id', 1) & 0xFF
            start_cmd = 0x01  # Start command
            return struct.pack('BBB', cp_id, connector_id, start_cmd) + b'\x00' * 5
        
        elif action == 'RemoteStopTransaction':
            # CAN ID 0x201: [tx_id (4 bytes), stop_cmd (1 byte)]
            tx_id = payload.get('transaction_id', 0)
            stop_cmd = 0x00  # Stop command
            return struct.pack('<IB', tx_id, stop_cmd) + b'\x00' * 3
        
        elif action == 'SetChargingProfile':
            # CAN ID 0x210: [profile_id (2 bytes), max_current (2 bytes)]
            profile_id = payload.get('profile_id', 1) & 0xFFFF
            max_current = int(payload.get('max_current', 16) * 10) & 0xFFFF  # 0.1A resolution
            return struct.pack('<HH', profile_id, max_current) + b'\x00' * 4
        
        elif action == 'MeterValues':
            # CAN ID 0x300: [connector_id (1 byte), energy (4 bytes, Wh), timestamp (2 bytes)]
            connector_id = payload.get('connector_id', 1) & 0xFF
            energy = int(payload.get('energy', 0)) & 0xFFFFFFFF
            timestamp = payload.get('timestamp', 0) & 0xFFFF
            return struct.pack('<BIBH', connector_id, energy, timestamp)
        
        elif action == 'StatusNotification':
            # CAN ID 0x301: [connector_id (1 byte), status (1 byte)]
            connector_id = payload.get('connector_id', 1) & 0xFF
            status_map = {'Available': 0x01, 'Preparing': 0x02, 'Charging': 0x03, 
                         'SuspendedEVSE': 0x04, 'SuspendedEV': 0x05, 'Finishing': 0x06,
                         'Reserved': 0x07, 'Unavailable': 0x08, 'Faulted': 0x09}
            status = status_map.get(payload.get('status', 'Available'), 0x00) & 0xFF
            return struct.pack('BB', connector_id, status) + b'\x00' * 6
        
        elif action == 'BootNotification':
            # CAN ID 0x100: [cp_id (1 byte), model_len (1 byte), model (max 6 bytes)]
            cp_id = payload.get('cp_id', 1) & 0xFF
            model = payload.get('model', 'TEST').encode('ascii')[:6]
            model_len = len(model) & 0xFF
            return struct.pack('BB', cp_id, model_len) + model.ljust(6, b'\x00')
        
        else:
            return b'\x00' * 8
    
    def can_to_ocpp(self, can_id: int, payload: bytes) -> Optional[Dict[str, Any]]:
        """
        CAN frame'ini OCPP mesajına dönüştür (ters yön)
        
        Returns:
            OCPP payload dict veya None
        """
        try:
            # CAN ID'den action'ı bul
            action = None
            for act, cid in self.CAN_IDS.items():
                if cid == can_id:
                    action = act
                    break
            
            if not action:
                logger.warning(f"Bilinmeyen CAN ID: {hex(can_id)}")
                return None
            
            return self._decode_payload(action, payload)
        except Exception as e:
            logger.error(f"CAN → OCPP decode hatası: {e}")
            return None
    
    def _decode_payload(self, action: str, payload: bytes) -> Dict[str, Any]:
        """CAN frame payload'ını OCPP payload'ına dönüştür"""
        
        if action == 'MeterValues':
            # CAN ID 0x300: [connector_id, energy, timestamp]
            if len(payload) >= 8:
                connector_id, energy, timestamp = struct.unpack('<BIBH', payload[:8])
                return {
                    'connector_id': connector_id,
                    'energy': energy,
                    'timestamp': timestamp
                }
        
        elif action == 'StatusNotification':
            # CAN ID 0x301: [connector_id, status]
            if len(payload) >= 2:
                connector_id, status_byte = struct.unpack('BB', payload[:2])
                status_map = {0x01: 'Available', 0x02: 'Preparing', 0x03: 'Charging',
                             0x04: 'SuspendedEVSE', 0x05: 'SuspendedEV', 0x06: 'Finishing',
                             0x07: 'Reserved', 0x08: 'Unavailable', 0x09: 'Faulted'}
                status = status_map.get(status_byte, 'Unknown')
                return {
                    'connector_id': connector_id,
                    'status': status
                }
        
        return {}
    
    def get_stats(self) -> Dict[str, int]:
        """Gateway istatistiklerini döndür"""
        return self.stats.copy()
    
    def enable_whitelist(self, allowed_ids: set = None):
        """Whitelist filtrelemeyi aktif et"""
        self.whitelist_enabled = True
        if allowed_ids:
            self.allowed_can_ids = allowed_ids
        else:
            self.allowed_can_ids = set(self.CAN_IDS.values())
        logger.info(f"Whitelist aktif edildi: {[hex(id) for id in self.allowed_can_ids]}")
    
    def disable_whitelist(self):
        """Whitelist filtrelemeyi kapat"""
        self.whitelist_enabled = False
        logger.info("Whitelist kapatıldı")

