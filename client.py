"""Chat client"""
from PyQt5 import QtWidgets, QtNetwork, QtCore
import sys
import json


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
        self.type_field = QtWidgets.QTextEdit(
            "Hello input")  # here type message
        self.type_field.lineWrapMode()
        self.type_field.installEventFilter(self)

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

    def eventFilter(self, obj, event):
        """
        Send message when Enter is pressed
        :param obj: object to change typical event
        :param event: pressed button
        """
        if obj is self.type_field and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
                self.send_mess()
        return super().eventFilter(obj, event)

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
        self.disconnection_message = json.dumps(
            {'type': "user_disconnected", 'value': self.user})
        self.sock.write(bytes(self.disconnection_message, 'utf8'))
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
        self.m = str(self.sock.read(4096), 'utf8')
        self.m = json.loads(self.m)
        self.xtype = self.m['type']
        if self.xtype == 'newuseradded':
            for i in self.m['value']:
                if i not in self.user_list:
                    if i != self.user:
                        self.users_list.insertItem(1, i)
                        self.user_list.append(i)
        elif self.xtype == 'userdisconnected':
            self.remove_client_from_list(self.m['value'])
            if self.m['value'] == self.mess_to:
                self.mess_to = ''
        elif self.xtype == 'IMessage':
            self.txt = self.chat.toPlainText()
            self.txt += "\n" + self.m['value']
            self.chat.setPlainText(self.txt)

    def send_mess(self):
        """
        Send message
        :return: None
        """
        if self.mess_to:
            self.message = self.type_field.toPlainText()
            self.message = json.dumps({'type': 'IMessage', 'value': {'from': self.user, 'to': self.mess_to,
                                                                     'message': self.message}})
            self.sock.write(bytes(self.message, 'utf8'))
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
