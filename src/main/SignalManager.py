from PyQt5.QtCore import QObject, pyqtSignal


class SignalManager(QObject):
    StartXingChenSignal = pyqtSignal()
    StopXingChenSignal = pyqtSignal()

    SendMessageSignal = pyqtSignal(str, str)
    MessageReceivedSignal = pyqtSignal(str, str)
    SendCompleteSignal = pyqtSignal(bool, str)
    ConnectionChangedSignal = pyqtSignal(bool)

    CriticalMessageBox = pyqtSignal(str, str)
    WarningMessageBox = pyqtSignal(str, str)
    InformationMessageBox = pyqtSignal(str, str)

    ConnectedServer = pyqtSignal()

    NetworkStateChangedSignal = pyqtSignal(str)
