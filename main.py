# client.py
import socket
import threading
import json
import sys

from config import host, port
from keyboard import is_pressed

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow)


class Window(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client


class Registration(Window):
    def __init__(self, client):
        super().__init__(client)
        self.setWindowTitle("test")
        self.setFixedSize(400, 370)

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 400, 371))
        self.tabWidget.setObjectName("tabWidget")

        self.tabVerification = QtWidgets.QWidget()
        self.tabVerification.setObjectName("tabVerification")

        self.lineLoginVerification = QtWidgets.QLineEdit(self.tabVerification)
        self.lineLoginVerification.setGeometry(QtCore.QRect(100, 70, 200, 41))
        self.lineLoginVerification.setClearButtonEnabled(True)
        self.lineLoginVerification.setObjectName("lineLoginVerification")

        self.linePasswordVerification = QtWidgets.QLineEdit(self.tabVerification)
        self.linePasswordVerification.setGeometry(QtCore.QRect(100, 130, 200, 41))
        self.linePasswordVerification.setClearButtonEnabled(True)
        self.linePasswordVerification.setObjectName("linePasswordVerification")

        self.rememberRadioButton = QtWidgets.QRadioButton(self.tabVerification)
        self.rememberRadioButton.setGeometry(QtCore.QRect(100, 190, 200, 26))
        self.rememberRadioButton.setObjectName("rememberRadioButton")

        self.exceptionVerificationLabel = QtWidgets.QLabel(self.tabVerification)
        self.exceptionVerificationLabel.setGeometry(100, 230, 200, 26)
        self.exceptionVerificationLabel.setObjectName("exceptionVerificationLabel")
        self.exceptionVerificationLabel.setStyleSheet("color: rgb(255,50,50)")

        self.loginButton = QtWidgets.QPushButton(self.tabVerification)
        self.loginButton.setGeometry(QtCore.QRect(100, 280, 201, 29))
        self.loginButton.setObjectName("loginButton")
        self.loginButton.clicked.connect(self.verification)

        self.tabWidget.addTab(self.tabVerification, "")
        self.tabRegistration = QtWidgets.QWidget()
        self.tabRegistration.setObjectName("tabRegistration")

        self.lineLoginRegistration = QtWidgets.QLineEdit(self.tabRegistration)
        self.lineLoginRegistration.setGeometry(QtCore.QRect(100, 20, 200, 41))
        self.lineLoginRegistration.setClearButtonEnabled(True)
        self.lineLoginRegistration.setObjectName("lineLoginRegistration")

        self.exceptionRegistrationLabel = QtWidgets.QLabel(self.tabRegistration)
        self.exceptionRegistrationLabel.setGeometry(100, 230, 200, 26)
        self.exceptionRegistrationLabel.setObjectName("exceptionRegistrationVerificationLabel")
        self.exceptionRegistrationLabel.setStyleSheet("color: rgb(255,50,50)")

        self.linePasswordRegistration_2 = QtWidgets.QLineEdit(self.tabRegistration)
        self.linePasswordRegistration_2.setGeometry(QtCore.QRect(100, 180, 200, 41))
        self.linePasswordRegistration_2.setClearButtonEnabled(True)
        self.linePasswordRegistration_2.setObjectName("linePasswordRegistration_2")

        self.linePasswordRegistration_1 = QtWidgets.QLineEdit(self.tabRegistration)
        self.linePasswordRegistration_1.setGeometry(QtCore.QRect(100, 130, 200, 41))
        self.linePasswordRegistration_1.setClearButtonEnabled(True)
        self.linePasswordRegistration_1.setObjectName("linePasswordRegistration_1")

        self.registrationButton = QtWidgets.QPushButton(self.tabRegistration)
        self.registrationButton.setGeometry(QtCore.QRect(100, 280, 201, 29))
        self.registrationButton.setObjectName("registrationButton")
        self.registrationButton.clicked.connect(self.registration)

        self.tabWidget.addTab(self.tabRegistration, "")

        self.setCentralWidget(self.tabWidget)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")

        self.setStatusBar(self.statusbar)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Verification"))

        with open("login.json") as r:
            remembered = json.load(r)
            self.lineLoginVerification.setText(_translate("MainWindow", remembered.get('login', "Login")))
            self.linePasswordVerification.setText(_translate("MainWindow",
                                                             remembered.get('p@ssword', "Password")))
            r.close()

        self.rememberRadioButton.setText(_translate("MainWindow", "Remember me"))
        self.loginButton.setText(_translate("MainWindow", "Log in"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabVerification), _translate("MainWindow", "Sign in"))
        self.lineLoginRegistration.setText(_translate("MainWindow", "Login"))
        self.linePasswordRegistration_2.setText(_translate("MainWindow", "Password again"))
        self.linePasswordRegistration_1.setText(_translate("MainWindow", "Password"))
        self.registrationButton.setText(_translate("MainWindow", "Registration"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabRegistration),
                                  _translate("MainWindow", "Registration"))

    def verification(self):
        if self.lineLoginVerification.text():
            message = json.dumps({'command': 'verification', 'login': self.lineLoginVerification.text(),
                                  'p@ssword': self.linePasswordVerification.text()})
            self.client.send(message.encode('utf-8'))
            message = self.client.recv(8192).decode('utf-8')
            if self.rememberRadioButton.isChecked():
                with open("login.json", "w") as r:
                    json.dump({'login': self.lineLoginVerification.text(),
                               'p@ssword': self.linePasswordVerification.text()}, r)
                    r.close()
            if message == 'SUCCESS':
                main_window = Application(self.lineLoginVerification.text(), self.client)
                main_window.start()
                self.close()
            else:
                self.exceptionVerificationLabel.setText(message)
        else:
            self.exceptionVerificationLabel.setText("Enter login")

    def registration(self):
        if self.lineLoginRegistration.text():
            if self.linePasswordRegistration_1.text() == self.linePasswordRegistration_2.text():
                message = json.dumps({'command': 'registration', 'login': self.lineLoginRegistration.text(),
                                      'p@ssword': self.linePasswordRegistration_1.text()})
                self.client.send(message.encode('utf-8'))
                message = self.client.recv(8192).decode('utf-8')
                if message == 'SUCCESS':
                    main_window = Application(self.lineLoginRegistration.text(), self.client)
                    main_window.start()
                    self.close()
                else:
                    self.exceptionRegistrationLabel.setText(message)
            else:
                self.exceptionRegistrationLabel.setText("Password does not match")
        else:
            self.exceptionRegistrationLabel.setText("Enter login")


class Application(Window):
    def __init__(self, nickname, client):
        super().__init__(client)

        self.nickname = nickname
        self.setFixedSize(901, 762)

        self.receiveThread_1 = threading.Thread(target=self.receive_messages)  # Получение всех сообщений
        self.receiveThread_2 = threading.Thread(target=self.enter_send)  # Получение всех сообщений

        self.threadCloser = False

        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 901, 741))
        self.tabWidget.setObjectName("tabWidget")

        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")

        self.goButton_1 = QtWidgets.QPushButton(self.tab_1)
        self.goButton_1.setGeometry(QtCore.QRect(35, 35, 80, 80))
        self.goButton_1.setObjectName('goButton_0')
        self.goButton_1.clicked.connect(lambda x: self.send_command("go", 1))
        self.goButton_1.setText("Go to 1")
        self.goButton_2 = QtWidgets.QPushButton(self.tab_1)
        self.goButton_2.setGeometry(QtCore.QRect(125, 35, 80, 80))
        self.goButton_2.setObjectName('goButton_1')
        self.goButton_2.clicked.connect(lambda x: self.send_command("go", 2))
        self.goButton_2.setText("Go to 2")
        self.goButton_3 = QtWidgets.QPushButton(self.tab_1)
        self.goButton_3.setGeometry(QtCore.QRect(215, 35, 80, 80))
        self.goButton_3.setObjectName('goButton_2')
        self.goButton_3.clicked.connect(lambda x: self.send_command("go", 3))
        self.goButton_3.setText("Go to 3")
        self.goButton_4 = QtWidgets.QPushButton(self.tab_1)
        self.goButton_4.setGeometry(QtCore.QRect(305, 35, 80, 80))
        self.goButton_4.setObjectName('goButton_3')
        self.goButton_4.clicked.connect(lambda x: self.send_command("go", 4))
        self.goButton_4.setText("Go to 4")
        self.goButton_5 = QtWidgets.QPushButton(self.tab_1)
        self.goButton_5.setGeometry(QtCore.QRect(395, 35, 80, 80))
        self.goButton_5.setObjectName('goButton_4')
        self.goButton_5.clicked.connect(lambda x: self.send_command("go", 5))
        self.goButton_5.setText("Go to 5")

        self.fightButtons = []
        self.fightButton_0 = QtWidgets.QPushButton(self.tab_1)
        self.fightButton_0.setGeometry(QtCore.QRect(35, 250, 440, 40))
        self.fightButton_0.setObjectName('fightButton_0')
        self.fightButton_0.clicked.connect(lambda x: self.send_command("fight", 0))
        self.fightButtons.append(self.fightButton_0)
        self.fightButton_1 = QtWidgets.QPushButton(self.tab_1)
        self.fightButton_1.setGeometry(QtCore.QRect(35, 300, 440, 40))
        self.fightButton_1.setObjectName('fightButton_1')
        self.fightButton_1.clicked.connect(lambda x: self.send_command("fight", 1))
        self.fightButtons.append(self.fightButton_1)
        self.fightButton_2 = QtWidgets.QPushButton(self.tab_1)
        self.fightButton_2.setGeometry(QtCore.QRect(35, 350, 440, 40))
        self.fightButton_2.setObjectName('fightButton_2')
        self.fightButton_2.clicked.connect(lambda x: self.send_command("fight", 2))
        self.fightButtons.append(self.fightButton_2)

        self.duelButtons = []
        self.duelButton_0 = QtWidgets.QPushButton(self.tab_1)
        self.duelButton_0.setGeometry(QtCore.QRect(35, 550, 440, 40))
        self.duelButton_0.setObjectName('duelButton_0')
        self.duelButton_0.clicked.connect(lambda x: self.send_command("duel", 0))
        self.duelButtons.append(self.duelButton_0)
        self.duelButton_1 = QtWidgets.QPushButton(self.tab_1)
        self.duelButton_1.setGeometry(QtCore.QRect(35, 600, 440, 40))
        self.duelButton_1.setObjectName('duelButton_1')
        self.duelButton_1.clicked.connect(lambda x: self.send_command("duel", 1))
        self.duelButtons.append(self.duelButton_1)

        self.messageLine_1 = QtWidgets.QLineEdit(self)
        self.messageLine_1.setGeometry(QtCore.QRect(510, 690, 281, 31))
        self.messageLine_1.setObjectName("messageLine_1")

        self.messageButton_1 = QtWidgets.QPushButton(self)
        self.messageButton_1.setGeometry(QtCore.QRect(800, 690, 93, 31))
        self.messageButton_1.setObjectName("messageButton_1")
        self.messageButton_1.clicked.connect(lambda x: self.send_messages(self.messageLine_1))

        self.textEdit_1 = QtWidgets.QTextEdit(self)
        self.textEdit_1.setGeometry(QtCore.QRect(510, 45, 381, 631))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.textEdit_1.setFont(font)
        self.textEdit_1.setObjectName("textEdit_1")

        self.tabWidget.addTab(self.tab_1, "Main")

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.statsLabel = QtWidgets.QLabel(self.tab_2)
        self.statsLabel.setGeometry(QtCore.QRect(35, 35, 400, 200))
        self.statsLabel.setObjectName('statsLabel')

        self.inventoryButtons = []
        self.inventoryButton_0 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_0.setGeometry(QtCore.QRect(35, 250, 80, 80))
        self.inventoryButton_0.setObjectName('inventoryButton_0')
        self.inventoryButton_0.clicked.connect(lambda x: self.send_command("equip", 0))
        self.inventoryButtons.append(self.inventoryButton_0)
        self.inventoryButton_1 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_1.setGeometry(QtCore.QRect(125, 250, 80, 80))
        self.inventoryButton_1.setObjectName('inventoryButton_1')
        self.inventoryButton_1.clicked.connect(lambda x: self.send_command("equip", 1))
        self.inventoryButtons.append(self.inventoryButton_1)
        self.inventoryButton_2 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_2.setGeometry(QtCore.QRect(215, 250, 80, 80))
        self.inventoryButton_2.setObjectName('inventoryButton_2')
        self.inventoryButton_2.clicked.connect(lambda x: self.send_command("equip", 2))
        self.inventoryButtons.append(self.inventoryButton_2)
        self.inventoryButton_3 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_3.setGeometry(QtCore.QRect(305, 250, 80, 80))
        self.inventoryButton_3.setObjectName('inventoryButton_3')
        self.inventoryButton_3.clicked.connect(lambda x: self.send_command("equip", 3))
        self.inventoryButtons.append(self.inventoryButton_3)
        self.inventoryButton_4 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_4.setGeometry(QtCore.QRect(395, 250, 80, 80))
        self.inventoryButton_4.setObjectName('inventoryButton_4')
        self.inventoryButton_4.clicked.connect(lambda x: self.send_command("equip", 4))
        self.inventoryButtons.append(self.inventoryButton_4)
        self.inventoryButton_5 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_5.setGeometry(QtCore.QRect(35, 340, 80, 80))
        self.inventoryButton_5.setObjectName('inventoryButton_5')
        self.inventoryButton_5.clicked.connect(lambda x: self.send_command("equip", 5))
        self.inventoryButtons.append(self.inventoryButton_5)
        self.inventoryButton_6 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_6.setGeometry(QtCore.QRect(125, 340, 80, 80))
        self.inventoryButton_6.setObjectName('inventoryButton_6')
        self.inventoryButton_6.clicked.connect(lambda x: self.send_command("equip", 6))
        self.inventoryButtons.append(self.inventoryButton_6)
        self.inventoryButton_7 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_7.setGeometry(QtCore.QRect(215, 340, 80, 80))
        self.inventoryButton_7.setObjectName('inventoryButton_7')
        self.inventoryButton_7.clicked.connect(lambda x: self.send_command("equip", 7))
        self.inventoryButtons.append(self.inventoryButton_7)
        self.inventoryButton_8 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_8.setGeometry(QtCore.QRect(305, 340, 80, 80))
        self.inventoryButton_8.setObjectName('inventoryButton_8')
        self.inventoryButton_8.clicked.connect(lambda x: self.send_command("equip", 8))
        self.inventoryButtons.append(self.inventoryButton_8)
        self.inventoryButton_9 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_9.setGeometry(QtCore.QRect(395, 340, 80, 80))
        self.inventoryButton_9.setObjectName('inventoryButton_9')
        self.inventoryButton_9.clicked.connect(lambda x: self.send_command("equip", 9))
        self.inventoryButtons.append(self.inventoryButton_9)
        self.inventoryButton_10 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_10.setGeometry(QtCore.QRect(35, 430, 80, 80))
        self.inventoryButton_10.setObjectName('inventoryButton_10')
        self.inventoryButton_10.clicked.connect(lambda x: self.send_command("equip", 10))
        self.inventoryButtons.append(self.inventoryButton_10)
        self.inventoryButton_11 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_11.setGeometry(QtCore.QRect(125, 430, 80, 80))
        self.inventoryButton_11.setObjectName('inventoryButton_11')
        self.inventoryButton_11.clicked.connect(lambda x: self.send_command("equip", 11))
        self.inventoryButtons.append(self.inventoryButton_11)
        self.inventoryButton_12 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_12.setGeometry(QtCore.QRect(215, 430, 80, 80))
        self.inventoryButton_12.setObjectName('inventoryButton_12')
        self.inventoryButton_12.clicked.connect(lambda x: self.send_command("equip", 12))
        self.inventoryButtons.append(self.inventoryButton_12)
        self.inventoryButton_13 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_13.setGeometry(QtCore.QRect(305, 430, 80, 80))
        self.inventoryButton_13.setObjectName('inventoryButton_13')
        self.inventoryButton_13.clicked.connect(lambda x: self.send_command("equip", 13))
        self.inventoryButtons.append(self.inventoryButton_13)
        self.inventoryButton_14 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_14.setGeometry(QtCore.QRect(395, 430, 80, 80))
        self.inventoryButton_14.setObjectName('inventoryButton_14')
        self.inventoryButton_14.clicked.connect(lambda x: self.send_command("equip", 14))
        self.inventoryButtons.append(self.inventoryButton_14)
        self.inventoryButton_15 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_15.setGeometry(QtCore.QRect(35, 520, 80, 80))
        self.inventoryButton_15.setObjectName('inventoryButton_15')
        self.inventoryButton_15.clicked.connect(lambda x: self.send_command("equip", 15))
        self.inventoryButtons.append(self.inventoryButton_15)
        self.inventoryButton_16 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_16.setGeometry(QtCore.QRect(125, 520, 80, 80))
        self.inventoryButton_16.setObjectName('inventoryButton_16')
        self.inventoryButton_16.clicked.connect(lambda x: self.send_command("equip", 16))
        self.inventoryButtons.append(self.inventoryButton_16)
        self.inventoryButton_17 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_17.setGeometry(QtCore.QRect(215, 520, 80, 80))
        self.inventoryButton_17.setObjectName('inventoryButton_17')
        self.inventoryButton_17.clicked.connect(lambda x: self.send_command("equip", 17))
        self.inventoryButtons.append(self.inventoryButton_17)
        self.inventoryButton_18 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_18.setGeometry(QtCore.QRect(305, 520, 80, 80))
        self.inventoryButton_18.setObjectName('inventoryButton_18')
        self.inventoryButton_18.clicked.connect(lambda x: self.send_command("equip", 18))
        self.inventoryButtons.append(self.inventoryButton_18)
        self.inventoryButton_19 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_19.setGeometry(QtCore.QRect(395, 520, 80, 80))
        self.inventoryButton_19.setObjectName('inventoryButton_19')
        self.inventoryButton_19.clicked.connect(lambda x: self.send_command("equip", 19))
        self.inventoryButtons.append(self.inventoryButton_19)
        self.inventoryButton_20 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_20.setGeometry(QtCore.QRect(35, 610, 80, 80))
        self.inventoryButton_20.setObjectName('inventoryButton_20')
        self.inventoryButton_20.clicked.connect(lambda x: self.send_command("equip", 20))
        self.inventoryButtons.append(self.inventoryButton_20)
        self.inventoryButton_21 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_21.setGeometry(QtCore.QRect(125, 610, 80, 80))
        self.inventoryButton_21.setObjectName('inventoryButton_21')
        self.inventoryButton_21.clicked.connect(lambda x: self.send_command("equip", 21))
        self.inventoryButtons.append(self.inventoryButton_21)
        self.inventoryButton_22 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_22.setGeometry(QtCore.QRect(215, 610, 80, 80))
        self.inventoryButton_22.setObjectName('inventoryButton_22')
        self.inventoryButton_22.clicked.connect(lambda x: self.send_command("equip", 22))
        self.inventoryButtons.append(self.inventoryButton_22)
        self.inventoryButton_23 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_23.setGeometry(QtCore.QRect(305, 610, 80, 80))
        self.inventoryButton_23.setObjectName('inventoryButton_23')
        self.inventoryButton_23.clicked.connect(lambda x: self.send_command("equip", 23))
        self.inventoryButtons.append(self.inventoryButton_23)
        self.inventoryButton_24 = QtWidgets.QPushButton(self.tab_2)
        self.inventoryButton_24.setGeometry(QtCore.QRect(395, 610, 80, 80))
        self.inventoryButton_24.setObjectName('inventoryButton_24')
        self.inventoryButton_24.clicked.connect(lambda x: self.send_command("equip", 24))
        self.inventoryButtons.append(self.inventoryButton_24)

        self.tabWidget.addTab(self.tab_2, "Inventory")

        self.setCentralWidget(self.tabWidget)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.messageButton_1.setText(_translate("MainWindow", "Send"))

    def send_command(self, command, cell):
        message = json.dumps({"command": command, "id": cell})
        self.client.send(message.encode('utf-8'))

    def start(self):
        self.show()
        self.receiveThread_1.start()
        self.receiveThread_2.start()
        self.client.send(json.dumps({"command": "get_info"}).encode('utf-8'))

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self,
                                               "QUIT",
                                               "Are you sure want to stop process?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            self.threadCloser = True
            self.client.send(json.dumps({'command': 'close'}).encode('utf-8'))
            event.accept()
        else:
            event.ignore()

    def send_messages(self, message_line):
        if message_line.text():
            message = json.dumps({'command': 'message', 'content': '{}: {}'.format(self.nickname, message_line.text())})
            message_line.clear()
            self.client.send(message.encode('utf-8'))

    def enter_send(self):
        while not self.threadCloser:
            if is_pressed("\n"):
                self.send_messages(self.messageLine_1)

    def receive_messages(self):
        while not self.threadCloser:  # Подтверждение соединения
            try:
                message = json.loads(self.client.recv(8192).decode('utf-8'))
                match message.get('command'):
                    case 'message':
                        self.textEdit_1.append(str(message.get('content', 'no_content')))
                    case 'info':
                        self.set_info(message)
                    case 'only_user_message':
                        self.textEdit_1.append(str(message.get('content', 'no_content')))
                        self.client.send(json.dumps({"command": "get_info"}).encode('utf-8'))

            except Exception as e:  # Если неправильный ip или порт
                print(e.__class__)
                print(e)
                self.textEdit_1.append(str(e))
                self.client.close()
                break

    def set_info(self, message):
        self.statsLabel.setText(message['stats'])
        for i in self.inventoryButtons:
            i.setText("")
        for i in self.fightButtons:
            i.setText("")
        for i in self.duelButtons:
            i.setText("")
        for i in range(len(message["inventory"])):
            self.inventoryButtons[i].setText(
                str(message["inventory"][i]["name"].replace(" ", "\n"))+" "+str(message["inventory"][i]["level"]))
        for i in range(len(message["beasts"])):
            text = "Fight "

            match message["beasts"][i]:
                case 1: text += "weak "
                case 2: text += "average "
                case 3: text += "big "
            match message["location"]:
                case 1: text += "healthy "
                case 2: text += "fire "
                case 3: text += "air "
                case 4: text += "water "
                case 5: text += "earth "
            text += "beast"
            self.fightButtons[i].setText(text)
        for i in range(len(message["duels"])):
            self.duelButtons[i].setText("Fight " + message["duels"][i])


app = QtWidgets.QApplication(sys.argv)
app_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Инициализация сокета
app_client.connect((host, port))  # Соединение клиента с сервером
registration_window = Registration(app_client)
registration_window.show()

sys.exit(app.exec_())
