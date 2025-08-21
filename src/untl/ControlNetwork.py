import threading
import time

from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtCore import QThread, pyqtSignal


class CtrlNetwork:
    def __init__(self):
        self.ip = None
        self.port = None
        self.socket = QTcpSocket()

        self.socket.readyRead.connect(self.OnReadyRead)
        self.socket.connected.connect(self.OnConnected)
        self.socket.error.connect(self.OnError)
        self.socket.stateChanged.connect(self.SocketStateChanged)

    def OnConnected(self):
        print(f"Connected to {self.ip}:{self.port}")
        self.socket.setSocketOption(QAbstractSocket.KeepAliveOption, 1)
        self.StartCheck()

    def Connect(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket.connectToHost(self.ip, self.port)

    def OnReadyRead(self):
        data = self.socket.readAll().data().decode("utf-8")
        print(data)

    def SocketStateChanged(self, socket_state: QAbstractSocket):
        if socket_state == QAbstractSocket.HostLookupState or socket_state == QAbstractSocket.ConnectingState:
            print("这里好没有写完！！！！！！！！！！")
            pass

    def StartCheck(self):
        self.checkNetworkThread = threading.Thread(target=self.CheckNetwork)
        self.checkNetworkThread.start()

    def CheckError(self):
        print("错误")

    def getSocketState(self):
        return self.socket.state()

    def OnError(self, socketerror):
        print(socketerror)

    def SendData(self, data):
        if self.socket.state() == QTcpSocket.ConnectedState:
            self.socket.write(data)
            self.socket.flush()

    def Disconnect(self):
        self.socket.disconnectFromHost()

    def CheckNetwork(self):
        while True:
            try:
                self.SendData(b"ping")
                time.sleep(5)
            except Exception as e:
                print(f"心跳线程异常: {e}")
                break
