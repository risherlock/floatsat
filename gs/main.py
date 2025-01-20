from PyQt5 import QtGui, QtCore, QtSerialPort
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSerialPort import *
from PyQt5.QtWidgets import *

import sys
import random
import pyqtgraph
from typing import *
from queue import *

import time
import struct
import rodosmwinterface as rodos

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

class RealTimeGraphs(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.graphs = []
        self.curves = []
        self.data = []

        for title, color in [("Accelerometer X", 'r'), ("Accelerometer Y", 'g'), ("Accelerometer Z", 'b')]:
            plot = pyqtgraph.PlotWidget()
            plot.setBackground('w')
            plot.setTitle(title, color=color, size="15pt")
            plot.setLabel('left', 'Value', color='r', size=12)
            plot.setLabel('bottom', 'Time', color='r', size=12)
            plot.setXRange(0, 100, padding=0)
            plot.setYRange(0, 10, padding=0)  # Adjust as needed for your data

            curve = plot.plot(pen=pyqtgraph.mkPen(color=color, width=2))
            layout.addWidget(plot)

            self.graphs.append(plot)
            self.curves.append(curve)
            self.data.append([0] * 100)

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start()

    def update_graphs(self):
        for i in range(3):
            self.data[i] = self.data[i][1:] + [random.uniform(0, 10)]
            self.curves[i].setData(list(range(100)), self.data[i])


class Compass(QMainWindow):

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


class rodos_thread(QThread):
  # Signal to send data to graph
  new_data = pyqtSignal(float, float, float)

  def __init__(self, parent: Optional[QWidget] = None):
    super().__init__(parent)
    self.is_running = True

  def run(self):
    rodos.printTopicInit(enable = True)

    # Callback function to process received data
    def topic_handler(data):
      try:
        unpacked = struct.unpack("qI", data);
        print("RODOS sends index: {} and time (s): {}".format(unpacked[0], unpacked[1]))
      except Exception as e:
        print(e)
        print(data)
        print(len(data))

    python_to_rodos = rodos.Topic(1002)
    rodos_to_python = rodos.Topic(1003)
    link_uart = rodos.LinkinterfaceUART(path = "/dev/rfcomm0")
    gateway_uart = rodos.gateway(link_uart)
    gateway_uart.run()

    rodos_to_python.addSubscriber(topic_handler)
    gateway_uart.forwardTopic(python_to_rodos)

    while self.is_running:
      sensor_index = 0
      x, y, z = 3.1415, 2.7182, 12345
      sensor_struct = struct.pack("20sIddd", b"Magnetometer", sensor_index, x, y, z)
      python_to_rodos.publish(sensor_struct)
      self.sleep(1)

    def stop(self):
      self.is_running = False
      self.quit()
      self.wait()

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

class MainApplication(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Ground Station")
    self.setGeometry(100, 100, 800, 600)

    # Create the tab widget
    self.tabs = QTabWidget()
    self.setCentralWidget(self.tabs)

    # Add the Serial Port GUI as a tab
    self.serial_port_gui = SerialPortGUI()
    self.tabs.addTab(self.serial_port_gui, "Serial Port")

    # Add the compass as a tab
    self.compass_widget = Compass()
    self.tabs.addTab(self.compass_widget, "Compass")

    # Add the Real-Time Graphs as a tab
    self.real_time_graphs = RealTimeGraphs()
    self.tabs.addTab(self.real_time_graphs, "Accelerometer")

    # Create and start RODOS thread
    self.rodos_thread = rodos_thread()
    self.rodos_thread.start()
    # self.rodos_thread.new_data.connect(self.real_time_graphs.update_graphs)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  main_app = MainApplication()
  main_app.show()
  sys.exit(app.exec_())
