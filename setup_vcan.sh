#!/bin/bash
# Sanal CAN (vcan0) kurulum scripti

echo "Sanal CAN arayüzü kuruluyor..."

# vcan modülünü yükle
sudo modprobe vcan

# vcan0 arayüzünü oluştur
sudo ip link add dev vcan0 type vcan 2>/dev/null || echo "vcan0 zaten mevcut"

# vcan0 arayüzünü aktif et
sudo ip link set up vcan0

# Durumu kontrol et
ip link show vcan0

echo "vcan0 hazır!"

