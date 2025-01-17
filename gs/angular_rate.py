from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtGui
from PyQt5.QtGui import QPainter, QPolygon, QBrush, QPen
from PyQt5.QtCore import Qt, QTimer, QPoint
import sys
import random  # For generating test angular velocity


class AngularVelocityMeter(QMainWindow):
    def __init__(self):
        super().__init__()

        # Timer for updating the meter
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  # Update every 100ms

        # Main window setup
        self.setWindowTitle("Angular Velocity Meter")
        self.setGeometry(200, 200, 300, 300)
        self.setStyleSheet("background: white;")

        # Needle shape
        self.needle = QPolygon([QPoint(6, 0), QPoint(-6, 0), QPoint(0, -70)])

        # Color and value properties
        self.needle_color = Qt.red
        self.needle_rotation = 0  # Initial angular velocity in degrees
        self.max_velocity = 360  # Maximum angular velocity for full-scale rotation

    def paintEvent(self, event):
        """Custom paint event for the meter."""
        rec = min(self.width(), self.height())
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(rec / 200, rec / 200)
        painter.setPen(Qt.NoPen)

        # Draw the needle
        self.draw_needle(painter)

        # Draw the scale and labels
        self.draw_scale(painter)

        painter.end()

    def draw_needle(self, painter):
        """Draw the needle pointing to the current angular velocity."""
        painter.setBrush(QBrush(self.needle_color))
        painter.save()
        rotation = (self.needle_rotation / self.max_velocity) * 180 - 90
        painter.rotate(rotation)
        painter.drawConvexPolygon(self.needle)
        painter.restore()

    def draw_scale(self, painter):
        """Draw the scale markings and labels."""
        painter.setPen(QPen(Qt.black, 2))
        for i in range(-90, 91, 10):  # Scale from -90 to +90 degrees
            painter.save()
            painter.rotate(i)
            if i % 30 == 0:  # Major tick
                painter.drawLine(80, 0, 100, 0)
                painter.drawText(110, 0, f"{i + 90}")  # Add label
            else:  # Minor tick
                painter.drawLine(90, 0, 100, 0)
            painter.restore()

    def update(self):
        """Update the needle position based on simulated angular velocity."""
        # Generate a random angular velocity between -360 and 360
        self.needle_rotation = random.uniform(-self.max_velocity, self.max_velocity)
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = AngularVelocityMeter()
    win.show()
    sys.exit(app.exec_())
