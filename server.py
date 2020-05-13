"""Chat server"""

from PyQt5 import QtCore, QtNetwork, QtWidgets
import sys
import json


class server(QtWidgets.QWidget):
    """Server"""

    def __init__(self):
        """Initialize"""
        super().__init__()
        self.client_list = []
        self.client_list_names = []
        self.server = QtNetwork.QTcpServer()
        self.timer = QtCore.QTimer()
        self.timer.start(50)
        self.server.setObjectName("ChatServer")
        self.sock = QtNetwork.QTcpSocket(self.server)
        # if self.server.listen(QtNetwork.QHostAddress("X.X.X.X"), 6666):
        if self.server.listen(QtNetwork.QHostAddress.LocalHost, 6666):
            print(f"Connected: {self.server.objectName()}\nAdress: {self.server.serverAddress().toString()}\n"
                  f"Port {str(self.server.serverPort())}")
        else:
            print("Error!!!")
        self.server.newConnection.connect(self.new_client)
        self.timer.timeout.connect(self.transfer_data)

    def on_disconnected_client(self, name):
        """
        Client disconnection
        :param name: Username
        :return:
        """
        print("disconnected: " + name)
        self.client_list_names.remove(name)
        print(self.client_list_names)
        for index, i in enumerate(self.client_list):
            if i[0] == name:
                self.client_list.pop(index)
        self.disconnected_message = json.dumps({'type': "userdisconnected", 'value': name})
        for j in self.client_list:
            j[2].write(bytes(self.disconnected_message, 'utf8'))

    def new_client(self):
        """
        Add new client
        """
        print("New Client is connected")
        self.clientconn = self.server.nextPendingConnection()
        self.address = str(self.clientconn.peerAddress().toString())
        self.clientconn.waitForReadyRead()
        self.name = str(self.clientconn.read(4096), 'utf8')
        self.client_list.append((self.name, self.address, self.clientconn))
        self.client_list_names.append(self.name)
        print(self.client_list_names)
        self.client_list_update()

    def client_list_update(self):
        """
        Adding new client
        :return: None
        """
        self.new_client_message = json.dumps({'type': 'newuseradded', 'value': self.client_list_names})
        for j in self.client_list:
            j[2].write(bytes(self.new_client_message, "utf8"))

    def transfer_data(self):
        """
        Recive data
        :return: None
        """
        for i in self.client_list:
            # try:
            self.mess = str(i[2].read(4096), 'utf8')
            if self.mess:
                self.xmess = json.loads(self.mess)
                self.xtype = self.xmess['type']
                if self.xtype == 'user_disconnected':
                    self.on_disconnected_client(self.xmess['value'])
                    print(self.client_list)
                elif self.xtype == 'IMessage':
                    self.mess_to = self.xmess['value']['to']
                    print("To: " + self.mess_to)
                    if self.xmess['value']['from']:
                        self.mess = json.dumps({'type': 'IMessage', 'value': self.xmess['value']['from'] + ": " + " ".join(
                            self.xmess['value']['message'])})
                        print(self.xmess['value']['from'] + ": " + self.xmess['value']['message'])
                        for j in self.client_list:
                            if j[0] == self.mess_to or j[0] == self.xmess['value']['from']:
                                j[2].write(bytes(self.mess, "utf8"))
            # except:
            pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ser = server()
    sys.exit(app.exec_())
