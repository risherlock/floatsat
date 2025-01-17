import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import pyqtgraph as pg


class RealTimeGraphs(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a layout for the graphs
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Create three plot widgets
        self.graphs = []
        self.curves = []
        self.data = []

        for title, color in [("Accelerometer X", 'r'), ("Accelerometer Y", 'g'), ("Accelerometer Z", 'b')]:
            plot = pg.PlotWidget()
            plot.setBackground('w')
            plot.setTitle(title, color=color, size="15pt")
            plot.setLabel('left', 'Value', color='r', size=12)
            plot.setLabel('bottom', 'Time', color='r', size=12)
            plot.setXRange(0, 100, padding=0)
            plot.setYRange(0, 10, padding=0)  # Adjust as needed for your data

            curve = plot.plot(pen=pg.mkPen(color=color, width=2))
            layout.addWidget(plot)

            # Store plot, curve, and data
            self.graphs.append(plot)
            self.curves.append(curve)
            self.data.append([0] * 100)  # Pre-fill data with zeros

        # Set up a QTimer to update the graphs
        self.timer = QTimer()
        self.timer.setInterval(100)  # Update interval in milliseconds
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start()

        # Counter for x-axis
        self.counter = 0

    def update_graphs(self):
        for i in range(3):
            self.data[i] = self.data[i][1:] + [random.uniform(0, 10)]
            self.curves[i].setData(list(range(100)), self.data[i])
        self.counter += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimeGraphs()
    window.setWindowTitle("Real-Time Graphs")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
