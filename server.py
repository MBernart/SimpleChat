"""Chat server"""

from PyQt5 import QtCore, QtNetwork, QtWidgets
import sys


class server(QtWidgets.QWidget):
    """Server"""

    def __init__(self):
        """Initialize"""
        super().__init__()
        self.client_list = []
        self.client_list_names = [" $user$"]
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

    def on_disconnected_client(self, name, index):
        """
        Client disconnection
        :param name: Username
        :param index: Index of client in the list
        :return:
        """
        print("disconnected: " + name)
        self.client_list_names.remove(name)
        print(self.client_list_names)
        self.client_list.pop(index)
        for j in self.client_list:
            j[2].write(bytes("$disconnecteduser$ " + name, 'utf8'))

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
        print(self.client_list)
        self.client_list_update()

    def client_list_update(self):
        """
        Adding new client
        :return: None
        """
        for j in self.client_list:
            j[2].write(bytes(" ".join(self.client_list_names), "utf8"))

    def transfer_data(self):
        """
        Recive data
        :return: None
        """
        for index, i in enumerate(self.client_list):
        #try:
            self.mess = str(i[2].read(4096), 'utf8')
            if self.mess:
                if self.mess.split()[0] == '$disconnected$':
                    self.on_disconnected_client(i[0], index)
                    print(self.client_list)
                elif self.mess != "":
                    self.mess = self.mess.split()
                    self.mess_to = self.mess.pop(0)
                    print("To: " + self.mess_to)
                    self.mess = i[0] + ": " + " ".join(self.mess)
                    print(self.mess)
                    for j in self.client_list:
                        if j[0] == self.mess_to or j[0] == i[0]:
                            j[2].write(bytes(self.mess, "utf8"))
        #except:
            pass


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ser = server()
    sys.exit(app.exec_())
