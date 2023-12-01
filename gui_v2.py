from PyQt5.QtWidgets import QApplication, QFrame, QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit, QVBoxLayout, QFormLayout, QGraphicsDropShadowEffect, QFileDialog, QScrollArea, QColorDialog, QStackedWidget, QMainWindow, QGridLayout
from PyQt5.QtGui import QPixmap, QImageReader, QIcon, QCursor, QFont, QPainter, QPainterPath, QLinearGradient, QColor, QPen, QBrush, QBitmap, QImage
from PyQt5.QtCore import Qt, QSize, QRect, QTimer, QObject, pyqtSignal, QThread, QEasingCurve, QPropertyAnimation
import pyqtgraph as pg
import numpy as np
import math
import random
import sys
import time
import subprocess
import bluetooth
from statistics import *

host_mac_address = 'D8:3A:DD:3C:D9:91'  # Replace with the Bluetooth adapter MAC address of the server

port = 4
backlog = 1
size = 1024

PATH = "/home/pi/mu_code/WSAN/"


class CalcBPM(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super(CalcBPM, self).__init__(parent)
        self.bpmList = np.array([])
        self.threshold = 120
        self.running = False
        self.bpm = -1
        self.rmssd = -1
        self.hrstd = -1
        self.time_interal_beat = [] # For calculating RMSSD

    def run(self):
        while True:
            start_time = time.time()
            while self.running:
                cur_time = time.time()
                self.time_interval_beat = []
                count = 0
                prev_beat = 0 # For calculating RMSSD
                while cur_time - start_time < 10:
                    # TODO: get the read data through Bluetooth
                    data = random.randrange(0, 255)
                    global client_socket
                    #data = client_socket.recv(size)
                    if data:
                        signal = int(data)

                        self.bpmList = np.append(self.bpmList, signal)

                        if signal > self.threshold:
                            beat = time.time()
                            print("beat!!")

                            if count > 0:
                                self.time_interval_beat.append(round(abs((beat - prev_beat)*1000),2))
                            prev_beat = beat
                            count += 1


                    time.sleep(0.15) # TODO: Remove
                    cur_time = time.time()

                # Update BPM
                self.bpm = count * 6
                print("Time:\n", self.time_interval_beat)
                print("BPM: %d" % self.bpm)
                # Update RMSSD
                self.rmssd, self.hrstd = self.calculate_rms()
                print("RMSSD: ", self.rmssd)
                start_time = time.time()


    #RMSSD ( 19ms - 48-50ms ) - ideal values
    def calculate_rms(self):
        rms_arr = []
        for i in range(1, len(self.time_interval_beat)):
            rms_arr.append(round(abs(self.time_interval_beat[i] - self.time_interval_beat[i-1]),2))

        # Calculating RMSSD value
        rms = round(math.sqrt(np.square(rms_arr).mean()),2)
        hrstd = round(stdev(rms_arr),2)
        
        #print("Time interval between successive beats for the past ten seconds\n",time_interval_beat)
        #print("RMS array: ", rms_arr)

        return rms, hrstd
    
class BPMPage(QWidget):
    def __init__(self, parent=None):
        super(BPMPage, self).__init__(parent)
        self.gridWidget = QGridLayout(self)


        self.bpm_timer = QTimer(self)
        self.bpm_timer.timeout.connect(self.update_graph)


        # Page title
        self.title = QLabel("Pulse Monitoring System", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.gridWidget.addWidget(self.title, 0, 0, 1, 6, alignment=Qt.AlignCenter)  # Span 1 row, 6 columns
        self.title.setStyleSheet("font-size: 35px; font-weight: bold; color: white; background: transparent;")

        self.heartBtn = QPushButton(self)
        self.heartBtn.setCursor(QCursor(Qt.PointingHandCursor))
        pixmap = QPixmap(PATH + 'heart_init.png')
        image = QImage(pixmap.toImage())

        #self.heartBtn.setIcon(QIcon(PATH + 'heart_init.png'))
        self.heartBtn.setContentsMargins(0,0,0,0)
        self.heartBtn.setIcon(QIcon(pixmap))
        self.heartBtn.setIconSize(QSize(150,150))
        self.heartBtn.clicked.connect(self.start_button_clicked)
        self.gridWidget.addWidget(self.heartBtn, 1, 0, 1, 6, alignment=Qt.AlignCenter)


        # BPM value
        self.bpmValue = QLabel("--")
        self.bpmValue.setStyleSheet("font-size: 80px; font-weight: bold; color: white; background: transparent;")
        self.gridWidget.addWidget(self.bpmValue, 2, 2, alignment=Qt.AlignCenter)


        # BPM unit
        self.bpmUnit = QLabel("BPM")
        self.bpmUnit.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background: transparent;")
        self.gridWidget.addWidget(self.bpmUnit, 2, 3, alignment=Qt.AlignCenter)

        # graph
        self.graphWidget = QWidget(self)
        self.gridWidget.addWidget(self.graphWidget, 3, 0, 1, 6, alignment=Qt.AlignCenter)

        # Create a QVBoxLayout for the graphWidget
        self.graphLayout = QVBoxLayout(self.graphWidget)


        # Create a pyqtgraph PlotWidget
        self.plotWidget = pg.PlotWidget()


        # Hide axes and grid lines
        self.plotWidget.getAxis('bottom').setStyle(showValues=False)
        self.plotWidget.getAxis('left').setStyle(showValues=False)
        self.plotWidget.getPlotItem().hideAxis('bottom')  # Hide X-axis completely
        self.plotWidget.getPlotItem().hideAxis('left')    # Hide Y-axis completely


        self.graphLayout.addWidget(self.plotWidget)


        # Initialize pyqtgraph PlotDataItem
        self.curve = self.plotWidget.plot()
        color = QColor(255, 0, 0)
        self.curve.setPen(color)


        self.plotWidget.setXRange(0, 30, padding=0)
        self.plotWidget.setYRange(0, 255, padding=0)


        # Create a horizontal line using QFrame
        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)


        # Add the line to the grid layout at row 5, column 0
        self.gridWidget.addWidget(self.line, 5, 0, alignment=Qt.AlignCenter)




        # Other info
        self.impGrid = QGridLayout()
        self.ipmLabel = QLabel("IPM")
        self.ipmLabel.setAlignment(Qt.AlignCenter)
        self.ipmLabel.setStyleSheet("font-size: 14px; color: grey; background: transparent;")
        self.impGrid.addWidget(self.ipmLabel, 0, 0, alignment=Qt.AlignCenter)
        self.ipmValue = QLabel("--")
        self.ipmValue.setStyleSheet("font-size: 28px; color: white; background: transparent;")
        self.impGrid.addWidget(self.ipmValue, 1, 0, alignment=Qt.AlignCenter)
        self.gridWidget.addLayout(self.impGrid, 6, 0)


        self.hrstdGrid = QGridLayout()
        self.hrstdLabel = QLabel("HRSTD")
        self.hrstdLabel.setAlignment(Qt.AlignCenter)
        self.hrstdLabel.setStyleSheet("font-size: 14px; color: grey; background: transparent;")
        self.hrstdGrid.addWidget(self.hrstdLabel, 0, 0, alignment=Qt.AlignCenter)
        self.hrstdValue = QLabel("--")
        self.hrstdValue.setStyleSheet("font-size: 28px; color: white; background: transparent;")
        self.hrstdGrid.addWidget(self.hrstdValue, 1, 0, alignment=Qt.AlignCenter)
        self.gridWidget.addLayout(self.hrstdGrid, 6, 2)


        self.rmssdGrid = QGridLayout()
        self.rmssdLabel = QLabel("RMSSD")
        self.rmssdLabel.setAlignment(Qt.AlignCenter)
        self.rmssdLabel.setStyleSheet("font-size: 14px; color: grey; background: transparent;")
        self.rmssdGrid.addWidget(self.rmssdLabel, 0, 0, alignment=Qt.AlignCenter)
        self.rmssdValue = QLabel("--")
        self.rmssdValue.setStyleSheet("font-size: 28px; color: white; background: transparent;")
        self.rmssdGrid.addWidget(self.rmssdValue, 1, 0, alignment=Qt.AlignCenter)
        self.gridWidget.addLayout(self.rmssdGrid, 6, 4)


        self.calcBPM = CalcBPM()
        self.thread = QThread()
        self.calcBPM.moveToThread(self.thread)


        self.calcBPM.bpmList = np.array([])


        self.thread.started.connect(self.calcBPM.run)
        self.thread.start()


    # Update the graph with new dialog data (last 30 seconds)
    def update_graph(self):
        self.calcBPM.bpmList = self.calcBPM.bpmList[-30:]
        self.curve.setData(np.arange(0, self.calcBPM.bpmList.size, 1), self.calcBPM.bpmList)
        self.bpmValue.setText((str(self.calcBPM.bpm) if self.calcBPM.bpm >= 0 else "--"))
        self.ipmValue.setText((str(self.calcBPM.bpm) if self.calcBPM.bpm >= 0 else "--"))
        self.hrstdValue.setText((str(self.calcBPM.hrstd) if self.calcBPM.hrstd >= 0 else "--"))
        self.rmssdValue.setText((str(self.calcBPM.rmssd) if self.calcBPM.rmssd >= 0 else "--"))


    def start_button_clicked(self):

        # Pairing using bluetoothctl
        subprocess.call(['bluetoothctl', 'discoverable', 'yes'])
        subprocess.call(['bluetoothctl', 'pairable', 'yes'])

        server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_socket.bind((host_mac_address, port))
        server_socket.listen(backlog)

        print("Waiting for connection...")
        global client_socket
        #client_socket, client_info = server_socket.accept()
        #print(f"Accepted connection from {client_info}")

        self.calcBPM.running = True
        self.bpm_timer.start(100)  # Graph update thread
        self.heartBtn.setIcon(QIcon(PATH + 'heart_stop.png'))
        self.heartBtn.clicked.connect(self.stop_button_clicked)



    def stop_button_clicked(self):
        self.bpm_timer.stop()
        self.calcBPM.running = False


        # Clear the bpmList
        self.calcBPM.bpmList = np.array([])
        self.calcBPM.bpm = -1
        self.curve.setData(np.arange(0, self.calcBPM.bpmList.size, 1), self.calcBPM.bpmList)
        self.bpmValue.setText("--")
        self.heartBtn.setIcon(QIcon(PATH + 'heart_init.png'))
        self.heartBtn.clicked.connect(self.start_button_clicked)




class MainWindow(QMainWindow):#self.title.setStyleSheet("font-size: 35px; font-weight: bold; color: white; background: transparent;")
    def __init__(self):
        super(MainWindow, self).__init__()


        # Create a stacked widget to manage pages
        self.stackedWidget = QStackedWidget(self)


        # Add the BPM page to the stacked widget
        self.bpmPage = BPMPage(self.stackedWidget)
        self.stackedWidget.addWidget(self.bpmPage)


        # Set the current index to show the landing page initially
        self.stackedWidget.setCurrentIndex(0)


        # Set up the main window
        self.setCentralWidget(self.stackedWidget)
        self.setWindowTitle("BPM Measurement")
        self.setGeometry(100, 100, 500, 700)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    style = """
        QWidget{
            background: black;
        }
        QPushButton{
            outline: none;
        }
    """
    app.setStyleSheet(style)


    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
