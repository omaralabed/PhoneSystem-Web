#!/bin/bash
# Start Chromium in kiosk mode for PhoneSystem-Web

# Wait for network
sleep 5

# Hide mouse cursor
unclutter -idle 0.1 &

# Start Chromium in kiosk mode
chromium-browser \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-component-extensions-with-background-pages \
    --disable-features=TranslateUI \
    --no-first-run \
    --check-for-update-interval=31536000 \
    http://localhost:5000
