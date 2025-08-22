import sys
import traceback
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                             QApplication, QLabel, QScrollArea, QSizePolicy, QTextEdit,
                             QDesktopWidget)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QEvent, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QTextOption
from qfluentwidgets import (
    MSFluentWindow, NavigationInterface, NavigationItemPosition,
    FluentIcon as FIF, PushButton, TextEdit
)
import darkdetect


class BaseWindow(MSFluentWindow):
    """窗口基类，封装通用功能"""

    def __init__(self):
        super().__init__()
        self.setMicaEffectEnabled(True)
        self.is_switching = False
        self.target_session = None

        self.initFont()
        self.initUI()
        self.initNavigation()
        self.initAnimation()

    def initFont(self):
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        QApplication.instance().setFont(font)

        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

    def initUI(self):
        self.stackedWidget.setMinimumSize(800, 600)

        if hasattr(self.navigationInterface, 'setWidth'):
            self.navigationInterface.setWidth(280)
        else:
            self.hBoxLayout.setStretch(0, 1)
            self.hBoxLayout.setStretch(1, 4)

        if hasattr(self.navigationInterface, 'setBorderVisible'):
            self.navigationInterface.setBorderVisible(True)

    def initNavigation(self):
        """由子类实现具体导航项"""
        pass

    def initAnimation(self):
        self.fadeOutAnimation = QPropertyAnimation(self.stackedWidget, b"opacity")
        self.fadeOutAnimation.setDuration(200)
        self.fadeOutAnimation.setEasingCurve(QEasingCurve.InOutQuad)

        self.fadeInAnimation = QPropertyAnimation(self.stackedWidget, b"opacity")
        self.fadeInAnimation.setDuration(200)
        self.fadeInAnimation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fadeInAnimation.finished.connect(self.on_switch_complete)

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def switchSession(self, session):
        if self.stackedWidget.currentWidget() == session:
            return

        if self.is_switching:
            self.target_session = session
            return

        self.is_switching = True
        self.target_session = session

        self.fadeOutAnimation.stop()
        self.fadeInAnimation.stop()

        self.fadeOutAnimation.setStartValue(1.0)
        self.fadeOutAnimation.setEndValue(0.0)
        self.fadeOutAnimation.start()

        try:
            self.fadeOutAnimation.finished.disconnect(self.process_switch)
        except:
            pass
        self.fadeOutAnimation.finished.connect(self.process_switch)

    def process_switch(self):
        if self.target_session:
            self.stackedWidget.setCurrentWidget(self.target_session)
            self.fadeInAnimation.setStartValue(0.0)
            self.fadeInAnimation.setEndValue(1.0)
            self.fadeInAnimation.start()

    def on_switch_complete(self):
        current = self.stackedWidget.currentWidget()
        if self.target_session and self.target_session != current:
            self.stackedWidget.setCurrentWidget(self.target_session)
            self.stackedWidget.setWindowOpacity(1.0)
        else:
            self.stackedWidget.setWindowOpacity(1.0)

        self.is_switching = False
        self.target_session = None


class ChatWindow(BaseWindow):
    """聊天窗口类"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xing Chen")
        self.resize(1300, 900)
        self.setMinimumSize(1000, 700)
        self.centerWindow()

        # 创建聊天接口
        self.chat_interface = ChatInterface()

        # 初始化聊天会话
        self.initChatSessions()

        # 连接信号
        self.connect_signals()

    def initNavigation(self):
        self.addChatSession("张三", FIF.PEOPLE, "离线")
        self.addChatSession("李四", FIF.PEOPLE, "离线")
        self.addChatSession("PyQt学习群", FIF.PEOPLE, "离线")

        self.navigationInterface.addItem(
            routeKey="settings",
            icon=FIF.SETTING,
            text="设置",
            position=NavigationItemPosition.BOTTOM
        )

    def initChatSessions(self):
        """初始化聊天会话"""
        pass

    def connect_signals(self):
        """连接信号与槽"""
        self.chat_interface.MessageReceivedSignal.connect(self.on_message_received)
        self.chat_interface.SendCompleteSignal.connect(self.on_send_complete)
        self.chat_interface.ConnectionChangedSignal.connect(self.on_connection_changed)

    def on_message_received(self, sender, content):
        """处理接收到的消息"""
        pass

    def on_send_complete(self, success, message):
        """处理发送完成状态"""
        pass

    def on_connection_changed(self, connected):
        """处理连接状态变化"""
        pass


class initChatSessions(QObject):
    """聊天接口类，处理网络和UI通信"""

    def __init__(self):
        super().__init__()

    def connect_to_network(self, network):
        """连接网络模块"""
        network.message_received.connect(self.handle_message_received)
        network.connection_changed.connect(self.handle_connection_changed)
        self.SendMessageSignal.connect(network.send_message)

    def handle_message_received(self, sender, message):
        """处理接收到的消息"""
        self.MessageReceivedSignal.emit(sender, message)

    def handle_connection_changed(self, connected):
        """处理连接状态变化"""
        self.ConnectionChangedSignal.emit(connected)

    def on_send_complete(self, success, message):
        """处理发送完成"""
        self.SendCompleteSignal.emit(success, message)