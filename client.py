"""Chat client"""
from PyQt5 import QtWidgets, QtNetwork, QtCore
import sys


class ClientWin(QtWidgets.QWidget):
    """
    Create Window for the client
    """

    def __init__(self, user):
        """
        Initialize chat window
        :param user: User's name
        """
        super().__init__()
        self.user = user

        self.user_list = []
        self.sock = QtNetwork.QTcpSocket()
        # self.sock.connectToHost(QtNetwork.QHostAddress('X.X.X.X'), 6666)
        self.sock.connectToHost(QtNetwork.QHostAddress.LocalHost, 6666)
        self.sock.write(bytes(self.user, 'utf8'))
        self.error_mess = QtWidgets.QErrorMessage()

        self.mess_to = ""

        self.error = QtWidgets.QErrorMessage()
        self.setAutoFillBackground(True)
        self.timer = QtCore.QTimer()

        self.setWindowTitle("ChattApp (user logged in: " + self.user + ")")

        self.container = QtWidgets.QHBoxLayout()  # main Box
        self.chatlay = QtWidgets.QVBoxLayout()  # left Box
        self.rightlay = QtWidgets.QVBoxLayout()  # right Box

        self.to = QtWidgets.QLabel("Conversation with: ")
        self.chat = QtWidgets.QTextEdit()  # show messages
        self.chat.setReadOnly(True)
        self.type_field = QtWidgets.QTextEdit("Hello input")  # here type message
        self.type_field.lineWrapMode()

        self.user_label = QtWidgets.QLabel("Active users:")
        self.users_list = QtWidgets.QListWidget()
        self.user_logoutbutt = QtWidgets.QPushButton("Log out")
        self.sendbutt = QtWidgets.QPushButton("Send")
        self.buttlay = QtWidgets.QHBoxLayout()
        self.buttlay.addWidget(self.sendbutt)
        self.buttlay.addWidget(self.user_logoutbutt)

        # Adding 2 layouts
        self.container.addLayout(self.chatlay, 6)
        self.container.addLayout(self.rightlay, 2)

        # Adding Widgets to the chatlay
        self.chatlay.addWidget(self.to)
        self.chatlay.addWidget(self.chat, 11)
        self.chatlay.addWidget(self.type_field, 2)

        # Adding Widgets to the rightlay
        self.rightlay.addWidget(self.user_label)
        self.rightlay.addWidget(self.users_list)
        self.rightlay.addLayout(self.buttlay)

        # Setting layout
        self.setLayout(self.container)

        # Actions on click
        self.sendbutt.clicked.connect(self.send_mess)
        self.users_list.itemClicked.connect(self.change_adress)

        # Receiving messages
        self.timer.start(500)
        self.sock.readyRead.connect(self.message_recive)
        self.user_logoutbutt.clicked.connect(self.disconnection)

    def closeEvent(self, event):
        """
        Disconnect
        :param event: closing signal - "X" pressed
        """
        self.disconnection()

    def remove_client_from_list(self, x):
        """
        Remove a client from the list (widget)
        :param x: username
        """
        self.user_list.remove(x)
        self.users_list.clear()
        for index, i in enumerate(self.user_list):
            if i != self.user:
                self.users_list.insertItem(index, i)

    def change_adress(self, x):
        """
        Change adress of messages
        :param x: username
        :return:
        """
        self.to.setText("Conversation with: " + x.text())
        self.mess_to = x.text()

    def disconnection(self):
        """
        Closing client
        :return:
        """
        print("disconnection")
        self.sock.write(bytes("$disconnected$ " + self.user, 'utf8'))
        self.sock.waitForBytesWritten(1000)
        self.sock.close()
        self.close()

    def cleartype(self):
        """
        Clears typing field
        :return:
        """
        self.type_field.clear()

    def message_recive(self):
        """
        Recive message
        :return:
        """
        self.m = self.sock.read(4096)
        self.m = str(self.m, 'utf8')
        self.temp = self.m.split()
        if self.temp[0] == "$user$":
            for i in range(1, len(self.temp), 1):
                if self.temp[i] not in self.user_list and '$user$' not in self.temp[i]:
                    if self.temp[i] != self.user:
                        self.users_list.insertItem(1, self.temp[i])
                        self.user_list.append(self.temp[i])
        elif self.temp[0] == "$disconnecteduser$":
            self.remove_client_from_list(self.temp[1])
            if self.temp[1] == self.mess_to:
                self.mess_to = ''
        else:
            self.txt = self.chat.toPlainText()
            self.txt += "\n" + self.m
            self.chat.setPlainText(self.txt)

    def send_mess(self):
        """
        Send message
        :return: None
        """
        if self.mess_to:
            message = self.type_field.toPlainText()
            self.sock.write(bytes(self.mess_to + " " + message, 'utf8'))
            self.cleartype()
        else:
            self.error_mess.showMessage("Select one recipient.")


def main():
    """
    Main
    """
    if __name__ == '__main__':
        name = input("Your name: ")
        app = QtWidgets.QApplication([])
        win = ClientWin(name)
        win.resize(800, 600)
        win.show()
        sys.exit(app.exec_())


main()
