#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time, serial, csv
import sys, glob

##########################################################
plotLen =  500#Numero de Muestras totales
threshold = 50
ksamples = 50
msamples = plotLen/ksamples
geophone = "Out"
##########################################################


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            print "SerialPort:", port
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

serialPorts = serial_ports()

if len(serialPorts)>=1:
    serialPort=serialPorts[0]
    print "SerialPort:", serialPort
    cPort = serial.Serial(port=serialPort,
                      baudrate=115200, 
                      timeout=1)
# plot array
def matrixInit():
    global plotY,plotT
    plotY = [0]*plotLen # Geophone 2 data
    plotT = np.arange(0.0, plotLen*1.0/ksamples, 1.0/ksamples) # time data

matrixInit()


#############################
# Grapichs Layout
#############################
app = QtGui.QApplication([])
win = QtGui.QMainWindow()
win.setWindowTitle('Refraccion Sismica')
win.resize(1000,600)
pg.setConfigOptions(antialias=True)

#############################
# Layout
win1 = pg.LayoutWidget()
win.setCentralWidget(win1)

fig2 = pg.PlotWidget(title='<div style="text-align: center;"><span style="color: #FF0; font-size: 14pt;">Refraccion Sismica</span></div>')
fig2.setLabel(axis="bottom",text="Tiempo",units="ms")
fig2.setLabel(axis="left",text="Amplitud",units="ms")
fig2.setLabel(axis="top",text='<span style="color: #FF0; font-size: 12pt;">Onda de Llegada</span>')
fig2.setYRange(-500,500);
fig2.showGrid(x=True, y=True)

curve2f1 = fig2.plot(pen='g',name="__G. Llegada")
curve2f1.setData(plotT,plotY)
arrow = pg.ArrowItem(angle=-45)
fig2.addItem(arrow)
textMax = pg.TextItem(html='<div style="text-align: center;"><span style="color: #FF0; font-size: 12pt;">Presione Inicio/Reset</span></div>', anchor=(-0.3,1), angle=0, fill=(0, 0, 255, 100))
fig2.addItem(textMax)


portlabel = QtGui.QLabel("Puerto:")
geolabel = QtGui.QLabel("Geofono:")
spelabel = QtGui.QLabel("Frec.:")
thresLabel = QtGui.QLabel("Humbral:")
thresEdit = QtGui.QLineEdit(str(threshold))
timeLabel = QtGui.QLabel("Duracion: 10ms")
strstpBtn = QtGui.QPushButton('Inicio/Reset')
saveBtn = QtGui.QPushButton('Guardar')
exitBtn = QtGui.QPushButton('Salir')

speedSel = QtGui.QComboBox()
speedSel.addItem('50KHz')
speedSel.addItem('25KHz')
speedSel.addItem('10KHz')
speedSel.addItem('5KHz')
#speedSel.addItem('1KHz')

geoSel = QtGui.QComboBox()
geoSel.addItem('Llegada')
geoSel.addItem('Salida')

portSel = QtGui.QComboBox()
for port in serialPorts:
    portSel.addItem(port)

thresLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
geolabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
portlabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
spelabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
timeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)


thresEdit.setMaxLength(3)
thresEdit.setMaximumSize(QtCore.QSize(0.1 * thresEdit.width(),thresEdit.height()))
speedSel.setMaximumSize(QtCore.QSize(0.1 * speedSel.width(),speedSel.height()))


win.showFullScreen()
win1.addWidget(fig2,0,0,1,14)
win1.nextRow()
win1.addWidget(portlabel,col=0)
win1.addWidget(portSel,col=1)
win1.addWidget(geolabel,col=2)
win1.addWidget(geoSel,col=3)
win1.addWidget(spelabel,col=4)
win1.addWidget(speedSel,col=5)
win1.addWidget(timeLabel,col=7)
win1.addWidget(thresLabel,col=8)
win1.addWidget(thresEdit,col=9)
win1.addWidget(strstpBtn,col=11)
win1.addWidget(saveBtn,col=12)
win1.addWidget(exitBtn,col=13)

def changeThreshold():
    global threshold
    threshold = int(thresEdit.text())

def startstop():
    matrixInit()
    textMax.setHtml('<div style="text-align: center;"><span style="color: #FF0; font-size: 12pt;">... Esperando Trigger</span></div>')
    textMax.setPos(0, 0)
    arrow.setPos(0, 0)
    curve2f1.setData(plotT,plotY)
    QtCore.QTimer.singleShot(100, getData)
    
def getData():
    global cPort, threshold
    global plotY,plotT
    if geophone=="In":
        insgeophone='0'
    if geophone=="Out":
        insgeophone='1'
    insamples = ksamples/5
    if insamples == 10:
        insamples = 0

    instruction = "%s%d%s\r"%(insgeophone,insamples,str(threshold))
    
    cPort.write(instruction)
    while True:
        outPut = cPort.readline()
        if ":" in outPut:
            outPut = outPut.replace("\r\n","")
            outPut = outPut.split(":")
            index = int(outPut[0]) 
            value = int(outPut[1])-512
            plotY[index]=value
            if index == 499:
                break
    maxValue = max(plotY)
    maxValueTime = plotT[plotY.index(maxValue)]
    textMax.setHtml('<div style="text-align: center;"><span style="color: #FF0; font-size: 12pt;">%2.2fms %2.2fV</span></div>'%(maxValueTime,maxValue/1023.0))
    textMax.setPos(maxValueTime, maxValue)
    arrow.setPos(maxValueTime, maxValue)
    curve2f1.setData(plotT,plotY)
    

def savecsv(self):
    path = QtGui.QFileDialog.getSaveFileName(
        parent = None, 
        caption='Guardar Archivo', 
        directory='', 
        filter='CSV(*.csv)')
    datetime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    if not path.isEmpty():

        with open(unicode(path.append('_%s.csv'%datetime)), 'wb') as stream:
            writer = csv.writer(stream)
            writer.writerow(['Fecha:',time.strftime("%Y/%m/%d", time.localtime())])
            writer.writerow(['Hora:',time.strftime("%H:%M:%S", time.localtime())])
            writer.writerow(['Geofono:',geoSel.currentText()])
            writer.writerow(['Muestreo:',speedSel.currentText()])
            
            writer.writerow(['t(ms)','G(mv)'])
            for row in range(plotLen):
                rawdata = [plotT[row], plotY[row]]
                writer.writerow(rawdata)

def speed():
    global ksamples
    ksamples = int(speedSel.currentText().replace("KHz",""))
    msamples = plotLen/ksamples
    timeLabel.setText('Duracion: %dms'%msamples)
    matrixInit()
    curve2f1.setData(plotT,plotY)

def portsel():
    global cPort
    serialPort = str(portSel.currentText())
    print "SerialPort:", serialPort
    cPort = serial.Serial(port=serialPort,
                  baudrate=115200, 
                  timeout=1)

def geosel():
    global geophone
    if geoSel.currentText()=='Salida':
        geophone='In'
        fig2.setLabel(axis="top",text='<span style="color: #FF0; font-size: 12pt;"><center>Onda de Salida</center></span>')
    
    if geoSel.currentText()=='Llegada':
        geophone='Out'
        fig2.setLabel(axis="top",text='<center><span style="color: #FF0; font-size: 12pt;">Onda de Llegada</span></center>')

def exit():
    app.quit()

strstpBtn.clicked.connect(startstop)    
saveBtn.clicked.connect(savecsv)    
exitBtn.clicked.connect(exit)    
thresEdit.textEdited.connect(changeThreshold)
speedSel.activated[str].connect(speed)
portSel.activated[str].connect(portsel)
geoSel.activated[str].connect(geosel)
## Start Qt event loop unless running in interactive mode or using pyside.
QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("windowsvista"))
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

### Escala fija, mejorar datos de escala
# Muestra en 50KhZ, 25KHz
# Muestreo de entrada
# Muestreo de salida
# Mostrar en la pantalla si esta a la espera
# Mostrar los puertos dispponibles