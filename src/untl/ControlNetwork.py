import threading
import time

from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtCore import QThread, pyqtSignal
from src.main.SignalManager import SignalManager


class CtrlNetwork:
    def __init__(self):
        self.ip = None
        self.port = None
        self.socket = QTcpSocket()

        self.socket.readyRead.connect(self.OnReadyRead)
        self.socket.connected.connect(self.OnConnected)
        self.socket.error.connect(self.OnError)

    def OnConnected(self):
        print(f"Connected to {self.ip}:{self.port}")
        self.socket.setSocketOption(QAbstractSocket.KeepAliveOption, 1)
        self.StartCheck()

    def Connect(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket.connectToHost(self.ip, self.port)

    def OnReadyRead(self):
        from src import StartXingChen
        data = self.socket.readAll().data().decode("utf-8")
        data = data.split(' ', 1)
        if data[0] == "message":
            SignalManager.MessageReceivedSignal.emit(data[1], data[2])
        elif data[0] == "XingChen Server":
            if data[2] == StartXingChen.VERSION:
                print("成功连接服务器")
                self.SendData("Xing Chen Client " + StartXingChen.VERSION)
            else:
                print("服务器版本不匹配")

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
            self.socket.write(data.encode("utf-8"))
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
