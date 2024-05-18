from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QBasicTimer, QProcess
import os
import sys

# TIMER
timer = QtCore.QTime()

#PACMAN AGENT TYPE
REFLEX = "reflex_agent"
MINIMAX = "minimax_agent"
ALPHA = "alpha_beta_agent"
EXPECTIMAX = "expecti_max_agent"
SEARCH = "SearchAgent"

DFS = "dfs"
BFS = "bfs"
UCS = "ucs"
ASTAR = "astar"

#SEARCH
TINYMAZE = "tinyMaze"
MEDIUMMAZE = "mediumMaze"
BIGMAZE = "bigMaze"

#MAZE
CAPSULE = "capsuleClassic"
CONTEST = "contestClassic"
MEDIUM = "mediumClassic"
MINI = "minimaxClassic"
OPEN = "openClassic"
ORIGINAL = "originalClassic"
SMALL = "smallClassic"
TEST = "testClassic"
TRAPPED = "trappedClassic"
TRICKY = "trickyClassic"

#Enemy
SMART = "directional_ghost"

class Ui_MainWindow(object):

    def __init__(self):
        self.agent_type = ''
        self.ghost_type = ''
        self.title = "Pacman"
        self.maze = ''
        self.iteration = ''
        self.fn = ''
        self.arr = ['python', 'pacman.py']
        self.process = None
        self.click = 0
        self.procTime = 0

    def stopped(self):
        if(self.click == 1):
            self.plainTextEdit.hide()
            self.label_2.hide()
            self.click = 0
        else:
            self.click += 1
        self.process.kill() #stopping the process manually

    def clicked(self):
        timer.start()
        #PACMAN AGENT
        if(self.iterationin.text() == '' or self.comboBox.currentText() == 'No Agent'):
            self.iteration = ''
        else:
            self.iteration = self.iterationin.text()

        if(self.comboBox.currentText() == "Reflex Agent"):
            self.agent_type = REFLEX
        elif(self.comboBox.currentText() == "Alpha Beta Agent"):
            self.agent_type = ALPHA
        elif(self.comboBox.currentText() == "ExpectiMax Agent"):
            self.agent_type = EXPECTIMAX
        elif(self.comboBox.currentText() == "MiniMax Agent"):
            self.agent_type = MINIMAX
        elif(self.comboBox.currentText() == "Search Agent"):
            self.agent_type = SEARCH

        #GHOST agent_type
        if(self.comboBox_2.currentText() == "Smart Agent"):
            self.ghost_type = SMART
        else:
            self.ghost_type = ''

        #maze
        if(self.comboBox_3.currentText() == "Tiny Maze"):
            self.maze = TINYMAZE
        elif(self.comboBox_3.currentText() == "Medium Maze"):
            self.maze = MEDIUMMAZE
        elif(self.comboBox_3.currentText() == "Big Maze"):
            self.maze = BIGMAZE
        elif(self.comboBox_3.currentText() == "Contest Classic"):
            self.maze = CONTEST
        elif(self.comboBox_3.currentText() == "Medium Classic"):
            self.maze = MEDIUM
        elif(self.comboBox_3.currentText() == "Minimax Classic"):
            self.maze = MINI
        elif(self.comboBox_3.currentText() == "Open Classic"):
            self.maze = OPEN
        elif(self.comboBox_3.currentText() == "Capsule Classic"):
            self.maze = CAPSULE
        elif(self.comboBox_3.currentText() == "Small Classic"):
            self.maze = SMALL
        elif(self.comboBox_3.currentText() == "Test Classic"):
            self.maze = TEST
        elif(self.comboBox_3.currentText() == "Trapped Classic"):
            self.maze = TRAPPED
        elif(self.comboBox_3.currentText() == "Tricky Classic"):
            self.maze = TRICKY
        else:
            self.maze = ORIGINAL

        if(self.comboBox_4.currentText() == "DFS"):
            self.fn = "fn="+DFS
        elif(self.comboBox_4.currentText() == "BFS"):
            self.fn = "fn="+BFS
        elif(self.comboBox_4.currentText() == "UCS"):
            self.fn = "fn="+UCS
        elif(self.comboBox_4.currentText() == "ASTAR"):
            self.fn = "fn="+ASTAR+",heuristic=manhattanHeuristic"
        else:
            self.fn = ''

        if(self.maze!=''):
            self.arr.append('-l')
            self.arr.append(self.maze)
        if(self.agent_type!=''):
            self.arr.append('-p')
            self.arr.append(self.agent_type)
        if(self.ghost_type!=''):
            self.arr.append('-g')
            self.arr.append(self.ghost_type)
        if(self.fn!=''):
            self.arr.append('-a')
            self.arr.append(self.fn)
        if(self.iteration!=''):
            self.arr.append('-n')
            self.arr.append(self.iteration)

        # print('Starting process')
        arr = ' '.join(self.arr)
        # print(arr)
        # self.process.start('python', self.arr)

        os.system(arr)
        self.stdoutReady()
        self.arr = ['python', 'pacman.py']
        # self.plainTextEdit.show()
        # self.label_2.show()

    def quitclicked(self):
        app.quit()

    def append(self, text):
        # self.plainTextEdit.clear()
        # self.plainTextEdit.insertPlainText(text)
        print(text)

    def stdoutReady(self):
        # text = bytearray(self.process.readAllStandardOutput())
        # text = text.decode('mbcs')
        self.procTime = timer.elapsed() / 5000
        str = "Thời gian chơi game: {} giây".format(self.procTime)
        print(str)
        # text += str
        # self.append(text)

    def show_processing(self):
        self.plainTextEdit.clear()
        self.plainTextEdit.insertPlainText("Processing..................................")

    def finished(self):
        # print('Finished!')
        self.arr.clear()
        self.arr.append('pacman.py')
        if(self.plainTextEdit.toPlainText() == "Processing.................................."):
            self.plainTextEdit.clear()


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2000, 1000)
        MainWindow.setStyleSheet("#MainWindow { border-image: url(../images/Pacman.png) 0 0 0 0 stretch stretch; }")
        MainWindow.setWindowIcon(QtGui.QIcon('../images/window_pacicon.png'))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.playbutton = QtWidgets.QPushButton(self.centralwidget)
        self.playbutton.setGeometry(QtCore.QRect(830, 870, 300, 100))
        self.playbutton.setStyleSheet("background:transparent;\n"
"font: 87 18pt \"Source Sans Pro Black\";\n"
"color: #0C1735;")
        self.playbutton.setAutoDefault(False)
        self.playbutton.setDefault(False)
        self.playbutton.setFlat(False)
        self.playbutton.setObjectName("playbutton")

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(300, 350, 191, 41))
        self.comboBox.setStyleSheet("background:transparent;\n"
"color:#FFE400;\n"
"font: 87 14pt \"Source Sans Pro Black\";")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(300, 380, 191, 31))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.comboBox_2 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_2.setGeometry(QtCore.QRect(1420, 350, 191, 41))
        self.comboBox_2.setStyleSheet("background:transparent;\n"
"color:#FFE400;\n"
"font: 87 14pt \"HK Modula\";")
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(330, 750, 191, 31))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")

        self.comboBox_3 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_3.setGeometry(QtCore.QRect(330, 720, 191, 41))
        self.comboBox_3.setStyleSheet("background:transparent;\n"
"color:#FFE400;\n"
"font: 87 14pt \"Source Sans Pro Black\";")
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")

        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(1420, 380, 191, 41))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")

        self.comboBox_4 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_4.setGeometry(QtCore.QRect(1420, 740, 191, 31))
        self.comboBox_4.setStyleSheet("background:transparent;\n"
"color:#FFE400;\n"
"font: 87 14pt \"Source Sans Pro Black\";")
        self.comboBox_4.setObjectName("comboBox_4")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")

        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(1420, 770, 191, 16))
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 30, 131, 71))
        self.label.setText("")
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        self.IterationLabel = QtWidgets.QLabel(self.centralwidget)
        self.IterationLabel.setGeometry(QtCore.QRect(850, 600, 181, 41))
        self.IterationLabel.setStyleSheet("font: 87 18pt \"Source Sans Pro Black\";\n"
"color: white;")
        self.IterationLabel.setObjectName("IterationLabel")

        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setGeometry(QtCore.QRect(850, 650, 181, 41))
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")

        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)

        # self.process = QtCore.QProcess(MainWindow)
        self.process = QtCore.QProcess(self.plainTextEdit)
        self.process.readyReadStandardOutput.connect(self.stdoutReady)
        self.process.started.connect(self.show_processing)
        self.process.finished.connect(self.finished)

        self.plainTextEdit.setGeometry(QtCore.QRect(700, 250, 521, 550))
        self.plainTextEdit.hide()
        self.plainTextEdit.setStyleSheet("background-color: rgba(34,36,38,230);\n"
"border:2px solid #FFE400;\n"
"color:white;\n"
"font: 87 12pt \"Consolas\";\n"
"")
        self.plainTextEdit.setDocumentTitle("")
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setBackgroundVisible(False)
        self.plainTextEdit.setCenterOnScroll(True)
        self.plainTextEdit.setObjectName("plainTextEdit")

        self.iterationin = QtWidgets.QLineEdit(self.centralwidget)
        self.iterationin.setGeometry(QtCore.QRect(850, 630, 191, 31))
        self.iterationin.setStyleSheet("background:transparent;\n"
"color:#FFE400;\n"
"border:none;\n"
"font: 87 16pt \"Source Sans Pro Black\";")
        self.iterationin.setObjectName("iterationin")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(700, 220, 201, 21))
        self.label_2.hide()
        self.label_2.setStyleSheet("font: 87 14pt \"Source Sans Pro Black\";\n"
"color: white;")
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Pacman"))
        self.playbutton.setText(_translate("MainWindow", ""))
        self.IterationLabel.setText(_translate("MainWindow", "Iteration"))
        self.comboBox.setItemText(0, _translate("MainWindow", "No Agent"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Reflex Agent"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Alpha Beta Agent"))
        self.comboBox.setItemText(3, _translate("MainWindow", "ExpectiMax Agent"))
        self.comboBox.setItemText(4, _translate("MainWindow", "MiniMax Agent"))
        self.comboBox.setItemText(5, _translate("MainWindow", "Search Agent"))

        self.comboBox_2.setItemText(0, _translate("MainWindow", "Random Agent"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "Smart Agent"))

        self.comboBox_3.setItemText(0, _translate("MainWindow", "Original Classic"))
        self.comboBox_3.setItemText(1, _translate("MainWindow", "Tiny Maze"))
        self.comboBox_3.setItemText(2, _translate("MainWindow", "Medium Maze"))
        self.comboBox_3.setItemText(3, _translate("MainWindow", "Big Maze"))
        self.comboBox_3.setItemText(4, _translate("MainWindow", "Contest Classic"))
        self.comboBox_3.setItemText(5, _translate("MainWindow", "Medium Classic"))
        self.comboBox_3.setItemText(6, _translate("MainWindow", "Minimax Classic"))
        self.comboBox_3.setItemText(7, _translate("MainWindow", "Open Classic"))
        self.comboBox_3.setItemText(8, _translate("MainWindow", "Capsule Classic"))
        self.comboBox_3.setItemText(9, _translate("MainWindow", "Small Classic"))
        self.comboBox_3.setItemText(10, _translate("MainWindow", "Test Classic"))
        self.comboBox_3.setItemText(11, _translate("MainWindow", "Trapped Classic"))
        self.comboBox_3.setItemText(12, _translate("MainWindow", "Tricky Classic"))

        self.comboBox_4.setItemText(0, _translate("MainWindow", "None"))
        self.comboBox_4.setItemText(1, _translate("MainWindow", "DFS"))
        self.comboBox_4.setItemText(2, _translate("MainWindow", "BFS"))
        self.comboBox_4.setItemText(3, _translate("MainWindow", "UCS"))
        self.comboBox_4.setItemText(4, _translate("MainWindow", "ASTAR"))
        self.label_2.setText(_translate("MainWindow", "Terminal Output"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.playbutton.clicked.connect(ui.clicked)
    MainWindow.show()
    sys.exit(app.exec_())
