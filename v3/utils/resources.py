from PyQt5.QtGui import QPixmap, QIcon, QColor, QPainter, QFont
from PyQt5.QtCore import Qt, QSize, QRect
import os

def get_placeholder_pixmap(width, height, color="#6d28d9", text=""):
    """Create a colored placeholder pixmap when an image is missing"""
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Draw rounded rectangle background
    painter.setBrush(QColor(color))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, width, height, width/4, height/4)
    
    # Draw text if provided
    if text:
        painter.setPen(QColor("white"))
        font = QFont("Arial", width//4)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRect(0, 0, width, height), Qt.AlignCenter, text)
    
    painter.end()
    return pixmap

def get_icon(path, fallback_char="", size=24):
    """Get an icon, with a text fallback if the file doesn't exist"""
    # Check if file exists
    if os.path.exists(path):
        icon = QIcon(path)
        if not icon.isNull():
            return icon
    
    # If file doesn't exist or icon is null, create placeholder
    pixmap = get_placeholder_pixmap(size, size, get_color_for_char(fallback_char), fallback_char)
    return QIcon(pixmap)

def get_pixmap(path, fallback_text="", width=80, height=80):
    """Get a pixmap, with a text fallback if the file doesn't exist"""
    # Check if file exists
    if os.path.exists(path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            return pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    # If file doesn't exist or pixmap is null, create placeholder
    return get_placeholder_pixmap(width, height, get_color_for_char(fallback_text), fallback_text)

def get_color_for_char(char):
    """Get a consistent color based on a character"""
    colors = [
        "#ef4444",  # Red
        "#f59e0b",  # Amber
        "#10b981",  # Green
        "#3b82f6",  # Blue
        "#8b5cf6",  # Purple
        "#ec4899",  # Pink
        "#06b6d4",  # Cyan
        "#14b8a6",  # Teal
        "#f97316",  # Orange
        "#6366f1"   # Indigo
    ]
    
    if not char:
        return colors[0]
    
    # Get a consistent index based on the first character
    index = ord(char[0].upper()) % len(colors)
    return colors[index]