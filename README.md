# PhoneSystem-Web

Web-based 8-line phone system for broadcast production, built with Flask and HTML/JS/CSS. Replaces the previous PyQt5 desktop application with a modern web interface accessible from any device.

## Features

- **8 Independent Phone Lines** - Each with SIP registration and call control
- **Multi-Device Access** - Control from Pi touchscreen, desktop browser, or mobile device
- **Real-time Updates** - WebSocket-powered live status updates
- **Audio Routing** - Route each line to any of 8 output channels (Focusrite 8i6)
- **Test Tone Generator** - Verify audio routing with 1kHz test tone
- **SIP Configuration** - Web-based settings for all 8 lines
- **Network Configuration** - Change between DHCP and Static IP from web UI
- **Dark Theme** - Professional broadcast-style interface

## Quick Start

### On Raspberry Pi

```bash
# Clone repository
git clone https://github.com/omaralabed/PhoneSystem-Web.git
cd PhoneSystem-Web

# Run installation script
chmod +x scripts/install.sh
./scripts/install.sh

# Start service
sudo systemctl start phonesystem
sudo systemctl enable phonesystem

# Access at http://localhost:5000
```

### From Network

Access from any device on the same network:
```
http://192.168.1.221:5000
```
(Replace with your Pi's IP address)

## Hardware Requirements

- **Raspberry Pi 4** (4GB+ recommended)
- **WIMAXIT 12" Touchscreen** (1366x768)
- **Focusrite Scarlett 8i6** USB audio interface
- **Ethernet connection** (recommended for SIP traffic)

## Configuration

### SIP Settings

1. Open `http://PI_IP:5000/sip-settings`
2. Configure global SIP server settings
3. Expand each line and enter credentials
4. Click "Save All Settings"
5. System will restart to apply changes

### Network Settings

1. Open `http://PI_IP:5000/network-settings`
2. Choose DHCP or Static IP
3. Enter network details (for static)
4. Click "Save & Reboot System"

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
python app.py

# Access at http://localhost:5000
```

## API Documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete API documentation.

### Quick API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/lines` | GET | Get all line statuses |
| `/api/lines/<id>/dial` | POST | Dial number on line |
| `/api/lines/<id>/hangup` | POST | Hang up line |
| `/api/config/sip` | GET/POST | SIP configuration |
| `/api/config/network` | GET/POST | Network configuration |

## Project Structure

```
PhoneSystem-Web/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── config/                 # Configuration files
│   ├── sip_config.json
│   └── audio_config.json
├── src/                    # Backend modules
│   ├── sip_engine.py
│   ├── audio_router.py
│   ├── phone_line.py
│   └── tone_generator.py
├── static/                 # Frontend assets
│   ├── css/styles.css
│   └── js/
│       ├── main.js
│       ├── websocket.js
│       ├── dialer.js
│       └── settings.js
├── templates/              # HTML templates
│   ├── index.html
│   ├── sip_settings.html
│   └── network_settings.html
└── scripts/                # Deployment scripts
    ├── install.sh
    ├── start_kiosk.sh
    └── update_network.sh
```

## Migration from PyQt5

This project replaces the previous PyQt5 desktop application. Key improvements:

- ✅ **Multi-device access** - Control from anywhere on the network
- ✅ **No freeze issues** - Separate pages instead of blocking dialogs
- ✅ **Native keyboard** - No custom virtual keyboard needed
- ✅ **Easier maintenance** - Standard HTML/CSS/JS instead of PyQt5
- ✅ **Better updates** - WebSocket for real-time status without polling

## Troubleshooting

### Service won't start

```bash
# Check service status
sudo systemctl status phonesystem

# View logs
sudo journalctl -u phonesystem -f
```

### No audio output

```bash
# Check audio device
arecord -l
aplay -l

# Test audio manually
speaker-test -c 8 -D hw:CARD=USB,DEV=0
```

### Can't access from network

```bash
# Check if service is running
sudo systemctl status phonesystem

# Check firewall
sudo ufw status

# Check IP address
hostname -I
```

## Contributing

This is a production system for a specific broadcast setup. For major changes, please open an issue first.

## Support

For issues or questions, please open a GitHub issue at:
https://github.com/omaralabed/PhoneSystem-Web/issues

---

**Built with ❤️ for broadcast production**
