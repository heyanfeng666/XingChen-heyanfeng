import sys
import threading
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from main.Network import XingChenNetwork
from src.main.SignalManager import SignalManager
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot, Qt

from src.main.Widgets import ChatWindow

VERSION = "Test 3.0.0"


def CreateFolder():
    from src.untl.ControlFiles import CreateDirs, CheckDirs, CtrlFiles
    path = Path("./config").parent / "src" / "config"
    if CheckDirs(str(path.resolve())):
        CreateDirs(str(path.resolve()))
        if CtrlFiles.CheckFiles(CtrlFiles("XingChenConfig.ini", str(path / "XingChenConfig.ini"), "w"),
                                str(path / "XingChenConfig.ini")):
            file = CtrlFiles("XingChenConfig.ini", str(path / "XingChenConfig.ini"), "w")


if __name__ == "__main__":
    CreateFolder()
    app = QApplication(sys.argv)

    manager = SignalManager()

    network = XingChenNetwork()

    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    window = ChatWindow()
    window.show()

    manager.StartXingChenSignal.emit()
    app.exec_()