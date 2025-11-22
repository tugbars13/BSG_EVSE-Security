#!/bin/bash
# Hızlı başlangıç scripti - Tüm bileşenleri başlatır

echo "=========================================="
echo "OCPP-CAN Bridge Simülasyonu - Hızlı Başlangıç"
echo "=========================================="
echo ""

# vcan0 kontrolü
if ! ip link show vcan0 &>/dev/null; then
    echo "vcan0 bulunamadı. Oluşturuluyor..."
    sudo ./setup_vcan.sh
    if [ $? -ne 0 ]; then
        echo "HATA: vcan0 oluşturulamadı!"
        exit 1
    fi
else
    echo "✓ vcan0 hazır"
fi

echo ""
echo "Başlatılacak bileşenler:"
echo "  1. CSMS Simülatörü (port 9000)"
echo "  2. CP Simülatörü (CP001)"
echo "  3. CAN Bus Simülatörü"
echo ""
echo "Her bileşen ayrı terminalde çalışacak."
echo ""

# Terminal 1: CSMS
echo "Terminal 1'de CSMS başlatılıyor..."
gnome-terminal -- bash -c "python3 csms_simulator.py; read -p 'Press Enter to close...'" 2>/dev/null || \
xterm -e "python3 csms_simulator.py; read -p 'Press Enter to close...'" 2>/dev/null || \
echo "Manuel olarak çalıştırın: python3 csms_simulator.py"

sleep 2

# Terminal 2: CP
echo "Terminal 2'de CP başlatılıyor..."
gnome-terminal -- bash -c "python3 cp_simulator.py CP001; read -p 'Press Enter to close...'" 2>/dev/null || \
xterm -e "python3 cp_simulator.py CP001; read -p 'Press Enter to close...'" 2>/dev/null || \
echo "Manuel olarak çalıştırın: python3 cp_simulator.py CP001"

sleep 2

# Terminal 3: CAN Bus
echo "Terminal 3'te CAN Bus başlatılıyor..."
gnome-terminal -- bash -c "python3 can_bus_simulator.py; read -p 'Press Enter to close...'" 2>/dev/null || \
xterm -e "python3 can_bus_simulator.py; read -p 'Press Enter to close...'" 2>/dev/null || \
echo "Manuel olarak çalıştırın: python3 can_bus_simulator.py"

echo ""
echo "Tüm bileşenler başlatıldı!"
echo "Logları kontrol etmek için terminal pencerelerini açın."
echo ""
echo "Test için: python3 test_scenarios.py --interactive"

