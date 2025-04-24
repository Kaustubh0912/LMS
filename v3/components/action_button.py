from PyQt5.QtWidgets import QPushButton

class ActionButton(QPushButton):
    STYLE_PRIMARY = "primary"
    STYLE_DANGER = "danger"
    STYLE_SUCCESS = "success"
    STYLE_WARNING = "warning"

    def __init__(self, text="", button_style=STYLE_PRIMARY, parent=None):
        super().__init__(text, parent)
        self.set_style(button_style)

    def set_style(self, button_style):
        base_style = """
            QPushButton {
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                opacity: 1.0;
            }
        """

        if button_style == self.STYLE_PRIMARY:
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: rgba(121, 134, 203, 0.7);
                }
                QPushButton:hover {
                    background-color: rgba(141, 154, 223, 0.8);
                }
                QPushButton:pressed {
                    background-color: rgba(101, 114, 183, 0.9);
                }
            """)
        elif button_style == self.STYLE_DANGER:
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: rgba(231, 76, 60, 0.7);
                }
                QPushButton:hover {
                    background-color: rgba(251, 96, 80, 0.8);
                }
                QPushButton:pressed {
                    background-color: rgba(211, 56, 40, 0.9);
                }
            """)
        elif button_style == self.STYLE_SUCCESS:
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: rgba(46, 204, 113, 0.7);
                }
                QPushButton:hover {
                    background-color: rgba(66, 224, 133, 0.8);
                }
                QPushButton:pressed {
                    background-color: rgba(26, 184, 93, 0.9);
                }
            """)
        elif button_style == self.STYLE_WARNING:
            self.setStyleSheet(base_style + """
                QPushButton {
                    background-color: rgba(241, 196, 15, 0.7);
                }
                QPushButton:hover {
                    background-color: rgba(261, 216, 35, 0.8);
                }
                QPushButton:pressed {
                    background-color: rgba(221, 176, 0, 0.9);
                }
            """)
