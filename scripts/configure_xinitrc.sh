#!/bin/bash
# Configure X11 startup with screen saver disabled

cat > ~/.xinitrc << 'XINITRC'
#!/bin/bash
sleep 2
export DISPLAY=:0

# Disable screen blanking and power management
xset s off
xset -dpms
xset s noblank

# Start GUI
cd /home/procomm/PhoneSystem-Web
python3 gui_launcher.py &

# Start window manager
exec /usr/bin/openbox-session
XINITRC

chmod +x ~/.xinitrc
echo "X11 startup configured with screen saver disabled"
