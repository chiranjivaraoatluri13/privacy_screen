"""
Fullscreen overlay for desktop-wide blur effect.
Uses PyQt5 to create a true borderless fullscreen window.
"""
import threading
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QColor, QPalette
import sys


class OverlaySignals(QObject):
    """Signals for communication with overlay thread."""
    show_signal = pyqtSignal()
    hide_signal = pyqtSignal()


class FullscreenOverlay(QWidget):
    """Fullscreen overlay widget for blur effect."""
    
    def __init__(self):
        """Initialize fullscreen overlay."""
        super().__init__()
        self.signals = OverlaySignals()
        self.signals.show_signal.connect(self.show_overlay)
        self.signals.hide_signal.connect(self.hide_overlay)
        
        # Setup window
        self.setWindowTitle("Privacy Overlay")
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        
        # Set dark red background
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(100, 50, 50))  # Dark red
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        # Make fullscreen
        self.showFullScreen()
        self.hide()  # Start hidden
    
    def show_overlay(self):
        """Show the overlay."""
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
    
    def hide_overlay(self):
        """Hide the overlay."""
        self.hide()
    
    def keyPressEvent(self, event):
        """Handle key press - allow Esc to exit (for testing)."""
        if event.key() == Qt.Key_Escape:
            pass  # Don't allow exiting with Esc - overlay should only hide from main app
        else:
            event.ignore()


class OverlayThread(threading.Thread):
    """Thread to run PyQt5 event loop for overlay."""
    
    def __init__(self):
        """Initialize overlay thread."""
        super().__init__(daemon=True)
        self.app = None
        self.overlay = None
        self.signals = None
        self.ready = threading.Event()
    
    def run(self):
        """Run PyQt5 event loop."""
        # Create app if it doesn't exist
        if QApplication.instance() is None:
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        # Create overlay
        self.overlay = FullscreenOverlay()
        self.signals = self.overlay.signals
        
        # Signal that we're ready
        self.ready.set()
        
        # Run event loop
        self.app.exec_()
    
    def show(self):
        """Show overlay (thread-safe)."""
        if self.signals:
            self.signals.show_signal.emit()
    
    def hide(self):
        """Hide overlay (thread-safe)."""
        if self.signals:
            self.signals.hide_signal.emit()


# Global overlay thread instance
_overlay_thread = None


def initialize_overlay():
    """Initialize the fullscreen overlay system."""
    global _overlay_thread
    if _overlay_thread is None:
        _overlay_thread = OverlayThread()
        _overlay_thread.start()
        _overlay_thread.ready.wait()  # Wait until overlay is ready
    return _overlay_thread


def show_privacy_overlay():
    """Show the privacy overlay."""
    thread = initialize_overlay()
    thread.show()


def hide_privacy_overlay():
    """Hide the privacy overlay."""
    thread = initialize_overlay()
    thread.hide()
