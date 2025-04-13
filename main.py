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
            sys.exit(0)


class DirectScreenshotTool:
    def __init__(self):
        self.screenshots_dir = os.path.expanduser("~/Pictures/Screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        self.temp_screenshot = None
        self.file_format = "png"

    def start_capture(self):
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                self.temp_screenshot = temp_file.name

            subprocess.run(['grim', self.temp_screenshot], check=True)

            pixmap = QtGui.QPixmap(self.temp_screenshot)

            self.selection_widget = SelectionArea(pixmap)
            self.selection_widget.selection_completed.connect(self.process_selection)

        except Exception as e:
            print(f"Error: {str(e)}")
            if self.temp_screenshot and os.path.exists(self.temp_screenshot):
                os.unlink(self.temp_screenshot)
            sys.exit(1)

    def process_selection(self, rect):
        try:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"screenshot_{timestamp}.{self.file_format}"
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

            QtCore.QTimer.singleShot(100, lambda: os._exit(0))

        except Exception as e:
            print(f"Error: {str(e)}")
            if self.temp_screenshot and os.path.exists(self.temp_screenshot):
                os.unlink(self.temp_screenshot)
            sys.exit(1)


def main():
    app = QtWidgets.QApplication(sys.argv)

    if len(sys.argv) > 1 and sys.argv[1] in ["png", "jpg"]:
        file_format = sys.argv[1]
    else:
        file_format = "png"

    tool = DirectScreenshotTool()
    tool.file_format = file_format
    tool.start_capture()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()