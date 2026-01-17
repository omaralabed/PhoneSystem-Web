#!/usr/bin/env python3
"""
PyQt5 GUI Launcher for PhoneSystem-Web
Embeds the web interface in a native Qt window
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt

class PhoneSystemGUI(QWebEngineView):
    def __init__(self):
        super().__init__()
        
        # Configure web engine settings for better rendering
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
        
        # Set window properties
        self.setWindowTitle("ProComm Phone System")
        
        # Load the web interface
        self.load(QUrl("http://localhost:5000"))
        
        # Show fullscreen
        self.showFullScreen()
        
        # Hide cursor for kiosk mode (optional - can be removed if you want cursor)
        # QApplication.setOverrideCursor(Qt.BlankCursor)
    
    def keyPressEvent(self, event):
        # Allow F11 to toggle fullscreen, ESC to exit
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_Escape:
            # Uncomment if you want ESC to exit the app
            # self.close()
            pass
        else:
            super().keyPressEvent(event)

def main():
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Better rendering
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    app = QApplication(sys.argv)
    app.setApplicationName("ProComm Phone System")
    
    # Create and show the GUI
    gui = PhoneSystemGUI()
    
    # Set zoom to make 1366x768 render like Safari (1.15 = bigger, fills screen)
    gui.setZoomFactor(1.15)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
