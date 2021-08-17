import os
import sys
import win32com.shell.shell as shell

from dbm import HistoryMgr
import time
import traceback
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QDataWidgetMapper,
    QDesktopWidget,
    QHeaderView,
    QLineEdit,
    QListView,
    QMainWindow,
    QApplication,
    QMessageBox,
    QTableView,
    QTextEdit,
)
from PyQt5 import QtCore
from PyQt5 import uic

# signal processing importing
from PyQt5.QtCore import (
    QModelIndex,
    QRunnable,
    QThread,
    QThreadPool,
    pyqtSlot,
    pyqtSignal,
    QObject,
)

from LogCapture import LogCaptureWin32Worker
from BKLOG import *

ui_form = uic.loadUiType("ui/auto_log_program.ui")[0]


class MsgsModel(list):
    def __init__(self, l=[]):
        super().__init__()

        self.data = []
        self.model = QStandardItemModel()

    def applyModel(self):
        self.model.clear()
        for data in self.data:
            self.model.appendRow(
                [
                    QStandardItem(data["user"]),
                    QStandardItem(data["message"]),
                ]
            )

    def add_msg(self, d):
        enter_exit = "등원" if d["rnk"] % 2 else "하원"
        INFO(f"rank = {d['rnk']} = {enter_exit}")
        msg = {
            "user": d["name"],
            "message": f"[{d['dtm']}] {d['name']}학생이 리드101송도학원에 { enter_exit }하였습니다.",
        }

        INFO(f"msg = [{msg}]")

        # 기 발송 검증
        if d["send_dtm"]:
            return

        # 중복 검증
        # {k: v for k, v in my_dict.items() if int(v) > 2000}
        # INFO(f"data = [{self.data}]")
        names = (data["user"] for data in self.data)
        # INFO(f"names = [{names}]")
        if d["name"] in names:
            return

        self.data.append(msg)
        self.applyModel()


class LogsModel(list):
    def __init__(self, l=[]):
        super().__init__()

        # self.PAGE_SIZE = 20
        self.PAGE_SIZE = 15
        self.current_page = 1

        self.item_data = {}
        self.item_data["current_page"] = 1

        self.model = QStandardItemModel()
        self.model.setColumnCount(7)
        self.aggregation_model = QStandardItemModel()
        self.query_page()

        """
        mgr = HistoryMgr()
        self.total_page = mgr.query_total_page(self.PAGE_SIZE)
        self.item_data["total_page"] = self.total_page

        #print(f"self.item_data=[{self.item_data}]")
        #print(f"total_page = [{self.item_data['total_page']}]")

        sql = f"SELECT dtm, name, temper, dtm2, reg_dtm, send_dtm \n"
        sql += f"FROM inout_history \n"
        sql += f"WHERE \n"
        sql += f"name like '%%'"
        sql += f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}"

        self.data = mgr.query(sql)

        print(f"data = [{self.data}]")

        self.model = QStandardItemModel()
        self.model.setColumnCount(7)
        self.aggregation_model = QStandardItemModel()

        self.applyModel()
        """

    def query_page(self):

        mgr = HistoryMgr()
        self.total_page = mgr.query_total_page(self.PAGE_SIZE)
        self.item_data["current_page"] = self.current_page
        self.item_data["total_page"] = self.total_page

        sql = f"SELECT dtm, name, temper, dtm2, reg_dtm, rank() over (PARTITION BY name ORDER by dtm) as rnk, send_dtm \n"
        sql += f"FROM inout_history \n"
        sql += f"WHERE \n"
        sql += f"name like '%%'\n"
        sql += f"ORDER BY dtm desc\n"
        sql += f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}"

        print(f"sql = [{sql}]")

        self.data = mgr.query(sql)

        print(f"data = [{self.data}]")

        # self.model = QStandardItemModel()
        # self.aggregation_model = QStandardItemModel()
        self.model.clear()
        self.model.setColumnCount(7)
        self.aggregation_model.clear()

        self.applyModel()

    def getRows(self, idx):
        return self.data[idx]

    def before_page(self):
        self.current_page -= 1
        if self.current_page < 1:
            self.current_page = 1

        print(f"before current_page=[{self.current_page}]")
        # self.model.clear()
        # self.aggregation_model.clear()
        self.query_page()

    def next_page(self):
        self.current_page += 1
        if self.current_page > self.total_page:
            self.current_page = self.total_page

        print(f"next current_page=[{self.current_page}]")
        # self.model.clear()
        # self.aggregation_model.clear()
        self.query_page()

    def remove(self, idx):
        DEBUG(f"remove index= [{idx}]")
        temp = self.data[idx]
        del self.data[idx]
        # last_idx = len(self.data) - 1
        # DEBUG(f"remove last_Index [{last_idx}]")

        # self.data[idx] = self.data[last_idx]
        # self.data[last_idx] = temp
        # self.data.pop()

        self.model.clear()
        self.aggregation_model.clear()
        self.applyModel()

        return temp

    def applyModel(self):

        print(
            f"Page: {self.item_data['current_page']} / {self.item_data['total_page']}"
        )

        self.aggregation_model.appendRow(
            [
                # QStandardItem(f"{self.item_data['current_page']} / {self.item_data['total_page']}"),
                QStandardItem(f"{self.current_page} / {self.item_data['total_page']}"),
            ]
        )

        self.model.setHorizontalHeaderLabels(
            ["출입일시", "이름", "온도", "일시2", "등록일시", "등하원", "전송일시"]
        )
        for data in self.data:
            self.model.appendRow(
                [
                    QStandardItem(data["dtm"]),
                    QStandardItem(data["name"]),
                    QStandardItem(data["temper"]),
                    QStandardItem(data["dtm2"]),
                    QStandardItem(data["reg_dtm"]),
                    QStandardItem("등원" if data["rnk"] % 2 else "하원"),
                    QStandardItem(data["send_dtm"]),
                ]
            )


class LogViewModel:
    def __init__(self, parent, views, models):
        self.parent = parent
        self.log_capture_loop = None
        self.views = views

        self.view: QTableView = views["table_view"]
        self.msg_view: QListView = views["msg_view"]
        self.item_view: QLineEdit = views["item_view"]
        # self.view = views["table_view"]
        self.scrap_log_edit: QTextEdit = views["scrap_log_edit"]

        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(models["log_model"].aggregation_model)

        self.model: LogsModel = models["log_model"]
        self.msg_model: MsgsModel = models["msg_model"]
        self.dataInit()

        # event 할당
        # self.view.clicked.connect(self.removeConfirm)
        self.view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        views["before_button"].clicked.connect(self.before_page)
        views["before_button2"].clicked.connect(self.before_page)
        views["next_button"].clicked.connect(self.next_page)
        views["next_button2"].clicked.connect(self.next_page)

        self.view.doubleClicked.connect(self.add_msg)

        # 두개의 thread를 위한 threadpool 생성
        self.thread = QThread()
        self.worker = LogCaptureWin32Worker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # self.worker.progress.connect(self.reportProgress)

        self.thread.started.connect(
            lambda: self.views["log_edit"].setStyleSheet("background: rightblue")
        )
        self.thread.finished.connect(
            lambda: self.views["log_edit"].setStyleSheet("background-color: #f5d6c1;")
        )

        # Step 6: Start the thread
        self.thread.start()

        ## TO-DO
        # Channel Message 전송 Thread가 동작하고
        # 처리과정은 logEdit로 보내져야 한다.
        # Thread가 살아 있다면 logEidt의 배경은 파란색으로, 죽어 있다면 붉은색으로 변경

        # 중복 로그는 남기지 않음
        self.worker.dupped.connect(self.dup_handle)
        self.worker.inserted.connect(self.inserted_handle)

    def __del__(self):
        # self.logCapture.loop_flag = False
        print(f"LogViewModel destroyed!!")

    def add_msg(self, model):
        row = self.view.currentIndex().row()
        # column = self.view.currentIndex().column()
        rows = self.model.getRows(row)
        DEBUG(f"rows = [{rows}]")
        self.msg_model.add_msg(rows)

    # scrap시 dup발생시 호출되는 함수
    def dup_handle(self, strlog, error):
        # self.scrap_log_edit.append(f"[{strlog}]-[{error}]")
        self.views["log_edit"].append(f"[{strlog}]-[{error}]")
        self.views["log_edit"].verticalScrollBar().setValue(
            self.views["log_edit"].verticalScrollBar().maximum()
        )

    # scrap시 insert발생시 호출되는 함수
    def inserted_handle(self, strlog):
        self.views["log_edit"].append(f"[{strlog}]")
        self.views["log_edit"].verticalScrollBar().setValue(
            self.views["log_edit"].verticalScrollBar().maximum()
        )

    def dataInit(self):
        self.view.setModel(self.model.model)
        self.msg_view.setModel(self.msg_model.model)
        self.mapper.addMapping(self.item_view, 0)
        self.mapper.toFirst()

    def before_page(self):
        self.model.before_page()
        self.mapper.toFirst()

    def next_page(self):
        self.model.next_page()
        self.mapper.toFirst()

    def removeConfirm(self):
        data = self.view.selectedIndexes()
        idx = data[0].row()

        msg = "[%s]에 발생한 [%s]님의 출입로그를 삭제하시겠습니까?" % (
            self.model.data[idx]["dtm"],
            self.model.data[idx]["name"],
        )

        rst = QMessageBox.question(
            None, "삭제하시겠습니까?", msg, QMessageBox.Yes | QMessageBox.No
        )

        if rst == QMessageBox.Yes:
            self.model.remove(idx)


# class Worker(QObject):
#     finished = pyqtSignal()
#     error = pyqtSignal(tuple)
#     result = pyqtSignal(object)
#     progress = pyqtSignal()

#     def __init__(self, *args, **kwargs):
#         super(QObject, self).__init__()

#         # Store constructor arguments (re-used for processing)
#         self.args = args
#         self.kwargs = kwargs
#         self.isRunning = True

#     @pyqtSlot()
#     def run(self):
#         while self.isRunning:
#             self.progress.emit()

#         self.finished.emit()

#     @pyqtSlot()
#     def stop(self):
#         self.isRunning = False


class MainWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.views = {}
        self.views["table_view"] = self.logTableView
        self.views["msg_view"] = self.msgListView
        self.views["item_view"] = self.pageEdit
        self.views["before_button"] = self.beforeBtn
        self.views["before_button2"] = self.beforeBtn2
        self.views["next_button"] = self.nextBtn
        self.views["next_button2"] = self.nextBtn2
        self.views["scrap_log_edit"] = self.scrapLogEdit
        self.views["log_edit"] = self.logEdit

        self.models = {}
        self.models["log_model"] = LogsModel()
        self.models["msg_model"] = MsgsModel()

        # self.logsModel = LogsModel()
        # self.logViewModel = LogViewModel(self.logTableView, self.logsModel)
        # self.logViewModel = LogViewModel(self.views, self.logsModel)
        self.logViewModel = LogViewModel(self, self.views, self.models)

        # QDataWidgetMapper

        self.adjustColumnSize()

        # self.setGeometry(300, 300, 1280, 768)
        self.setGeometry(300, 300, 1024, 768)
        self.center()
        self.show()

        # edit = QLineEdit()
        # edit.

    @pyqtSlot()
    def adjustColumnSize(self):
        header = self.logTableView.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        # self.logTableView.setColumnWidth(5, 50)
        header.setSectionResizeMode(header.count() - 1, QtWidgets.QHeaderView.Stretch)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def uac_require():
    asadmin = "asadmin"
    # try:
    if sys.argv[-1] != asadmin:
        script = os.path.abspath(sys.argv[0])
        params = " ".join([script] + sys.argv[1:] + [asadmin])
        shell.ShellExecuteEx(lpVerb="runas", lpFile=sys.executable, lpParameters=params)
        sys.exit(0)
    return True
    # except:
    #    return False


if __name__ == "__main__":
    # if uac_require():
    #    INFO("continue")
    # else:
    #    ERROR("error message")

    app = QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.setWindowTitle("Log Monitor")
    # myWindow.show()
    # 이벤트 큐 루프에 들어가기전 log capture thread와 channel message sending thread 가동
    app.exec_()
