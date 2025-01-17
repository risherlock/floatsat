from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import numpy as np

class Clock(QMainWindow):

  def __init__(self):
    super().__init__()
    timer = QTimer(self)
    timer.timeout.connect(self.update)
    timer.start(1000)
    self.setWindowTitle('compass')
    self.setGeometry(200, 200, 300, 300)
    self.setStyleSheet("background : white;")
    self.hPointer = QtGui.QPolygon([QPoint(6, 0),
                                        QPoint(-6, 0),
                                        QPoint(0, -50)])
    self.rPointer = QtGui.QPolygon([QPoint(6, 0),
                                        QPoint(-6, 0),
                                        QPoint(0, 50)])
    self.bColor = Qt.black
    self.rColor = Qt.red

  def paintEvent(self, event):
    rec = min(self.width(), self.height())
    tik = QTime.currentTime()
    painter = QPainter(self)

    def drawPointer(color, rotation, pointer):
      painter.setBrush(QBrush(color))
      painter.save()
      painter.rotate(rotation)
      painter.drawConvexPolygon(pointer)
      painter.restore()

    painter.setRenderHint(QPainter.Antialiasing)
    painter.translate(self.width() / 2, self.height() / 2)
    painter.scale(rec / 200, rec / 200)
    painter.setPen(QtCore.Qt.NoPen)

    drawPointer(self.bColor, 5 * tik.second(), self.hPointer)
    drawPointer(self.rColor, 5 * tik.second(), self.rPointer)
    painter.setPen(QPen(self.bColor))

    # Draw clock ticks
    for i in range(0, 60):
      if (i % 5) == 0:
          painter.drawLine(87, 0, 97, 0)
      painter.rotate(6)

    # Draw angles every 10 degrees
    painter.setPen(QPen(Qt.black, 1))
    for i in range(0, 360, 30):
      angle_text = str(i)
      x = (int)(110 * np.cos(np.deg2rad(i)))
      y = (int)(110 * np.sin(np.deg2rad(i)))
      painter.drawText(x - 10, y + 5, angle_text)  # Adjust text position slightly

    painter.end()

if __name__ == '__main__':
  app = QApplication(sys.argv)
  win = Clock()
  win.show()
  exit(app.exec_())
