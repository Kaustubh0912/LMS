from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import Qt

class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glassCard")
        self.setStyleSheet("""
            #glassCard {
                background-color: rgba(43, 45, 55, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setContentsMargins(15, 15, 15, 15)
