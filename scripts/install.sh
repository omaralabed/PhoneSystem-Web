#!/bin/bash
# PhoneSystem-Web Installation Script
# Installs all dependencies and sets up the system

set -e

echo "========================================="
echo "PhoneSystem-Web Installation"
echo "========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run as root. Run as normal user."
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Project directory: $PROJECT_DIR"

# Update system
echo ""
echo "Updating system packages..."
sudo apt-get update

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    baresip \
    alsa-utils \
    chromium-browser \
    unclutter \
    git

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
cd "$PROJECT_DIR"
python3 -m venv venv

# Activate and install Python packages
echo ""
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copy systemd service
echo ""
echo "Installing systemd service..."
sudo cp "$PROJECT_DIR/systemd/phonesystem.service" /etc/systemd/system/
sudo sed -i "s|/home/pi/PhoneSystem-Web|$PROJECT_DIR|g" /etc/systemd/system/phonesystem.service
sudo systemctl daemon-reload

# Set up passwordless sudo for network script
echo ""
echo "Setting up passwordless sudo for network script..."
SUDO_RULE="$USER ALL=(ALL) NOPASSWD: $PROJECT_DIR/scripts/update_network.sh"
echo "$SUDO_RULE" | sudo tee /etc/sudoers.d/phonesystem > /dev/null
sudo chmod 0440 /etc/sudoers.d/phonesystem

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x "$PROJECT_DIR"/scripts/*.sh

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "To start the service:"
echo "  sudo systemctl start phonesystem"
echo "  sudo systemctl enable phonesystem"
echo ""
echo "To set up kiosk mode (auto-start browser):"
echo "  ./scripts/setup_kiosk.sh"
echo ""
echo "Access the system at:"
echo "  http://localhost:5000 (on Pi)"
echo "  http://$(hostname -I | awk '{print $1}'):5000 (from network)"
echo ""
