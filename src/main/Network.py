import configparser

from PyQt5.QtNetwork import QAbstractSocket

from src.untl.ControlNetwork import CtrlNetwork
from src.main.SignalManager import SignalManager

from datetime import datetime
import time
import threading

host = "127.0.0.1"
port = 55030


class XingChenNetwork:
    def __init__(self):
        self.server = CtrlNetwork()
        self.server.Connect(host, port)


    def SendMessage(self, goal: str, context: str):
        self.server.SendData(f"send_message {goal} {context}")
        SignalManager.SendMessageSignal.connect(self.SendMessage)


class SocketNoHaveConnectedError(Exception):
    def __init__(self):
        super().__init__("Socket has not connected")
