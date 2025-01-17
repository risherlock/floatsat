
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QVBoxLayout, QHBoxLayout, QComboBox,
                             QPushButton, QTextEdit, QLabel)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from typing import Optional
from queue import Queue
import sys

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class SerialThread(QThread):
    """
    A thread class for handling serial port operations.
    """
    received_data = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.serial_port: QSerialPort = QSerialPort()
        self.is_running: bool = False
        self.write_queue: Queue = Queue()

    def setup_port(self, port_name: str, baud_rate: int,
                   data_bits: int, parity: QSerialPort.Parity,
                   stop_bits: QSerialPort.StopBits,
                   flow_control: QSerialPort.FlowControl) -> None:
        """
        Set up the serial port with the given parameters.
        """
        self.serial_port.setPortName(port_name)
        self.serial_port.setBaudRate(baud_rate)
        self.serial_port.setDataBits(data_bits)
        self.serial_port.setParity(parity)
        self.serial_port.setStopBits(stop_bits)
        self.serial_port.setFlowControl(flow_control)

    def run(self) -> None:
        """
        The main loop of the thread for reading data from the serial
        port and writing queued data.
        """
        if not self.serial_port.open(QSerialPort.ReadWrite):
            self.error_occurred.emit(
                f"Failed to open port: {self.serial_port.errorString()}")
            return

        self.is_running = True

        while self.is_running:
            # Handle writing
            while not self.write_queue.empty():
                data = self.write_queue.get()
                self.serial_port.write(data)
                self.serial_port.flush()

            # Handle reading
            if self.serial_port.waitForReadyRead(100):
                data = self.serial_port.readAll().data().decode()
                self.received_data.emit(data)

        self.serial_port.close()

    def stop(self) -> None:
        """
        Stop the thread and close the serial port.
        """
        self.is_running = False
        self.quit()
        self.wait()

    def write_data(self, data: str) -> None:
        """
        Queue data to be written to the serial port.
        """
        if self.serial_port.isOpen():
            self.write_queue.put(data.encode())
        else:
            self.error_occurred.emit("Serial port is not open")



class SerialPortGUI(QMainWindow):
    """
    The main GUI class for the serial port communication application.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Port Communication")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()

        self.serial_thread = SerialThread(self)
        self.serial_thread.received_data.connect(self.update_received_data)
        self.serial_thread.error_occurred.connect(self.show_error)

    def setup_ui(self) -> None:

        self.port_combo = QComboBox()
        self.port_combo.setFixedWidth(80)
        self.refresh_ports()

        self.baud_combo = QComboBox()
        self.baud_combo.setFixedWidth(80)
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_combo.setCurrentText("19200")

        self.data_bits_combo = QComboBox()
        self.data_bits_combo.setFixedWidth(80)
        self.data_bits_combo.addItems(["5", "6", "7", "8"])
        self.data_bits_combo.setCurrentText("8")

        self.parity_combo = QComboBox()
        self.parity_combo.setFixedWidth(80)
        self.parity_combo.addItems(["None", "Even", "Odd", "Space", "Mark"])

        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.setFixedWidth(80)
        self.stop_bits_combo.addItems(["1", "1.5", "2"])

        self.flow_control_combo = QComboBox()
        self.flow_control_combo.setFixedWidth(80)
        self.flow_control_combo.addItems(["None", "Hardware", "Software"])

        label_layout = QVBoxLayout()
        label_layout.addWidget(QLabel("Port:"))
        label_layout.addWidget(QLabel("Baud Rate:"))
        label_layout.addWidget(QLabel("Data Bits:"))
        label_layout.addWidget(QLabel("Parity:"))
        label_layout.addWidget(QLabel("Stop Bits:"))
        label_layout.addWidget(QLabel("Flow Control:"))

        combo_layout = QVBoxLayout()
        combo_layout.addWidget(self.port_combo)
        combo_layout.addWidget(self.baud_combo)
        combo_layout.addWidget(self.data_bits_combo)
        combo_layout.addWidget(self.parity_combo)
        combo_layout.addWidget(self.stop_bits_combo)
        combo_layout.addWidget(self.flow_control_combo)

        label_combo_layout = QHBoxLayout()
        label_combo_layout.addLayout(label_layout)
        label_combo_layout.addStretch(1)
        label_combo_layout.addLayout(combo_layout)

        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedWidth(80)
        self.connect_button.clicked.connect(self.connect_serial)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setFixedWidth(80)
        self.disconnect_button.clicked.connect(self.disconnect_serial)
        self.disconnect_button.setEnabled(False)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.connect_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.disconnect_button)

        self.send_input = QTextEdit()

        self.send_button = QPushButton("Send")
        self.send_button.setFixedWidth(80)
        self.send_button.clicked.connect(self.send_data)

        send_button_layout = QHBoxLayout()
        send_button_layout.addStretch(1)
        send_button_layout.addWidget(self.send_button)

        # Received data display
        self.received_display = QTextEdit()
        self.received_display.setReadOnly(True)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setFixedWidth(80)
        self.clear_button.clicked.connect(self.clear_data)

        clear_button_layout = QHBoxLayout()
        clear_button_layout.addStretch(1)
        clear_button_layout.addWidget(self.clear_button)

        self.layout.addLayout(label_combo_layout)
        self.layout.addSpacing(20)
        self.layout.addLayout(buttons_layout)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.send_input)
        self.layout.addLayout(send_button_layout)
        self.layout.addWidget(self.received_display)
        self.layout.addLayout(clear_button_layout)

        self.setFixedSize(400, 500)

    def refresh_ports(self) -> None:
        """
        Refresh the list of available serial ports.
        """
        self.port_combo.clear()
        for port in QSerialPortInfo.availablePorts():
            self.port_combo.addItem(port.portName())

    @pyqtSlot()
    def connect_serial(self) -> None:
        """
        Connect to the selected serial port with the chosen settings.
        """
        port_name = self.port_combo.currentText()
        baud_rate = int(self.baud_combo.currentText())
        data_bits = int(self.data_bits_combo.currentText())
        parity = QSerialPort.Parity(self.parity_combo.currentIndex())
        stop_bits = QSerialPort.StopBits(self.stop_bits_combo.currentIndex())
        flow_control = QSerialPort.FlowControl(self.flow_control_combo.currentIndex())

        self.serial_thread.setup_port(port_name, baud_rate, data_bits, 
                                      parity, stop_bits, flow_control)
        self.serial_thread.start()

        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)

    @pyqtSlot()
    def disconnect_serial(self) -> None:
        """
        Disconnect from the serial port.
        """
        self.serial_thread.stop()
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)

    @pyqtSlot()
    def send_data(self) -> None:
        """
        Send data type str through the serial port.
        """
        data = self.send_input.toPlainText()
        self.serial_thread.write_data(data)
        # self.send_input.clear()

    @pyqtSlot(str)
    def update_received_data(self, data: str) -> None:
        """
        Update the received data display with new data.
        """
        self.received_display.append(data)

    @pyqtSlot(str)
    def show_error(self, error: str) -> None:
        """
        Display an error message.
        """
        self.received_display.append(f"ERROR: {error}")

    def clear_data(self) -> None:
        self.received_display.clear()

    # Overwrite method closeEvent from class QMainWindow.
    def closeEvent(self, event) -> None:
        # Close the thread
        if self.serial_thread.isRunning():
            self.serial_thread.stop()

        # Accept the event.
        event.accept()


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

    for i in range(0, 60):
      if (i % 5) == 0:
          painter.drawLine(87, 0, 97, 0)
      painter.rotate(6)

    painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialPortGUI()
    win = Clock()

    win.show()
    window.show()
    sys.exit(app.exec_())