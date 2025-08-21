from PyQt5.QtCore import QObject, pyqtSignal


class SignalManager(QObject):
    StartXingChenSignal = pyqtSignal()
    StopXingChenSignal = pyqtSignal()

    def StartXingChen(self):
        self.StartXingChenSignal.emit()

    def StopXingChen(self):
        self.StopXingChenSignal.emit()
