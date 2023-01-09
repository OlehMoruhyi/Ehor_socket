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
        self.setFixedSize(441, 800)

        self.receiveThread_1 = threading.Thread(target=self.receive_messages)  # Получение всех сообщений
        self.receiveThread_2 = threading.Thread(target=self.enter_send)  # Получение всех сообщений

        self.threadCloser = False

        self.messageLine_1 = QtWidgets.QLineEdit(self)
        self.messageLine_1.setGeometry(QtCore.QRect(30, 690, 281, 31))
        self.messageLine_1.setObjectName("messageLine_1")

        self.messageButton_1 = QtWidgets.QPushButton(self)
        self.messageButton_1.setGeometry(QtCore.QRect(320, 690, 93, 31))
        self.messageButton_1.setObjectName("messageButton_1")
        self.messageButton_1.clicked.connect(lambda x: self.send_messages(self.messageLine_1))

        self.textEdit_1 = QtWidgets.QTextEdit(self)
        self.textEdit_1.setGeometry(QtCore.QRect(30, 45, 381, 631))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.textEdit_1.setFont(font)
        self.textEdit_1.setObjectName("textEdit_1")

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        font_2 = QtGui.QFont()
        font_2.setPointSize(16)

        self.button_0 = QtWidgets.QPushButton(self)
        self.button_0.setGeometry(45, 740, 41, 41)
        self.button_0.setFont(font_2)
        self.button_0.setText("❤")
        self.button_0.clicked.connect(lambda x: self.smile("❤"))
        self.button_1 = QtWidgets.QPushButton(self)
        self.button_1.setGeometry(106, 740, 41, 41)
        self.button_1.setFont(font_2)
        self.button_1.setText("😊")
        self.button_1.clicked.connect(lambda x: self.smile("😊"))
        self.button_2 = QtWidgets.QPushButton(self)
        self.button_2.setGeometry(167, 740, 41, 41)
        self.button_2.setFont(font_2)
        self.button_2.setText("😂")
        self.button_2.clicked.connect(lambda x: self.smile("😂"))
        self.button_3 = QtWidgets.QPushButton(self)
        self.button_3.setGeometry(228, 740, 41, 41)
        self.button_3.setFont(font_2)
        self.button_3.setText("😍")
        self.button_3.clicked.connect(lambda x: self.smile("😍"))
        self.button_4 = QtWidgets.QPushButton(self)
        self.button_4.setGeometry(289, 740, 41, 41)
        self.button_4.setFont(font_2)
        self.button_4.setText("😒")
        self.button_4.clicked.connect(lambda x: self.smile("😒"))
        self.button_5 = QtWidgets.QPushButton(self)
        self.button_5.setGeometry(350, 740, 41, 41)
        self.button_5.setFont(font_2)
        self.button_5.setText("🖕")
        self.button_5.clicked.connect(lambda x: self.smile("🖕"))

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Anonymous chat"))
        self.messageButton_1.setText(_translate("MainWindow", "Send"))

    def start(self):
        self.show()
        self.receiveThread_1.start()
        self.receiveThread_2.start()

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

    def smile(self, smile):
        self.messageLine_1.setText(self.messageLine_1.text() + smile)

    def receive_messages(self):
        while not self.threadCloser:  # Подтверждение соединения
            try:
                message = json.loads(self.client.recv(8192).decode('utf-8'))
                match message.get('command'):
                    case 'message':
                        self.textEdit_1.append(str(message.get('content', 'no_content')))
                    case _:
                        print("Fucking wrong")

            except Exception as e:  # Если неправильный ip или порт
                print(e.__class__)
                print(e)
                self.textEdit_1.append(str(e))
                self.client.close()
                break




app = QtWidgets.QApplication(sys.argv)
app_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Инициализация сокета
app_client.connect((host, port))  # Соединение клиента с сервером
registration_window = Registration(app_client)
registration_window.show()

sys.exit(app.exec_())
