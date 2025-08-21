import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
                             QApplication, QLabel, QScrollArea)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    MSFluentWindow, NavigationInterface, NavigationItemPosition,
    FluentIcon as FIF, PushButton, LineEdit, TextEdit, Theme, setTheme
)
import darkdetect


class ChatWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        # 启用云母效果（Windows 11）
        self.setMicaEffectEnabled(True)

        # 初始化UI
        self.initFont()
        self.initUI()
        self.initNavigation()
        self.initAnimation()

        # 设置窗口属性
        self.setWindowTitle("Fluent 聊天")
        self.resize(1100, 750)  # 初始大小
        self.setMinimumSize(800, 600)  # 最小尺寸限制
        self.centerWindow()

    def initFont(self):
        """初始化全局字体，解决字体过小问题"""
        font = QFont()
        font.setFamily("Segoe UI")  # Fluent设计推荐字体
        font.setPointSize(10)  # 基础字体大小

        # 为应用设置全局字体
        QApplication.instance().setFont(font)

        # 高DPI适配
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

    def initUI(self):
        """初始化界面布局"""
        # 使用框架内置的stackedWidget作为会话容器
        self.stackedWidget.setMinimumSize(600, 500)

        # 调整导航栏样式 - 兼容不同版本
        if hasattr(self.navigationInterface, 'setWidth'):
            # 如果是NavigationInterface，直接设置宽度
            self.navigationInterface.setWidth(220)
        else:
            # 如果是NavigationBar，通过布局约束宽度
            self.hBoxLayout.setStretch(0, 0)  # 导航栏不拉伸
            self.hBoxLayout.setStretch(1, 1)  # 内容区域拉伸

        # 设置导航栏边框（如果支持）
        if hasattr(self.navigationInterface, 'setBorderVisible'):
            self.navigationInterface.setBorderVisible(True)

    def initNavigation(self):
        """初始化导航栏会话列表"""
        # 添加会话
        self.addChatSession("张三", FIF.PEOPLE, "在线")
        self.addChatSession("李四", FIF.PEOPLE, "离线")
        self.addChatSession("PyQt学习群", FIF.PEOPLE, "128人在线")

        # 底部添加设置按钮
        self.navigationInterface.addItem(
            routeKey="settings",
            icon=FIF.SETTING,
            text="设置",
            position=NavigationItemPosition.BOTTOM
        )

    def initAnimation(self):
        """初始化切换动画"""
        # 为stackedWidget添加淡入淡出动画
        self.animation = QPropertyAnimation(self.stackedWidget, b"opacity")
        self.animation.setDuration(300)  # 动画持续时间
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)  # 缓动曲线
        self.stackedWidget.setWindowOpacity(1.0)

    def addChatSession(self, name, icon, status):
        """添加聊天会话"""
        session = ChatSessionWidget(name, status, self)
        session.setObjectName(name)
        self.stackedWidget.addWidget(session)

        # 添加导航项，绑定切换事件
        self.navigationInterface.addItem(
            routeKey=name,
            icon=icon,
            text=name,
            onClick=lambda: self.switchSession(session)
        )

    def switchSession(self, session):
        """切换会话，带动画效果"""
        # 开始淡出动画
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()

        # 动画结束后切换会话并淡入
        def onAnimationFinished():
            self.stackedWidget.setCurrentWidget(session)
            self.animation.setStartValue(0.0)
            self.animation.setEndValue(1.0)
            self.animation.start()

        self.animation.finished.connect(onAnimationFinished)

    def centerWindow(self):
        """窗口居中显示"""
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class ChatSessionWidget(QWidget):
    def __init__(self, username, status, parent=None):
        super().__init__(parent)
        self.username = username
        self.status = status
        self.initLayout()
        self.initStyle()

    def initLayout(self):
        """初始化会话布局"""
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(15, 15, 15, 15)
        self.mainLayout.setSpacing(10)

        # 顶部标题栏
        self.initTitleBar()

        # 消息显示区域
        self.initChatDisplay()

        # 输入区域
        self.initInputArea()

    def initTitleBar(self):
        """初始化会话标题栏"""
        titleLayout = QHBoxLayout()

        # 用户名和状态
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

        # 标题栏右侧按钮
        self.moreBtn = PushButton("", self, icon=FIF.MORE)
        self.moreBtn.setIconSize(QSize(18, 18))
        self.moreBtn.setMinimumSize(36, 36)

        titleLayout.addWidget(userInfo)
        titleLayout.addStretch(1)
        titleLayout.addWidget(self.moreBtn)

        self.mainLayout.addLayout(titleLayout)

    def initChatDisplay(self):
        """初始化聊天显示区域"""
        # 滚动区域包装聊天内容
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 6px;
                margin: 5px 0;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(150, 150, 150, 0.5);
                border-radius: 3px;
            }
        """)

        # 聊天内容容器
        self.chatContainer = QWidget()
        self.chatLayout = QVBoxLayout(self.chatContainer)
        self.chatLayout.setContentsMargins(0, 0, 0, 0)
        self.chatLayout.setSpacing(15)
        self.chatLayout.addStretch(1)  # 推消息到顶部

        self.scrollArea.setWidget(self.chatContainer)
        self.mainLayout.addWidget(self.scrollArea, 1)  # 占主要空间

    def initInputArea(self):
        """初始化输入区域"""
        inputContainer = QWidget()
        inputLayout = QVBoxLayout(inputContainer)
        inputLayout.setContentsMargins(0, 0, 0, 0)
        inputLayout.setSpacing(10)

        # 工具栏（表情、附件等）
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

        # 输入框和发送按钮
        editLayout = QHBoxLayout()
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

        self.sendBtn = PushButton("发送", self)
        self.sendBtn.setMinimumHeight(60)
        self.sendBtn.setMinimumWidth(80)
        self.sendBtn.clicked.connect(self.sendMsg)

        editLayout.addWidget(self.inputEdit, 1)
        editLayout.addWidget(self.sendBtn)

        inputLayout.addLayout(editLayout)
        self.mainLayout.addWidget(inputContainer)

    def initStyle(self):
        """初始化样式"""
        # 设置背景色（根据主题自适应）
        if not darkdetect.isDark():
            self.setStyleSheet("background-color: #1e1e1e;")
        else:
            self.setStyleSheet("background-color: #f5f5f5;")

    def sendMsg(self):
        """发送消息"""
        msg = self.inputEdit.toPlainText().strip()
        if msg:
            self.addMessage("我", msg, is_self=True)
            self.inputEdit.clear()

            # 模拟回复
            if self.username == "张三":
                import random
                replies = ["好的，我知道了", "没问题，稍后回复你", "这个想法不错！", "我正在处理，稍等"]
                self.addMessage("张三", random.choice(replies), is_self=False)

    def addMessage(self, sender, content, is_self):
        """添加消息到聊天区域"""
        msgWidget = QWidget()
        layout = QHBoxLayout(msgWidget)

        # 根据是否自己发送的消息调整对齐方式
        if is_self:
            layout.setAlignment(Qt.AlignRight)
            bg_color = "#0078d4"  # 自己消息的背景色（Fluent蓝）
            text_color = "white"
        else:
            layout.setAlignment(Qt.AlignLeft)
            # 根据主题设置对方消息背景色
            bg_color = "#eaeaea" if not Theme.isDarkTheme() else "#333333"
            text_color = "black" if not Theme.isDarkTheme() else "white"

        # 消息气泡
        bubble = QLabel(content)
        bubble.setWordWrap(True)  # 自动换行
        bubble.setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            border-radius: 12px;
            padding: 10px 15px;
            max-width: 60%;  # 限制最大宽度
            font-size: 14px;
        """)

        # 设置字体
        font = bubble.font()
        font.setPointSize(11)
        bubble.setFont(font)

        layout.addWidget(bubble)
        self.chatLayout.insertWidget(self.chatLayout.count() - 1, msgWidget)

        # 滚动到底部
        self.scrollArea.verticalScrollBar().setValue(
            self.scrollArea.verticalScrollBar().maximum()
        )