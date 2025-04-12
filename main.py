#!/usr/bin/env python3
import sys
import os
import subprocess
import tempfile
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore

class SelectionArea(QtWidgets.QWidget):
    selection_completed = QtCore.pyqtSignal(QtCore.QRect)

    def __init__(self, background_image=None):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor)

        self.background_image = background_image
        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()
        self.is_drawing = False

        self.showFullScreen()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        if self.background_image:
            painter.drawPixmap(0, 0, self.background_image)

        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 100))

        if self.is_drawing:
            selection = QtCore.QRect(self.start_point, self.end_point).normalized()

            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2, QtCore.Qt.SolidLine))
            painter.drawRect(selection)

            handle_size = 8
            handle_color = QtGui.QColor(0, 120, 215)
            painter.setBrush(QtGui.QBrush(handle_color))
            painter.setPen(QtCore.Qt.NoPen)

            painter.drawRect(QtCore.QRect(selection.topLeft().x() - handle_size//2,
                                         selection.topLeft().y() - handle_size//2,
                                         handle_size, handle_size))
            painter.drawRect(QtCore.QRect(selection.topRight().x() - handle_size//2,
                                         selection.topRight().y() - handle_size//2,
                                         handle_size, handle_size))
            painter.drawRect(QtCore.QRect(selection.bottomLeft().x() - handle_size//2,
                                         selection.bottomLeft().y() - handle_size//2,
                                         handle_size, handle_size))
            painter.drawRect(QtCore.QRect(selection.bottomRight().x() - handle_size//2,
                                         selection.bottomRight().y() - handle_size//2,
                                         handle_size, handle_size))

            text = f"{selection.width()} × {selection.height()}"
            font = QtGui.QFont("Arial", 10)
            font.setBold(True)
            painter.setFont(font)

            # Text background
            text_rect = painter.fontMetrics().boundingRect(text)
            text_rect.moveCenter(selection.center())
            text_rect.moveBottom(selection.top() - 5)
            text_rect.adjust(-5, -5, 5, 5)

            painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 160)))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRoundedRect(text_rect, 3, 3)

            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
            painter.drawText(text_rect, QtCore.Qt.AlignCenter, text)

            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            painter.fillRect(selection, QtGui.QColor(0, 0, 0, 0))

            if self.background_image:
                painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
                region = QtGui.QRegion(selection)
                painter.setClipRegion(region)
                painter.drawPixmap(0, 0, self.background_image)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.is_drawing:
            self.end_point = event.pos()
            self.is_drawing = False
            selection = QtCore.QRect(self.start_point, self.end_point).normalized()
            self.selection_completed.emit(selection)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()


class ModernButton(QtWidgets.QPushButton):
    def __init__(self, text, parent=None, icon=None):
        super().__init__(text, parent)
        self.setFixedHeight(40)
        self.setCursor(QtCore.Qt.PointingHandCursor)

        if icon:
            self.setIcon(icon)


class SnippingTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.screenshots_dir = os.path.expanduser("~/Pictures/Screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.temp_screenshot = None
        self.processing = False

        self.setStyleSheet("""
            QMainWindow {
                background-color: #292d3e;
            }
            QWidget {
                color: #eeffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #3c4051;
                border: none;
                border-radius: 4px;
                color: #eeffff;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #444b6a;
            }
            QPushButton:pressed {
                background-color: #292d3e;
            }
            QLabel {
                font-size: 13px;
            }
            QComboBox {
                background-color: #3c4051;
                border: none;
                border-radius: 4px;
                color: #eeffff;
                padding: 6px;
                min-width: 6em;
            }
            QComboBox:hover {
                background-color: #444b6a;
            }
            QComboBox::drop-down {
                width: 20px;
                border: none;
            }
            QComboBox::down-arrow {
                image: url(dropdown-arrow.png);
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 2px;
                border: 2px solid #575f77;
            }
            QCheckBox::indicator:checked {
                background-color: #82aaff;
                border: 2px solid #82aaff;
                image: url(checkbox.png);
            }
        """)

    def initUI(self):
        self.setWindowTitle('Screenshot Tool')
        self.setGeometry(300, 300, 360, 250)
        self.setWindowIcon(QtGui.QIcon.fromTheme("camera-photo"))

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(main_layout)

        header_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("Screenshot Tool")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: #3c4051;")
        main_layout.addWidget(separator)

        self.screenshot_btn = ModernButton('Capture Screenshot')
        self.screenshot_btn.setIcon(QtGui.QIcon.fromTheme("camera-photo"))
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        main_layout.addWidget(self.screenshot_btn)

        self.status_label = QtWidgets.QLabel('Ready to capture')
        self.status_label.setStyleSheet("color: #c3e88d; font-size: 12px;")
        main_layout.addWidget(self.status_label)

        options_group = QtWidgets.QGroupBox("Options")
        options_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3c4051;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        options_layout = QtWidgets.QVBoxLayout(options_group)

        format_layout = QtWidgets.QHBoxLayout()
        format_layout.setContentsMargins(0, 0, 0, 0)
        format_label = QtWidgets.QLabel('Format:')
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(['png', 'jpg'])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)

        self.close_after = QtWidgets.QCheckBox("Close after capture")
        self.close_after.setChecked(True)
        options_layout.addWidget(self.close_after)

        main_layout.addWidget(options_group)

        main_layout.addStretch()

        shortcut_label = QtWidgets.QLabel("Press Win+Shift+S to capture anytime")
        shortcut_label.setStyleSheet("color: #7f85a3; font-size: 11px;")
        shortcut_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(shortcut_label)

    def take_screenshot(self):
        if self.processing:
            return
        self.processing = True
        self.hide()  # Hide window while taking screenshot
        QtCore.QTimer.singleShot(300, self.prepare_selection)

    def prepare_selection(self):
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                self.temp_screenshot = temp_file.name

            subprocess.run(['grim', self.temp_screenshot], check=True)

            pixmap = QtGui.QPixmap(self.temp_screenshot)

            self.selection_widget = SelectionArea(pixmap)
            self.selection_widget.selection_completed.connect(self.process_selection)
            self.selection_widget.show()

        except Exception as e:
            self.status_label.setText(f'Error: {str(e)}')
            self.status_label.setStyleSheet("color: #f07178; font-size: 12px;")
            self.show()
            self.processing = False

    def process_selection(self, rect):
        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_format = self.format_combo.currentText().lower()
            filename = f"screenshot_{timestamp}.{file_format}"
            save_path = os.path.join(self.screenshots_dir, filename)

            from PIL import Image
            img = Image.open(self.temp_screenshot)
            cropped = img.crop((rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height()))
            cropped.save(save_path)

            if self.temp_screenshot and os.path.exists(self.temp_screenshot):
                os.unlink(self.temp_screenshot)
                self.temp_screenshot = None

            subprocess.Popen(['notify-send', 'Screenshot Captured', f'Saved to: {save_path}'])

            subprocess.Popen(['wl-copy', '-t', 'image/png', save_path])

            if self.close_after.isChecked():
                os._exit(0)
            else:
                self.status_label.setText(f'Saved to: {save_path}')
                self.status_label.setStyleSheet("color: #c3e88d; font-size: 12px;")
                self.show()

        except Exception as e:
            self.status_label.setText(f'Error: {str(e)}')
            self.status_label.setStyleSheet("color: #f07178; font-size: 12px;")
            self.show()
        finally:
            self.processing = False


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    tool = SnippingTool()
    tool.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()