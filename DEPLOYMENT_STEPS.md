# Raspberry Pi Deployment Steps

Complete guide to wipe the old PyQt5 system and install the new web-based phone system.

## Step 1: Copy Files to Raspberry Pi

From your Mac:

```bash
# Copy the cleanup script first
scp /Users/viewvision/Desktop/PhoneSystem-Web/scripts/wipe_and_prepare.sh pi@192.168.1.221:/home/pi/

# SSH into the Pi
ssh pi@192.168.1.221
```

## Step 2: Wipe Old System

On the Raspberry Pi:

```bash
# Make cleanup script executable
chmod +x /home/pi/wipe_and_prepare.sh

# Run cleanup (this will remove old ProComm system)
./wipe_and_prepare.sh
```

**What this does:**
- ✅ Stops old phonesystem service
- ✅ Removes old systemd service files
- ✅ Kills any running Python processes
- ✅ Deletes /home/pi/ProComm directory
- ✅ Removes autostart entries
- ✅ Cleans up old virtual environments
- ✅ Removes old cron jobs
- ✅ Cleans package cache

## Step 3: Copy New System

Back on your Mac:

```bash
# Copy entire PhoneSystem-Web directory to Pi
scp -r /Users/viewvision/Desktop/PhoneSystem-Web pi@192.168.1.221:/home/pi/
```

## Step 4: Install New System

SSH back into the Pi:

```bash
ssh pi@192.168.1.221

# Navigate to project
cd /home/pi/PhoneSystem-Web

# Make install script executable
chmod +x scripts/install.sh

# Run installation
./scripts/install.sh
```

**What install.sh does:**
- ✅ Installs system dependencies (Python, baresip, ALSA, etc.)
- ✅ Creates Python virtual environment
- ✅ Installs Python packages from requirements.txt
- ✅ Copies systemd service file
- ✅ Enables and starts phonesystem service
- ✅ Configures audio routing
- ✅ Sets up kiosk mode

## Step 5: Verify Installation

```bash
# Check service status
sudo systemctl status phonesystem

# View logs
sudo journalctl -u phonesystem -f

# Test web interface
curl http://localhost:5000/api/system/status
```

## Step 6: Configure SIP Settings

1. **From Pi touchscreen:** Open Chromium to http://localhost:5000
2. **From network:** Open browser to http://192.168.1.221:5000
3. Click "Settings" → "SIP Configuration"
4. Enter your SIP server details and line credentials
5. Click "Save All Settings"
6. System will restart automatically

## Step 7: Set Up Kiosk Mode

```bash
# Make kiosk script executable
chmod +x /home/pi/PhoneSystem-Web/scripts/start_kiosk.sh

# Set to run on startup
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/phonesystem-kiosk.desktop << 'DESKTOP'
[Desktop Entry]
Type=Application
Name=Phone System Kiosk
Exec=/home/pi/PhoneSystem-Web/scripts/start_kiosk.sh
X-GNOME-Autostart-enabled=true
DESKTOP

# Reboot to test
sudo reboot
```

## Troubleshooting

### Service Won't Start

```bash
# Check detailed logs
sudo journalctl -u phonesystem -n 50 --no-pager

# Check Python errors
cd /home/pi/PhoneSystem-Web
source venv/bin/activate
python app.py
```

### Can't Access from Network

```bash
# Check if service is listening
sudo netstat -tlnp | grep 5000

# Check firewall
sudo ufw status

# Get Pi's IP address
hostname -I
```

### Audio Issues

```bash
# List audio devices
aplay -l
arecord -l

# Test audio output
speaker-test -c 8 -D hw:CARD=USB,DEV=0

# Check ALSA configuration
cat /etc/asound.conf
```

## Quick Command Reference

```bash
# Restart service
sudo systemctl restart phonesystem

# View live logs
sudo journalctl -u phonesystem -f

# Stop service
sudo systemctl stop phonesystem

# Start service
sudo systemctl start phonesystem

# Disable service
sudo systemctl disable phonesystem

# Re-run installation
cd /home/pi/PhoneSystem-Web
./scripts/install.sh
```

## Rollback (If Needed)

If you need to go back to the old PyQt5 system:

```bash
# Stop new service
sudo systemctl stop phonesystem
sudo systemctl disable phonesystem

# Remove new installation
sudo rm -rf /home/pi/PhoneSystem-Web

# Re-copy old ProComm from backup
# (Make sure you have a backup before wiping!)
scp -r /Users/viewvision/Desktop/ProComm pi@192.168.1.221:/home/pi/
```

---

**Need Help?**
- Check logs: `sudo journalctl -u phonesystem -f`
- GitHub Issues: https://github.com/omaralabed/PhoneSystem-Web/issues
