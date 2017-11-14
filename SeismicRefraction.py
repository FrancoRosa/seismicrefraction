# Done by Franco 08/09/2017

# -*- coding: utf-8 -*-

# Software for seismic refraction test, it should take samples as fast as possible,
# Acording to the serial test of arduino sampling frecuency of both channels is less
# than 2ms, this script should get data and plot 10s of data as maximun

# This software consists in two threads one for getting all data from logger
# the second one will plot the gattered data each 200ms of test

# We will use PyQTGraph as plottinf library 
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time, serial, csv


##########################################################
dataLen=  200 # Numero de Muestras de buffer
plotTime = 1
plotLen =  plotTime*1000#Numero de Muestras totales
getTimer = 1
plotTimer= 200
serialPort = "COM17"
threshold = 50
flagStart = False
##########################################################

cPort = serial.Serial(port=serialPort,
                      baudrate=115200, 
                      timeout=0.0005)

# Data buffer
dataX = [0]*dataLen # Geophone 1 data
dataY = [0]*dataLen # Geophone 2 data
dataT = [0]*dataLen # time data

# plot array
def matrixInit():
    global plotX, plotY,plotT
    plotX = [0]*plotLen # Geophone 1 data
    plotY = [0]*plotLen # Geophone 2 data
    plotT = np.arange(0.0, plotLen*.001, 0.001) # time data

matrixInit()
#flagPlot=False


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


# Simple ADC plot
fig1 = pg.PlotWidget(title="Medicion de Refraccion Sismica")
fig1.setLabel(axis="bottom",text="Tiempo (s)")
fig1.setLabel(axis="left",text="Amplitud (mV)")
fig1.showGrid(x=True, y=True)
fig1.addLegend()


fig2 = pg.PlotWidget(title="Medicion de Refraccion Sismica")
fig2.setLabel(axis="bottom",text="Tiempo (s)")
fig2.setLabel(axis="left",text="Amplitud (mV)")
fig2.showGrid(x=True, y=True)
fig2.addLegend()
fig2.setXLink(fig1)
fig2.setYLink(fig1)

curve1f1 = fig1.plot(pen='y',name="__G. Salida")
curve2f1 = fig2.plot(pen='g',name="__G. Llegada")


label = QtGui.QLabel("-")
thresLabel = QtGui.QLabel("Humbral:")
thresEdit = QtGui.QLineEdit(str(threshold))
timeLabel = QtGui.QLabel("Duracion:")
timeEdit = QtGui.QLineEdit(str(plotTime))
strstpBtn = QtGui.QPushButton('Inicio/Reset')
saveBtn = QtGui.QPushButton('Guardar')
exitBtn = QtGui.QPushButton('Salir')

thresLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
timeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
thresEdit.setMaxLength(3)
thresEdit.setMaximumSize(QtCore.QSize(0.1 * thresEdit.width(),thresEdit.height()))
timeEdit.setMaxLength(3)
timeEdit.setMaximumSize(QtCore.QSize(0.1 * timeEdit.width(),timeEdit.height()))

win.showFullScreen()
win1.addWidget(fig1,0,0,1,10)
win1.nextRow()
win1.addWidget(fig2,1,0,1,10)
win1.nextRow()
win1.addWidget(label,col=0)
win1.addWidget(thresLabel,col=3)
win1.addWidget(thresEdit,col=4)
win1.addWidget(timeLabel,col=5)
win1.addWidget(timeEdit,col=6)
win1.addWidget(strstpBtn,col=7)
win1.addWidget(saveBtn,col=8)
win1.addWidget(exitBtn,col=9)

def changeThreshold():
    global threshold
    threshold = int(thresEdit.text())

def changeTime():
    global plotTime, plotLen
    plotTime = int(timeEdit.text())
    plotLen = plotTime*1000
    matrixInit()

def startstop():
    for n in range(plotLen):
        plotX[n]=0
        plotY[n]=0

def savecsv(self):
    path = QtGui.QFileDialog.getSaveFileName(
        parent = None, 
        caption='Guardar Archivo', 
        directory='', 
        filter='CSV(*.csv)')

    if not path.isEmpty():
        with open(unicode(path).replace('.csv','_ref.csv'), 'wb') as stream:
            writer = csv.writer(stream)
            writer.writerow([time.ctime()])
            writer.writerow(['t','G1','G2'])
            for row in range(plotLen):
                rawdata = [plotT[row], plotX[row], plotY[row]]
                writer.writerow(rawdata)



def exit():
    app.quit()

strstpBtn.clicked.connect(startstop)    
saveBtn.clicked.connect(savecsv)    
exitBtn.clicked.connect(exit)    
thresEdit.textEdited.connect(changeThreshold)
timeEdit.textEdited.connect(changeTime)


# Simple ADC plot
def loadData(part,total,index):
    try:
        print "ZZZZZZIndex", index
        for z in range(len(part)):
            total[index+z] = part[z]
        print "index+z" ,index+z
        print "z" ,z
        print "t" ,t
        print "k" ,k
        return total

    except:
        print "!!!!!!!!!ERROR loading data"

k = 0;
t = 0;

def getData():
    global flagPlot,dataX,dataY,dataT,plotX,plotY,plotT,k,t
    global flagStart
    #while True:
    rawstring = cPort.readline();
    #try:
    if ' ' in rawstring:
        try:
            rawdata = rawstring.split(' ')
            rawX = rawdata[0]         
            rawY = rawdata[1]         
            dataX[k]=int(rawX,16)-512
            dataY[k]=int(rawY,16)-512
            dataT[k]=t*0.001
            if (dataX[k]>threshold):
                flagStart=True
            
            if flagStart:
                k=k+1
                t=t+1
        except:
            print "DataError"
            pass

        if (k >= dataLen):
            print "blockComplete"
            flagPlot = True
            
            if flagStart:
                plotX = loadData(dataX,plotX,t-k)
                plotY = loadData(dataY,plotY,t-k)
                plotT = loadData(dataT,plotT,t-k)

            if t>=plotLen:
                print "t, before Reset" , t
                t=0
                flagStart = False
                flagPlot = False

            print "k before Reset", k
            k = 0
            #break
    #except:
    #    print "DataError"
    #    break
            

def plotData():
    global flagPlot,plotX,plotY,plotT
    #if flagPlot:
    curve1f1.setData(plotT,plotX)
    curve2f1.setData(plotT,plotY)
    #    flagPlot=False;

timer2 = QtCore.QTimer()
timer2.timeout.connect(plotData)
timer2.start(plotTimer) 


timer1 = QtCore.QTimer()
timer1.timeout.connect(getData)
#timer1.setSingleShot(True)
timer1.start(getTimer)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
