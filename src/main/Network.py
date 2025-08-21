import configparser

from PyQt5.QtNetwork import QAbstractSocket

from src.untl.ControlNetwork import CtrlNetwork

from datetime import datetime
import time
import threading

host = "127.0.0.1"
port = 55030


class XingChenNetwork:
    def __init__(self):
        self.server = CtrlNetwork()
        self.server.Connect(host, port)

    def Send(self, data):
        if self.server.socket.state() == QAbstractSocket.ConnectedState:
            self.server.SendData(data)
            print(f"成功发送消息{data}给{self.server.socket.peerAddress().toString()}:{self.server.socket.peerPort()}")
        elif (self.server.socket.state() == QAbstractSocket.UnconnectedState
              or self.server.socket.state() == QAbstractSocket.HostLookupState
              or self.server.socket.state() == QAbstractSocket.ConnectingState
              or self.server.socket.state() == QAbstractSocket.ClosingState
              or self.server.socket.state() == QAbstractSocket.BoundState):
            raise SocketNoHaveConnectedError()


class SocketNoHaveConnectedError(Exception):
    def __init__(self):
        super().__init__("Socket has not connected")
