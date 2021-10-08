from PyQt5 import QtWidgets, uic
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys

app = QtWidgets.QApplication([])
ui = uic.loadUi('design.ui')
ui.setWindowTitle('SerialGUI')

serial = QSerialPort()
serial.setBaudRate(9600)
portList = []
ports = QSerialPortInfo().availablePorts()
for port in ports:
    portList.append(port.portName())
ui.comList.addItems(portList)

def onOpen():
    serial.setPortName(ui.comList.currentText())
    serial.open(QIODevice.ReadWrite)

def onClose():
    serial.close()

posX, posY = 430, 0
listX, listY = [], []
for x in range(100):
    listX.append(x)
    listY.append(0)

def onRead():
    rx = serial.readLine()
    rxs = str(rx, 'utf-8').strip()
    data = rxs.split(',')
    if data[0] == '0':
        ui.barTemp.setValue(int(float(data[3])*10))
        ui.labelTemp.setText(data[3])
        ui.lcdNumber.display(data[1])
        global listX; global listY
        listY = listY[1:]
        listY.append(int(data[2]))
        ui.graph.clear()
        ui.graph.plot(listX, listY)
    elif data[0] == '1':
        if data[1] == '0':
            ui.btnCircle.setVisible(True)
            ui.btnCircle.setChecked(True)
        else:
            ui.btnCircle.setChecked(False)
    elif data[0] == '2':
        global posX; global posY
        posX += int((int(data[1]) - 512) / 100)
        posY += int((int(data[2]) - 512) / 100)
        ui.btnCircle.setVisible(True)
        ui.btnCircle.setGeometry(posX, posY, 20, 20)
    else:
        ui.btnCircle.setVisible(False)

def serialSend(data):   #список int
    txs = ''
    for val in data:
        txs += str(val)
        txs += ','
    txs = txs[:-1]
    txs += ';'
    serial.write(txs.encode())  #преобразовали строку в массив байтов

def ledControl(val):
    if val == 2:
        val = 1
    serialSend([0, val])

def fanControl(val):
    if val == 2:
        val = 1
    serialSend([3, val])

def bulbControl(val):
    if val == 2:
        val = 1
    serialSend([4, val])

def rgbControl():
    serialSend([1, ui.sliderR.value(), ui.sliderB.value(), ui.sliderG.value()])

def servoControl(val):
    serialSend(([2, val]))

def sendText():
    txs = '5,'
    txs += ui.textField.displayText()
    txs += ';'
    serial.write(txs.encode())


serial.readyRead.connect(onRead)

ui.btnOpen.clicked.connect(onOpen)
ui.btnClose.clicked.connect(onClose)

ui.checkBoxLED.stateChanged.connect(ledControl)
ui.checkBoxFAN.stateChanged.connect(fanControl)
ui.checkBoxBULB.stateChanged.connect(bulbControl)

ui.sliderR.valueChanged.connect(rgbControl)
ui.sliderG.valueChanged.connect(rgbControl)
ui.sliderB.valueChanged.connect(rgbControl)

ui.servoAngel.valueChanged.connect(servoControl)

ui.btnSend.clicked.connect(sendText)

ui.btnCircle.setGeometry(posX, posY, 20, 20)

ui.show()
app.exec()

