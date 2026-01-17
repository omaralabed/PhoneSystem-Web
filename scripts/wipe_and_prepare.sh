#!/bin/bash
# Script to wipe old PyQt5 phone system and prepare for web-based system

set -e  # Exit on error

echo "=========================================="
echo "Raspberry Pi Cleanup & Preparation Script"
echo "=========================================="
echo ""

# Stop old services
echo "1. Stopping old phone system service..."
sudo systemctl stop phonesystem 2>/dev/null || true
sudo systemctl disable phonesystem 2>/dev/null || true

# Remove old systemd service
echo "2. Removing old systemd service..."
sudo rm -f /etc/systemd/system/phonesystem.service
sudo systemctl daemon-reload

# Kill any running Python phone system processes
echo "3. Killing old phone system processes..."
sudo pkill -f "main.py" 2>/dev/null || true
sudo pkill -f "python.*ProComm" 2>/dev/null || true

# Remove old project directory
echo "4. Removing old ProComm directory..."
sudo rm -rf /home/pi/ProComm 2>/dev/null || true
sudo rm -rf /home/pi/Desktop/ProComm 2>/dev/null || true

# Remove old kiosk autostart (if exists)
echo "5. Cleaning up old autostart entries..."
rm -rf ~/.config/autostart/phonesystem.desktop 2>/dev/null || true
rm -rf /home/pi/.config/autostart/phonesystem.desktop 2>/dev/null || true

# Clean up old Python virtual environments
echo "6. Removing old virtual environments..."
rm -rf ~/venv 2>/dev/null || true
rm -rf /home/pi/venv 2>/dev/null || true

# Remove old cron jobs (if any)
echo "7. Checking for old cron jobs..."
crontab -l 2>/dev/null | grep -v "ProComm\|phonesystem" | crontab - 2>/dev/null || true

# Clean up package cache
echo "8. Cleaning package cache..."
sudo apt-get autoremove -y
sudo apt-get autoclean

# Verify cleanup
echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
echo ""
echo "Verification:"
echo "  - Old service stopped: $(systemctl is-active phonesystem 2>/dev/null || echo 'not running')"
echo "  - ProComm directory: $([ -d /home/pi/ProComm ] && echo 'still exists (ERROR)' || echo 'removed ✓')"
echo "  - Python processes: $(pgrep -f 'main.py|ProComm' | wc -l) running"
echo ""
echo "System is ready for new installation!"
echo ""
echo "Next steps:"
echo "  1. Copy PhoneSystem-Web to /home/pi/"
echo "  2. Run: cd /home/pi/PhoneSystem-Web"
echo "  3. Run: chmod +x scripts/install.sh"
echo "  4. Run: ./scripts/install.sh"
echo ""
