import sys
import time
import traceback
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                             QApplication, QLabel, QScrollArea, QMessageBox, QSizePolicy, QTextEdit)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, QThread, pyqtSignal, QEvent, QTimer
from PyQt5.QtGui import QFont, QFontMetrics, QTextOption
from qfluentwidgets import (
    MSFluentWindow, NavigationInterface, NavigationItemPosition,
    FluentIcon as FIF, PushButton, TextEdit, Theme, setTheme
)
import darkdetect


class AutoWidthTextEdit(QTextEdit):
    """自定义文本编辑框，能够根据内容自动调整宽度"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setWordWrapMode(QTextOption.WordWrap)
        self.setMinimumHeight(40)
        self.setMaximumHeight(1000)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        # 添加最小宽度限制，避免过窄
        self.min_width = 80  # 适合短消息的最小宽度

    def setTextAndAdjustWidth(self, text, max_width):
        """设置文本并根据内容调整宽度"""
        self.setPlainText(text)

        # 使用与显示相同的字体计算宽度
        font = self.font()
        font_metrics = QFontMetrics(font)

        # 计算文本宽度
        lines = text.split('\n')
        max_line_width = 0

        for line in lines:
            # 计算单行文本宽度，如果超过最大宽度则按最大宽度计算
            line_width = font_metrics.width(line)
            max_line_width = max(max_line_width, line_width)

        # 加上内边距
        desired_width = max_line_width + 30  # 左右内边距各15px

        # 确保不小于最小宽度，不大于最大宽度
        final_width = max(self.min_width, min(desired_width, max_width))

        self.setFixedWidth(final_width)
        self.updateGeometry()


class NetworkThread(QThread):
    """网络处理线程，避免UI卡顿"""
    new_message = pyqtSignal(str, str)
    send_complete = pyqtSignal(bool, str)  # 发送完成信号(是否成功, 消息)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.parent = parent
        self.queue = []  # 消息队列

    def run(self):
        """网络消息监听循环"""
        try:
            while self.running:
                # 处理消息队列
                while self.queue:
                    target, message = self.queue.pop(0)
                    try:
                        # 模拟网络发送延迟
                        time.sleep(0.5)
                        print(f"[网络发送提醒] 向 {target} 发送: {message}")
                        self.send_complete.emit(True, message)

                        # 模拟张三的回复
                        if target == "张三":
                            import random
                            time.sleep(0.3)  # 模拟网络延迟
                            replies = ["好的", "收到", "嗯", "好", "可以",
                                       "这是一条比较长的回复消息，用来测试消息气泡的自动宽度调整功能，看看多行文本的显示效果如何"]
                            self.new_message.emit(target, random.choice(replies))
                    except Exception as e:
                        self.send_complete.emit(False, f"发送失败: {str(e)}")

                # 休眠一小段时间，减少CPU占用
                time.sleep(0.1)
        except Exception as e:
            print(f"网络线程错误: {str(e)}")

    def send(self, target, message):
        """将消息加入队列，由网络线程处理"""
        self.queue.append((target, message))


class ChatWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.setMicaEffectEnabled(True)

        # 网络线程初始化
        self.network_thread = NetworkThread(self)
        self.network_thread.new_message.connect(self.on_network_message)
        self.network_thread.start()

        # 切换控制变量
        self.is_switching = False
        self.target_session = None  # 记录目标会话

        # UI初始化
        self.initFont()
        self.initUI()
        self.initNavigation()
        self.initAnimation()

        # 窗口设置
        self.setWindowTitle("Fluent 聊天")
        self.resize(1300, 900)
        self.setMinimumSize(1000, 700)
        self.centerWindow()

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
        self.addChatSession("张三", FIF.PEOPLE, "在线")
        self.addChatSession("李四", FIF.PEOPLE, "离线")
        self.addChatSession("PyQt学习群", FIF.PEOPLE, "128人在线")

        self.navigationInterface.addItem(
            routeKey="settings",
            icon=FIF.SETTING,
            text="设置",
            position=NavigationItemPosition.BOTTOM
        )

    def initAnimation(self):
        # 创建两个动画，避免冲突
        self.fadeOutAnimation = QPropertyAnimation(self.stackedWidget, b"opacity")
        self.fadeOutAnimation.setDuration(200)
        self.fadeOutAnimation.setEasingCurve(QEasingCurve.InOutQuad)

        self.fadeInAnimation = QPropertyAnimation(self.stackedWidget, b"opacity")
        self.fadeInAnimation.setDuration(200)
        self.fadeInAnimation.setEasingCurve(QEasingCurve.InOutQuad)

        # 连接淡入动画完成信号
        self.fadeInAnimation.finished.connect(self.on_switch_complete)

    def addChatSession(self, name, icon, status):
        session = ChatSessionWidget(name, status, self, self.network_thread)
        session.setObjectName(name)
        self.stackedWidget.addWidget(session)

        self.navigationInterface.addItem(
            routeKey=name,
            icon=icon,
            text=name,
            onClick=lambda: self.switchSession(session)
        )

    def switchSession(self, session):
        """改进的会话切换逻辑，防止快速点击导致的反复横跳"""
        # 如果是当前会话，不处理
        if self.stackedWidget.currentWidget() == session:
            return

        # 如果正在切换中，更新目标会话并返回
        if self.is_switching:
            self.target_session = session
            return

        # 开始切换流程
        self.is_switching = True
        self.target_session = session

        # 停止所有可能运行的动画
        self.fadeOutAnimation.stop()
        self.fadeInAnimation.stop()

        # 开始淡出动画
        self.fadeOutAnimation.setStartValue(1.0)
        self.fadeOutAnimation.setEndValue(0.0)
        self.fadeOutAnimation.start()

        # 连接淡出完成信号到切换处理
        try:
            self.fadeOutAnimation.finished.disconnect(self.process_switch)
        except:
            pass
        self.fadeOutAnimation.finished.connect(self.process_switch)

    def process_switch(self):
        """处理实际的会话切换"""
        if self.target_session:
            self.stackedWidget.setCurrentWidget(self.target_session)

            # 开始淡入动画
            self.fadeInAnimation.setStartValue(0.0)
            self.fadeInAnimation.setEndValue(1.0)
            self.fadeInAnimation.start()

    def on_switch_complete(self):
        """切换完成后的处理"""
        # 检查是否有新的目标会话等待切换
        current = self.stackedWidget.currentWidget()
        if self.target_session and self.target_session != current:
            # 立即切换到新目标，不播放动画
            self.stackedWidget.setCurrentWidget(self.target_session)
            self.stackedWidget.setWindowOpacity(1.0)
        else:
            self.stackedWidget.setWindowOpacity(1.0)

        # 重置切换状态
        self.is_switching = False
        self.target_session = None

    def on_network_message(self, sender, content):
        try:
            for i in range(self.stackedWidget.count()):
                widget = self.stackedWidget.widget(i)
                if isinstance(widget, ChatSessionWidget) and widget.username == sender:
                    widget.addMessage(sender, content, is_self=False)
                    return

            current = self.stackedWidget.currentWidget()
            if isinstance(current, ChatSessionWidget):
                current.addMessage("系统", f"收到来自 {sender} 的消息: {content}", is_self=False)
        except Exception as e:
            print(f"处理网络消息错误: {str(e)}")
            traceback.print_exc()

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        self.network_thread.running = False
        self.network_thread.wait()
        event.accept()


class ChatSessionWidget(QWidget):
    def __init__(self, username, status, parent=None, network_thread=None):
        super().__init__(parent)
        self.username = username
        self.status = status
        self.network_thread = network_thread

        # 连接网络线程的发送完成信号
        if self.network_thread:
            self.network_thread.send_complete.connect(self.on_send_complete)

        self.initLayout()
        self.initStyle()

        # 计算最大气泡宽度（占聊天区域的60%）
        self.max_bubble_width_ratio = 0.6
        self.max_bubble_width = 0

    def initLayout(self):
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(15, 15, 15, 15)
        self.mainLayout.setSpacing(10)

        self.initTitleBar()
        self.initChatDisplay()
        self.initInputArea()

    def initTitleBar(self):
        titleLayout = QHBoxLayout()

        userInfo = QWidget()
        userLayout = QVBoxLayout(userInfo)
        userLayout.setContentsMargins(0, 0, 0, 0)

        self.nameLabel = QLabel(self.username)
        nameFont = self.nameLabel.font()
        nameFont.setPointSize(12)
        nameFont.setBold(True)
        self.nameLabel.setFont(nameFont)

        self.statusLabel = QLabel(self.status)
        statusFont = self.statusLabel.font()
        statusFont.setPointSize(9)
        self.statusLabel.setFont(statusFont)
        self.statusLabel.setStyleSheet("color: #6e6e6e;")

        userLayout.addWidget(self.nameLabel)
        userLayout.addWidget(self.statusLabel)

        self.moreBtn = PushButton("", self, icon=FIF.MORE)
        self.moreBtn.setIconSize(QSize(18, 18))
        self.moreBtn.setMinimumSize(36, 36)

        titleLayout.addWidget(userInfo)
        titleLayout.addStretch(1)
        titleLayout.addWidget(self.moreBtn)

        self.mainLayout.addLayout(titleLayout)

    def initChatDisplay(self):
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { width: 6px; margin: 5px 0; }
            QScrollBar::handle:vertical {
                background-color: rgba(150, 150, 150, 0.5);
                border-radius: 3px;
            }
        """)

        self.chatContainer = QWidget()
        self.chatLayout = QVBoxLayout(self.chatContainer)
        self.chatLayout.setContentsMargins(0, 0, 0, 0)
        self.chatLayout.setSpacing(15)
        self.chatLayout.addStretch(1)

        self.scrollArea.setWidget(self.chatContainer)
        self.mainLayout.addWidget(self.scrollArea, 1)

        # 监听窗口大小变化，动态调整最大气泡宽度
        self.scrollArea.resizeEvent = self.on_scrollarea_resize

        # 初始化时触发一次大小计算
        QTimer.singleShot(100, self.on_scrollarea_resize)

    def on_scrollarea_resize(self, event=None):
        """滚动区域大小变化时，重新计算最大气泡宽度"""
        if self.scrollArea.width() > 0:
            self.max_bubble_width = int(self.scrollArea.width() * self.max_bubble_width_ratio)
        # 如果有事件参数，调用父类处理
        if event:
            super(QScrollArea, self.scrollArea).resizeEvent(event)

    def initInputArea(self):
        inputContainer = QWidget()
        inputLayout = QVBoxLayout(inputContainer)
        inputLayout.setContentsMargins(0, 0, 0, 0)
        inputLayout.setSpacing(10)

        toolLayout = QHBoxLayout()
        self.emojiBtn = PushButton("", self, icon=FIF.CLOUD)
        self.attachmentBtn = PushButton("", self, icon=FIF.PEOPLE)
        self.imageBtn = PushButton("", self, icon=FIF.PHOTO)

        for btn in [self.emojiBtn, self.attachmentBtn, self.imageBtn]:
            btn.setIconSize(QSize(20, 20))
            btn.setMinimumSize(36, 36)
            toolLayout.addWidget(btn)

        toolLayout.addStretch(1)
        inputLayout.addLayout(toolLayout)

        editLayout = QHBoxLayout()
        # 输入框使用qfluentwidgets的TextEdit
        self.inputEdit = TextEdit(self)
        self.inputEdit.setMinimumHeight(60)
        self.inputEdit.setPlaceholderText("输入消息...")
        self.inputEdit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """)

        self.inputEdit.installEventFilter(self)

        self.sendBtn = PushButton("发送", self)
        self.sendBtn.setMinimumHeight(60)
        self.sendBtn.setMinimumWidth(80)
        self.sendBtn.clicked.connect(self.sendMsg)

        editLayout.addWidget(self.inputEdit, 1)
        editLayout.addWidget(self.sendBtn)

        inputLayout.addLayout(editLayout)
        self.mainLayout.addWidget(inputContainer)

    def eventFilter(self, obj, event):
        try:
            if obj == self.inputEdit and event.type() == QEvent.KeyPress:
                key_event = event
                if key_event.key() == Qt.Key_Return and not key_event.modifiers() & Qt.ShiftModifier:
                    self.sendMsg()
                    return True
        except Exception as e:
            print(f"事件过滤错误: {str(e)}")
        return super().eventFilter(obj, event)

    def initStyle(self):
        if not darkdetect.isDark():
            self.setStyleSheet("background-color: #1e1e1e;")
        else:
            self.setStyleSheet("background-color: #f5f5f5;")

    def sendMsg(self):
        """发送消息，使用队列和信号避免阻塞"""
        try:
            msg = self.inputEdit.toPlainText().strip()
            if not msg:
                return

            # 先在本地显示消息
            self.addMessage("我", msg, is_self=True)
            self.inputEdit.clear()

            # 禁用发送按钮防止重复发送
            self.sendBtn.setEnabled(False)

            if self.network_thread:
                # 使用网络线程发送，不阻塞UI
                self.network_thread.send(self.username, msg)
                # 延迟启用发送按钮，防止快速连续发送
                QTimer.singleShot(1000, lambda: self.sendBtn.setEnabled(True))
            else:
                # 如果没有网络线程，直接启用按钮
                self.sendBtn.setEnabled(True)
        except Exception as e:
            print(f"发送消息错误: {str(e)}")
            traceback.print_exc()
            # 发生错误时确保按钮状态正确
            self.sendBtn.setEnabled(True)

    def on_send_complete(self, success, message):
        """处理发送完成的回调"""
        if not success:
            self.addMessage("系统", message, is_self=False)

        # 确保发送按钮状态正确
        if self.sendBtn.isEnabled() is False:
            self.sendBtn.setEnabled(True)

    def addMessage(self, sender, content, is_self):
        try:
            # 确保已计算最大宽度
            if self.max_bubble_width == 0:
                self.on_scrollarea_resize()

            msgWidget = QWidget()
            layout = QHBoxLayout(msgWidget)
            layout.setContentsMargins(0, 0, 0, 0)

            if is_self:
                layout.setAlignment(Qt.AlignRight)
                bg_color = "#0078d4"
                text_color = "white"
            else:
                layout.setAlignment(Qt.AlignLeft)
                if darkdetect.isDark():
                    bg_color = "#333333"
                    text_color = "white"
                else:
                    bg_color = "#eaeaea"
                    text_color = "black"

            # 使用自定义的自动调整宽度文本框
            bubble = AutoWidthTextEdit(self.chatContainer)
            bubble.setTextAndAdjustWidth(content, self.max_bubble_width)

            # 设置样式
            bubble.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {bg_color};
                    color: {text_color};
                    border-radius: 12px;
                    padding: 10px 15px;
                    font-size: 14px;
                    border: none;
                }}
                QTextEdit::contentsMargins {{ margin: 0; padding: 0; }}
            """)

            # 设置字体
            font = bubble.font()
            font.setFamily("Segoe UI")
            font.setPointSize(11)
            bubble.setFont(font)

            layout.addWidget(bubble)
            self.chatLayout.insertWidget(self.chatLayout.count() - 1, msgWidget)

            # 确保布局更新
            self.chatContainer.updateGeometry()
            self.chatLayout.update()

            # 滚动到底部
            QTimer.singleShot(10, lambda: self.scrollArea.verticalScrollBar().setValue(
                self.scrollArea.verticalScrollBar().maximum()
            ))
        except Exception as e:
            print(f"添加消息错误: {str(e)}")
            traceback.print_exc()


if __name__ == "__main__":
    # 捕获全局异常，防止程序意外退出
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        print(f"全局异常: {exc_type} {exc_value}")
        traceback.print_tb(exc_traceback)
        QMessageBox.critical(None, "程序错误", f"发生错误:\n{str(exc_value)}")


    sys.excepthook = handle_exception

    app = QApplication(sys.argv)
    setTheme(Theme.DARK if darkdetect.isDark() else Theme.LIGHT)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
