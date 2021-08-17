import sys
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
    QMainWindow,
    QApplication,
    QMessageBox,
    QTableView,
)
from PyQt5 import QtCore
from PyQt5 import uic

# signal processing importing
from PyQt5.QtCore import QRunnable, QThread, QThreadPool, pyqtSlot, pyqtSignal, QObject

from LogCapture import LogCaptureWin32, log_capture_main
from BKLOG import *

ui_form = uic.loadUiType("ui/auto_log_program.ui")[0]


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

        sql = f"SELECT dtm, name, temper, dtm2, reg_dtm, send_dtm \n"
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
            ["출입일시", "이름", "온도", "일시2", "등록일시", "전송일시", "전송버튼"]
        )
        for data in self.data:
            self.model.appendRow(
                [
                    QStandardItem(data["dtm"]),
                    QStandardItem(data["name"]),
                    QStandardItem(data["temper"]),
                    QStandardItem(data["dtm2"]),
                    QStandardItem(data["reg_dtm"]),
                    QStandardItem(data["send_dtm"]),
                    QStandardItem(""),
                ]
            )


class LogViewModel:
    def __init__(self, parent, views, models):
        self.parent = parent
        self.log_capture_loop = None
        self.views = views

        self.view = views["table_view"]
        self.item_view = views["item_view"]
        self.view = views["table_view"]
        self.scrap_log_edit = views['scrap_log_edit']

        self.mapper = QDataWidgetMapper()
        self.mapper.setModel(models["logModel"].aggregation_model)

        self.model = models["logModel"]
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
        # 두개의 thread를 위한 threadpool 생성
        self.threadpool = QThreadPool()
        INFO(
            "Multithreading with maximum %d threads" % self.threadpool.maxThreadCount()
        )

        self.logCapture = LogCaptureWin32()
        # 중복 로그는 남기지 않음
        #self.logCapture.dupped.connect(self.dup_handle)
        self.logCapture.inserted.connect(self.inserted_handle)

        # self.do_work(self.log_capture_fn)
        self.do_work(self.log_capture_fn)

        #self.log_capture_th = QThread(self.parent)
        #logCapture = LogCaptureWin32()
        #logCapture.moveToThread(self.log_capture_th)
        #self.log_capture_th.start()

        ## TO-DO
        # Channel Message 전송 Thread가 동작하고
        # 처리과정은 logEdit로 보내져야 한다.
        # Thread가 살아 있다면 logEidt의 배경은 파란색으로, 죽어 있다면 붉은색으로 변경

        # self.view
        # self.model.onDataChange.connect(self.adjustColumnSize)

        # self.view.resizeColumnsToContents()
        # self.view.setColumnWidth(2, 50)

    def __del__(self):
        #self.logCapture.loop_flag = False
        print(f"LogViewModel destroyed!!")

    # thread를 만들어 pool에 추가한다.
    def do_work(self, _fn, *args, **kwargs):
        # Pass the function to execute
        worker = Worker(
            # self.log_capture_fn
            _fn
        )  # Any other args, kwargs are passed to the run function
        worker.setAutoDelete(True)

        if "result_signal_handler" in kwargs:
            worker.signals.result.connect(kwargs["result_signal_handler"])

        if "finished_signal_handler" in kwargs:
            worker.signals.finished.connect(kwargs["finished_signal_handler"])

        if "progress_signal_handler" in kwargs:
            worker.signals.progress.connect(kwargs["progress_signal_handler"])

        # Execute
        self.threadpool.start(worker)

    def log_capture_fn(self, progress_callback):
        #self.log_capture_loop = logCapture.loop_flag
        self.logCapture.run()
        #log_capture_main()
            # progress_callback.emit(n * 100 / 4)

        return "Done."

    # scrap시 dup발생시 호출되는 함수
    def dup_handle(self, strlog, error):
        #self.scrap_log_edit.append(f"[{strlog}]-[{error}]")
        self.views['log_edit'].append(f"[{strlog}]-[{error}]")

    # scrap시 insert발생시 호출되는 함수
    def inserted_handle(self, strlog):
        self.views['log_edit'].append(f"[{strlog}]")

    def dataInit(self):
        self.view.setModel(self.model.model)
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


# class LogCaptureWorker(QObject):
#     finished = pyqtSignal()
#     ticReady = pyqtSignal(int)
#     response = pyqtSignal()

#     def __init__(self):
#         self.loop = True

#     @pyqtSlot()
#     def run(self):  # A slot takes no params
#         while self.loop:
#             time.sleep(1)
#             self.ticReady.emit(i)
#             self.response.emit()

#         self.finished.emit()


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data
    error
        tuple (exctype, value, traceback.format_exc() )
    result
        object data returned from processing, anything
    progress
        int indicating % progress
    """

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        if "progress_callback" not in self.kwargs:
            self.kwargs["progress_callback"] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class MainWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.views = {}
        self.views["table_view"] = self.logTableView
        self.views["item_view"] = self.pageEdit
        self.views["before_button"] = self.beforeBtn
        self.views["before_button2"] = self.beforeBtn2
        self.views["next_button"] = self.nextBtn
        self.views["next_button2"] = self.nextBtn2
        self.views["scrap_log_edit"] = self.scrapLogEdit
        self.views["log_edit"] = self.logEdit

        self.models = {}
        self.models["logModel"] = LogsModel()

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
    try:
        if sys.argv[-1] != asadmin:
            script = os.path.abspath(sys.argv[0])
            params = " ".join([script] + sys.argv[1:] + [asadmin])
            shell.ShellExecuteEx(
                lpVerb="runas", lpFile=sys.executable, lpParameters=params
            )
            sys.exit()
        return True
    except:
        return False


if __name__ == "__main__":
    if uac_require():
        INFO("continue")
    else:
        ERROR("error message")

    app = QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.setWindowTitle("Log Monitor")
    # myWindow.show()
    # 이벤트 큐 루프에 들어가기전 log capture thread와 channel message sending thread 가동
    app.exec_()
