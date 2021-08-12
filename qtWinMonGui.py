import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtWidgets import (
    QPushButton,
    QToolTip,
    QLabel,
    QLineEdit,
    QTextEdit,
    QTableView,
)
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QVBoxLayout,
    QGridLayout,
    QTabWidget,
    QTableWidget,
)

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import (
    QCoreApplication,
    QAbstractTableModel,
    QDate,
    QTime,
    QDateTime,
    Qt,
)


class LogHandlingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        my_array = [["00", "01", "02"], ["10", "11", "12"], ["20", "21", "22"]]
        # self.rows = []
        self.rows = my_array
        ## Center Table Widget
        self.tableWidget = QTableWidget()
        # self.tableWidget.setModel(self.model)
        self.tableWidget.setRowCount(15)
        self.tableWidget.setColumnCount(4)

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)
        # self.tableWidget.setEditTriggers(QAbstractItemView.AllEditTriggers)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.tableWidget = QTableWidget()
        # self.tableWidget.setModel(self.model)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # for i in range(20):
        #    for j in range(4):
        #        self.tableWidget.setItem(i, j, QTableWidgetItem(str(i+j)))

        ###################################################################
        # Top Grid
        self.topGrid = QGridLayout()

        ### Before Button
        beforeBtn = QPushButton("이전", self)
        beforeBtn.setToolTip("Before")
        beforeBtn.resize(beforeBtn.sizeHint())
        beforeBtn.clicked.connect(QCoreApplication.instance().quit)

        ## spacer
        spacerItem = QSpacerItem(146, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        ### page edit control
        pageEdit = QLineEdit()
        pageEdit.setReadOnly(True)

        ## spacer
        spacerItem2 = QSpacerItem(146, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        ### Next Button
        nextBtn = QPushButton("다음", self)
        nextBtn.setToolTip("Next")
        nextBtn.resize(nextBtn.sizeHint())
        nextBtn.clicked.connect(QCoreApplication.instance().quit)

        ### Close Button
        # closeBtn = QPushButton('닫기', self)
        # closeBtn.setToolTip('Close')
        # closeBtn.resize(closeBtn.sizeHint())
        # closeBtn.clicked.connect(QCoreApplication.instance().quit)

        ## Top Grid Layout
        self.topGrid.addWidget(beforeBtn, 0, 1)
        self.topGrid.addItem(spacerItem, 0, 2)
        self.topGrid.addWidget(pageEdit, 0, 3)
        self.topGrid.addItem(spacerItem2, 0, 4)
        self.topGrid.addWidget(nextBtn, 0, 5)
        # self.topGrid.addWidget(closeBtn, 0, 3)
        ###################################################################

        ###################################################################
        ## Bottom Grid
        self.bottomGrid = QGridLayout()

        ### Before Button
        beforeBtn2 = QPushButton("이전", self)
        beforeBtn2.setToolTip("Before")
        beforeBtn2.resize(beforeBtn2.sizeHint())
        beforeBtn2.clicked.connect(QCoreApplication.instance().quit)

        ## spacer
        spacerItem3 = QSpacerItem(146, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        ### page edit control
        pageEdit2 = QLineEdit()
        pageEdit2.setReadOnly(True)

        ## spacer
        spacerItem4 = QSpacerItem(146, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        ### Next Button
        nextBtn2 = QPushButton("다음", self)
        nextBtn2.setToolTip("Next")
        nextBtn2.resize(nextBtn2.sizeHint())
        nextBtn2.clicked.connect(QCoreApplication.instance().quit)

        ### Close Button
        # QToolTip.setFont(QFont('SansSerif', 10))
        # closeBtn2 = QPushButton('닫기', self)
        # closeBtn2.setToolTip('Close')
        # closeBtn2.resize(closeBtn2.sizeHint())
        # closeBtn2.clicked.connect(QCoreApplication.instance().quit)

        ## Bottom Grid Layout
        self.bottomGrid.addWidget(beforeBtn2, 0, 1)
        self.bottomGrid.addItem(spacerItem3, 0, 2)
        self.bottomGrid.addWidget(pageEdit2, 0, 3)
        self.bottomGrid.addItem(spacerItem4, 0, 4)
        self.bottomGrid.addWidget(nextBtn2, 0, 5)
        # self.bottomGrid.addWidget(closeBtn2, 0, 3)
        ###################################################################

        ## Layout Setting
        layout = QVBoxLayout()

        # layout.addWidget(self.header)
        layout.addLayout(self.topGrid)
        # layout.addWidget(self.tableWidget)
        layout.addWidget(self.tableWidget)
        layout.addLayout(self.bottomGrid)
        # layout.addLayout(self.bottomGrid)
        self.setLayout(layout)

        self.setWindowTitle("QTableWidget")
        # self.setGeometry(300, 100, 600, 400)
        # self.show()

        # 데이터 변경시 event emit을 해야함
        # Trigger refresh.
        #    self.model.layoutChanged.emit()


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 바닥 레이아웃부터 순서대로
        # tab1 = QWidget()
        tab1 = LogHandlingWindow()
        tab2 = QWidget()

        tabs = QTabWidget()
        tabs.addTab(tab1, "Log")
        tabs.addTab(tab2, "User")

        vbox = QVBoxLayout()
        vbox.addWidget(tabs)

        self.setLayout(vbox)

        # 라벨, 버튼

        # 최종 Window의 크기 조절 및 위치 조절
        self.setWindowTitle("My First Application")
        self.setGeometry(300, 300, 1024, 768)
        self.center()
        self.show()

        # 여긴 임시 테스트
        now = QDate.currentDate()
        # print(now.toString('d.M.yy'))                   # 12.8.21
        # print(now.toString('dd.MM.yyyy'))               # 12.08.2021
        # print(now.toString('yyyy.MM.dd'))               # 2021.12.08
        print(now.toString("yyyy.MM.dd(ddd)"))  # 2021.08.12(목)
        # print(now.toString('ddd.MMMM.yyyy'))            # 목.8월.2021
        # print(now.toString(Qt.ISODate))                 # 2021-08-12
        # print(now.toString(Qt.DefaultLocaleLongDate))   # 2021년 8월 12일 목요일
        # print(now.toString())
        time = QTime.currentTime()
        # print(time.toString('h.m.s'))                    # 18.40.19
        print(time.toString("hh.mm.ss"))  # 18.40.19
        # print(time.toString('hh.mm.ss.zzz'))             # 18.40.19.864
        print(time.toString(Qt.DefaultLocaleLongDate))  # 오후 6:40:19
        # print(time.toString(Qt.DefaultLocaleShortDate))  # 오후 6:40
        # print(time.toString())

        datetime = QDateTime.currentDateTime()
        # print(datetime.toString('d.M.yy hh:mm:ss'))
        # print(datetime.toString('dd.MM.yyyy, hh:mm:ss'))
        print(datetime.toString("yyyyMMddhhmmss"))
        print(datetime.toString("yyyy.MM.dd(ddd) hh:mm:ss"))
        print(datetime.toString(Qt.DefaultLocaleLongDate))
        print(datetime.toString(Qt.DefaultLocaleShortDate))
        # print(datetime.toString())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class MyAppTest5(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 바닥 레이아웃부터 순서대로
        grid = QGridLayout()
        self.setLayout(grid)

        grid.addWidget(QLabel("Title:"), 0, 0)
        grid.addWidget(QLabel("Author:"), 1, 0)
        grid.addWidget(QLabel("Review:"), 2, 0)

        grid.addWidget(QLineEdit(), 0, 1)
        grid.addWidget(QLineEdit(), 1, 1)
        grid.addWidget(QTextEdit(), 2, 1)

        # 라벨, 버튼
        QToolTip.setFont(QFont("SansSerif", 10))
        self.setToolTip("This is a <b>QWidget</b> widget")
        # btn = QPushButton('Quit', self)
        btn = QPushButton("닫기", self)
        btn.setToolTip("This is a <b>QPushButton</b> widget")
        # self.frameGeometry().right
        right = self.frameGeometry().right()
        # print(f"right=[{right}]")
        btn.move(right - 50, 50)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(QCoreApplication.instance().quit)

        # 최종 Window의 크기 조절 및 위치 조절
        self.setWindowTitle("My First Application")
        self.setGeometry(300, 300, 800, 600)
        self.center()
        self.show()

        # 여긴 임시 테스트
        now = QDate.currentDate()
        # print(now.toString('d.M.yy'))                   # 12.8.21
        # print(now.toString('dd.MM.yyyy'))               # 12.08.2021
        # print(now.toString('yyyy.MM.dd'))               # 2021.12.08
        print(now.toString("yyyy.MM.dd(ddd)"))  # 2021.08.12(목)
        # print(now.toString('ddd.MMMM.yyyy'))            # 목.8월.2021
        # print(now.toString(Qt.ISODate))                 # 2021-08-12
        # print(now.toString(Qt.DefaultLocaleLongDate))   # 2021년 8월 12일 목요일
        # print(now.toString())
        time = QTime.currentTime()
        # print(time.toString('h.m.s'))                    # 18.40.19
        print(time.toString("hh.mm.ss"))  # 18.40.19
        # print(time.toString('hh.mm.ss.zzz'))             # 18.40.19.864
        print(time.toString(Qt.DefaultLocaleLongDate))  # 오후 6:40:19
        # print(time.toString(Qt.DefaultLocaleShortDate))  # 오후 6:40
        # print(time.toString())

        datetime = QDateTime.currentDateTime()
        # print(datetime.toString('d.M.yy hh:mm:ss'))
        # print(datetime.toString('dd.MM.yyyy, hh:mm:ss'))
        print(datetime.toString("yyyyMMddhhmmss"))
        print(datetime.toString("yyyy.MM.dd(ddd) hh:mm:ss"))
        print(datetime.toString(Qt.DefaultLocaleLongDate))
        print(datetime.toString(Qt.DefaultLocaleShortDate))
        # print(datetime.toString())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class MyAppTest4(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 바닥 레이아웃부터 순서대로
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(3)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

        # 라벨, 버튼
        QToolTip.setFont(QFont("SansSerif", 10))
        self.setToolTip("This is a <b>QWidget</b> widget")
        # btn = QPushButton('Quit', self)
        btn = QPushButton("닫기", self)
        btn.setToolTip("This is a <b>QPushButton</b> widget")
        # self.frameGeometry().right
        right = self.frameGeometry().right()
        # print(f"right=[{right}]")
        btn.move(right - 50, 50)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(QCoreApplication.instance().quit)

        # 최종 Window의 크기 조절 및 위치 조절
        self.setWindowTitle("My First Application")
        self.setGeometry(300, 300, 800, 600)
        self.center()
        self.show()

        # 여긴 임시 테스트
        now = QDate.currentDate()
        # print(now.toString('d.M.yy'))                   # 12.8.21
        # print(now.toString('dd.MM.yyyy'))               # 12.08.2021
        # print(now.toString('yyyy.MM.dd'))               # 2021.12.08
        print(now.toString("yyyy.MM.dd(ddd)"))  # 2021.08.12(목)
        # print(now.toString('ddd.MMMM.yyyy'))            # 목.8월.2021
        # print(now.toString(Qt.ISODate))                 # 2021-08-12
        # print(now.toString(Qt.DefaultLocaleLongDate))   # 2021년 8월 12일 목요일
        # print(now.toString())
        time = QTime.currentTime()
        # print(time.toString('h.m.s'))                    # 18.40.19
        print(time.toString("hh.mm.ss"))  # 18.40.19
        # print(time.toString('hh.mm.ss.zzz'))             # 18.40.19.864
        print(time.toString(Qt.DefaultLocaleLongDate))  # 오후 6:40:19
        # print(time.toString(Qt.DefaultLocaleShortDate))  # 오후 6:40
        # print(time.toString())

        datetime = QDateTime.currentDateTime()
        # print(datetime.toString('d.M.yy hh:mm:ss'))
        # print(datetime.toString('dd.MM.yyyy, hh:mm:ss'))
        print(datetime.toString("yyyyMMddhhmmss"))
        print(datetime.toString("yyyy.MM.dd(ddd) hh:mm:ss"))
        print(datetime.toString(Qt.DefaultLocaleLongDate))
        print(datetime.toString(Qt.DefaultLocaleShortDate))
        # print(datetime.toString())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class MyAppTest3(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 바닥 레이아웃부터 순서대로
        lbl_red = QLabel("Red")
        lbl_green = QLabel("Green")
        lbl_blue = QLabel("Blue")

        lbl_red.setStyleSheet(
            "color: red;"
            "border-style: solid;"
            "border-width: 2px;"
            "border-color: #FA8072;"
            "border-radius: 3px"
        )
        lbl_green.setStyleSheet("color: green;" "background-color: #7FFFD4")
        lbl_blue.setStyleSheet(
            "color: blue;"
            "background-color: #87CEFA;"
            "border-style: dashed;"
            "border-width: 3px;"
            "border-color: #1E90FF"
        )
        vbox = QVBoxLayout()
        vbox.addWidget(lbl_red)
        vbox.addWidget(lbl_green)
        vbox.addWidget(lbl_blue)

        self.setLayout(vbox)

        # 라벨, 버튼
        label1 = QLabel("Label1", self)
        label1.move(20, 20)
        label2 = QLabel("Label2", self)
        label2.move(20, 60)

        btn1 = QPushButton("Button1", self)
        btn1.move(80, 13)
        btn2 = QPushButton("Button2", self)
        btn2.move(80, 53)

        QToolTip.setFont(QFont("SansSerif", 10))
        self.setToolTip("This is a <b>QWidget</b> widget")
        # btn = QPushButton('Quit', self)
        btn = QPushButton("닫기", self)
        btn.setToolTip("This is a <b>QPushButton</b> widget")
        # self.frameGeometry().right
        right = self.frameGeometry().right()
        # print(f"right=[{right}]")
        btn.move(right - 50, 50)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(QCoreApplication.instance().quit)

        # 최종 Window의 크기 조절 및 위치 조절
        self.setWindowTitle("My First Application")
        self.setGeometry(300, 300, 800, 600)
        self.center()
        self.show()

        # 여긴 임시 테스트
        now = QDate.currentDate()
        # print(now.toString('d.M.yy'))                   # 12.8.21
        # print(now.toString('dd.MM.yyyy'))               # 12.08.2021
        # print(now.toString('yyyy.MM.dd'))               # 2021.12.08
        print(now.toString("yyyy.MM.dd(ddd)"))  # 2021.08.12(목)
        # print(now.toString('ddd.MMMM.yyyy'))            # 목.8월.2021
        # print(now.toString(Qt.ISODate))                 # 2021-08-12
        # print(now.toString(Qt.DefaultLocaleLongDate))   # 2021년 8월 12일 목요일
        # print(now.toString())
        time = QTime.currentTime()
        # print(time.toString('h.m.s'))                    # 18.40.19
        print(time.toString("hh.mm.ss"))  # 18.40.19
        # print(time.toString('hh.mm.ss.zzz'))             # 18.40.19.864
        print(time.toString(Qt.DefaultLocaleLongDate))  # 오후 6:40:19
        # print(time.toString(Qt.DefaultLocaleShortDate))  # 오후 6:40
        # print(time.toString())

        datetime = QDateTime.currentDateTime()
        # print(datetime.toString('d.M.yy hh:mm:ss'))
        # print(datetime.toString('dd.MM.yyyy, hh:mm:ss'))
        print(datetime.toString("yyyyMMddhhmmss"))
        print(datetime.toString("yyyy.MM.dd(ddd) hh:mm:ss"))
        print(datetime.toString(Qt.DefaultLocaleLongDate))
        print(datetime.toString(Qt.DefaultLocaleShortDate))
        # print(datetime.toString())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class MyAppTest2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        lbl_red = QLabel("Red")
        lbl_green = QLabel("Green")
        lbl_blue = QLabel("Blue")

        lbl_red.setStyleSheet(
            "color: red;"
            "border-style: solid;"
            "border-width: 2px;"
            "border-color: #FA8072;"
            "border-radius: 3px"
        )
        lbl_green.setStyleSheet("color: green;" "background-color: #7FFFD4")
        lbl_blue.setStyleSheet(
            "color: blue;"
            "background-color: #87CEFA;"
            "border-style: dashed;"
            "border-width: 3px;"
            "border-color: #1E90FF"
        )
        vbox = QVBoxLayout()
        vbox.addWidget(lbl_red)
        vbox.addWidget(lbl_green)
        vbox.addWidget(lbl_blue)

        self.setLayout(vbox)

        # exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction = QAction(QIcon("exit.png"), "나가기", self)
        # exitAction = QAction('나가기', self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Exit application")
        exitAction.triggered.connect(qApp.quit)

        # self.statusBar().showMessage('Ready')
        now = QDate.currentDate()
        self.statusBar().showMessage(now.toString("yyyy.MM.dd(ddd)"))

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(exitAction)

        self.toolbar = self.addToolBar("Exit")
        self.toolbar.addAction(exitAction)

        self.setWindowTitle("My First Application")
        self.setGeometry(300, 300, 800, 600)
        self.center()
        self.show()

        # 여긴 임시 테스트
        now = QDate.currentDate()
        # print(now.toString('d.M.yy'))                   # 12.8.21
        # print(now.toString('dd.MM.yyyy'))               # 12.08.2021
        # print(now.toString('yyyy.MM.dd'))               # 2021.12.08
        print(now.toString("yyyy.MM.dd(ddd)"))  # 2021.08.12(목)
        # print(now.toString('ddd.MMMM.yyyy'))            # 목.8월.2021
        # print(now.toString(Qt.ISODate))                 # 2021-08-12
        # print(now.toString(Qt.DefaultLocaleLongDate))   # 2021년 8월 12일 목요일
        # print(now.toString())
        time = QTime.currentTime()
        # print(time.toString('h.m.s'))                    # 18.40.19
        print(time.toString("hh.mm.ss"))  # 18.40.19
        # print(time.toString('hh.mm.ss.zzz'))             # 18.40.19.864
        print(time.toString(Qt.DefaultLocaleLongDate))  # 오후 6:40:19
        # print(time.toString(Qt.DefaultLocaleShortDate))  # 오후 6:40
        # print(time.toString())

        datetime = QDateTime.currentDateTime()
        # print(datetime.toString('d.M.yy hh:mm:ss'))
        # print(datetime.toString('dd.MM.yyyy, hh:mm:ss'))
        print(datetime.toString("yyyyMMddhhmmss"))
        print(datetime.toString("yyyy.MM.dd(ddd) hh:mm:ss"))
        print(datetime.toString(Qt.DefaultLocaleLongDate))
        print(datetime.toString(Qt.DefaultLocaleShortDate))
        # print(datetime.toString())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class MyAppTest1(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        QToolTip.setFont(QFont("SansSerif", 10))
        self.setToolTip("This is a <b>QWidget</b> widget")
        # btn = QPushButton('Quit', self)
        btn = QPushButton("닫기", self)
        btn.setToolTip("This is a <b>QPushButton</b> widget")
        btn.move(50, 50)
        btn.resize(btn.sizeHint())
        btn.clicked.connect(QCoreApplication.instance().quit)

        self.setWindowTitle("My First Application")
        self.setWindowIcon(QIcon("web.png"))
        # self.move(300, 300)
        # self.resize(400, 200)
        self.setGeometry(300, 300, 800, 600)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
