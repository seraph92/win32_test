from ChannelMsgAuto import ChannelMessageSending
import os
import sys
import win32com.shell.shell as shell

from dbm import HistoryMgr
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QDataWidgetMapper,
    QDesktopWidget,
    QDialog,
    QHeaderView,
    QLineEdit,
    QListView,
    QMainWindow,
    QApplication,
    QMessageBox,
    QTableView,
    QTextEdit,
)
from PyQt5 import uic

# signal processing importing
from PyQt5.QtCore import (
    QThread,
    pyqtSlot,
)

from LogCapture import LogCaptureWin32Worker
from BKLOG import *

ui_form = uic.loadUiType("ui/auto_log_program.ui")[0]
UserDetailDialog = uic.loadUiType("ui/user_detail.ui")[0]

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

    def del_msg(self, idx):
        del self.data[idx]
        self.applyModel()

    def deque_msg(self):
        try:
            data = self.data[0]
            del self.data[0]
            self.applyModel()
        except IndexError as ie:
            data = None
        return data


    def add_msg(self, d):
        enter_exit = "등원" if d["rnk"] % 2 else "하원"
        INFO(f"rank = {d['rnk']} = {enter_exit}")

        if enter_exit == "등원":
            enter_exit_msg = "도착했습니다.\n-READ101-"
        elif enter_exit == "하원":
            enter_exit_msg = "수업이 끝났습니다.(출발)\n-READ101-"
        else:
            enter_exit_msg = "출입 체크 되었습니다.\n-READ101-"

        msg = {
            "user": d["name"],
            "message": f"[{d['dtm']}] {d['name']}학생 { enter_exit_msg }",
            "dtm": d["dtm"],
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

class UsersModel(list):
    def __init__(self, l=[]):
        super().__init__()

        self.model = QStandardItemModel()
        self.model.setColumnCount(4)
        self.query_page()

    # 현재 Page 조회
    def query_page(self):
        mgr = HistoryMgr()

        sql = f"SELECT no, user_name, chat_room, reg_dtm \n"
        sql += f"FROM user \n"
        sql += f"WHERE \n"
        sql += f"user_name like '%%'\n"
        sql += f"ORDER BY user_name \n"
        #sql += f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}"

        DEBUG(f"sql = [{sql}]")
        #INFO(f"sql = [{sql}]")

        self.data = mgr.query(sql)

        DEBUG(f"data = [{self.data}]")
        #INFO(f"data = [{self.data}]")

        self.applyModel()

    def getRows(self, idx):
        return self.data[idx]

    # remove Button 클릭시 호출됨 (하지만 현재 사용하지 않음)
    def remove(self, idx):
        DEBUG(f"remove index= [{idx}]")
        temp = self.data[idx]
        del self.data[idx]
        self.applyModel()

        return temp

    # data를 model에 적용
    def applyModel(self):
        self.model.clear()
        self.model.setColumnCount(4)

        self.model.setHorizontalHeaderLabels(
            ["no", "이름", "채팅방", "등록일시"]
        )
        for data in self.data:
            self.model.appendRow(
                [
                    QStandardItem(str(data["no"])),
                    QStandardItem(data["user_name"]),
                    QStandardItem(data["chat_room"]),
                    QStandardItem(data["reg_dtm"]),
                ]
            )



class LogsModel(list):
    def __init__(self, l=[]):
        super().__init__()

        now = datetime.datetime.now()
        self.today = now.strftime("%Y%m%d")
        # self.PAGE_SIZE = 20
        self.PAGE_SIZE = 15
        self.current_page = 1

        self.item_data = {}
        self.item_data["current_page"] = 1

        self.model = QStandardItemModel()
        self.model.setColumnCount(7)
        self.aggregation_model = QStandardItemModel()
        self.today_model = QStandardItemModel()
        self.query_page()

        """
        mgr = HistoryMgr()
        self.total_page = mgr.query_total_page(self.PAGE_SIZE)
        self.item_data["total_page"] = self.total_page

        #DEBUG(f"self.item_data=[{self.item_data}]")
        #DEBUG(f"total_page = [{self.item_data['total_page']}]")

        sql = f"SELECT dtm, name, temper, dtm2, reg_dtm, send_dtm \n"
        sql += f"FROM inout_history \n"
        sql += f"WHERE \n"
        sql += f"name like '%%'"
        sql += f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}"

        self.data = mgr.query(sql)

        DEBUG(f"data = [{self.data}]")

        self.model = QStandardItemModel()
        self.model.setColumnCount(7)
        self.aggregation_model = QStandardItemModel()

        self.applyModel()
        """

    # Total Page 조회
    def query_total_page(self):
        page = self.PAGE_SIZE
        today = f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:8]}"
        mgr = HistoryMgr()
        sql = f"select count(*) / {page} + case count(*) % {page} when 0 then 0 else 1 END as total_page\n"
        sql += f"from inout_history\n"
        sql += f"where date(dtm) = date('{today}')\n"
        rslt = mgr.query(sql)
        return rslt[0]["total_page"]

    # 현재 Page 조회
    def query_page(self):
        mgr = HistoryMgr()
        # self.total_page = mgr.query_total_page(self.PAGE_SIZE)
        self.total_page = self.query_total_page()
        self.item_data["current_page"] = self.current_page
        self.item_data["total_page"] = self.total_page
        today = f"{self.today[:4]}-{self.today[4:6]}-{self.today[6:8]}"
        INFO(f"self.today = {self.today}")
        INFO(f"today = {today}")
        # 20210809

        sql = f"SELECT dtm, name, temper, dtm2, reg_dtm, rank() over (PARTITION BY name ORDER by dtm) as rnk, send_dtm \n"
        sql += f"FROM inout_history \n"
        sql += f"WHERE \n"
        sql += f"name like '%%'\n"
        sql += f"and date(dtm) = date('{today}')\n"
        sql += f"ORDER BY dtm desc\n"
        sql += f"LIMIT {self.PAGE_SIZE} OFFSET {self.PAGE_SIZE*(self.current_page-1)}"

        DEBUG(f"sql = [{sql}]")

        self.data = mgr.query(sql)

        DEBUG(f"data = [{self.data}]")

        self.applyModel()

    def getRows(self, idx):
        return self.data[idx]

    # before Button 클릭시 호출됨
    def before_page(self):
        self.current_page -= 1
        if self.current_page < 1:
            self.current_page = 1

        DEBUG(f"before current_page=[{self.current_page}]")
        # self.model.clear()
        # self.aggregation_model.clear()
        self.query_page()

    # next Button 클릭시 호출됨
    def next_page(self):
        self.current_page += 1
        if self.current_page > self.total_page:
            self.current_page = self.total_page

        DEBUG(f"next current_page=[{self.current_page}]")
        # self.model.clear()
        # self.aggregation_model.clear()
        self.query_page()

    # remove Button 클릭시 호출됨 (하지만 현재 사용하지 않음)
    def remove(self, idx):
        DEBUG(f"remove index= [{idx}]")
        temp = self.data[idx]
        del self.data[idx]
        # last_idx = len(self.data) - 1
        # DEBUG(f"remove last_Index [{last_idx}]")

        # self.data[idx] = self.data[last_idx]
        # self.data[last_idx] = temp
        # self.data.pop()

        # self.model.clear()
        # self.aggregation_model.clear()
        self.applyModel()

        return temp

    def update_sent_dtm(self, user_msg):
        mgr = HistoryMgr()
        sql = f"UPDATE inout_history\n"
        sql += f"SET send_dtm = strftime('%Y-%m-%d %H:%M:%f','now')\n"
        sql += f"where dtm = '{user_msg['dtm']}'\n"
        rslt = mgr.execute(sql)
        mgr.dbconn.commit()
        self.query_page()
        self.applyModel()

    # data를 model에 적용
    def applyModel(self):
        self.model.clear()
        self.model.setColumnCount(7)
        self.aggregation_model.clear()

        DEBUG(
            f"Page: {self.item_data['current_page']} / {self.item_data['total_page']}"
        )

        self.today_model.appendRow(
            [
                QStandardItem(f"{self.today}"),
            ]
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

        # Log Tab
        self.view: QTableView = views["table_view"]
        self.model: LogsModel = models["log_model"]

        self.paging_mapper = QDataWidgetMapper()
        self.paging_mapper.setModel(models["log_model"].aggregation_model)

        self.today_mapper = QDataWidgetMapper()
        self.today_mapper.setModel(models["log_model"].today_model)

        self.page_edit: QLineEdit = views["page_edit"]

        # User Tab
        self.user_view: QTableView = views["user_table_view"]
        self.user_model: LogsModel = models["user_model"]


        # Left Top
        self.msg_view: QListView = views["msg_view"]
        self.msg_model: MsgsModel = models["msg_model"]
        # Right Bottom
        self.scrap_log_edit: QTextEdit = views["scrap_log_edit"]
        # Left Bottom

        self.dataInit()

        self.view.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # event 할당
        views["before_button"].clicked.connect(self.before_page)
        views["before_button2"].clicked.connect(self.before_page)
        views["next_button"].clicked.connect(self.next_page)
        views["next_button2"].clicked.connect(self.next_page)
        views["today_edit"].editingFinished.connect(self.date_change)

        views["regist_user_button"].clicked.connect(self.show_dialog)
        views["regist_user_button2"].clicked.connect(self.show_dialog)

        self.view.doubleClicked.connect(self.add_msg)
        self.msg_view.doubleClicked.connect(self.del_msg)

        self.setup_log_capture_thread()
        #self.setup_send_msg_thread()

    def show_dialog(self):
        #self.views["user_detail_dialog"].exec()
        # 신규등록 창
        dlg = UserDetailDlg(self.parent)
        dlg.accepted.connect(self.dialog_accept)
        dlg.rejected.connect(self.dialog_reject)
        dlg.exec()

    def dialog_accept(self):
        pass

    def dialog_reject(self):
        pass

    def adjust_user_view_column(self):
        header = self.user_view.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(header.count() - 1, QtWidgets.QHeaderView.Stretch)

    def adjust_log_view_column(self):
        header = self.view.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(header.count() - 1, QtWidgets.QHeaderView.Stretch)


    def setup_send_msg_thread(self):
        # Log Capture Thread 설정
        self.msg_thread = QThread()
        self.msg_worker = ChannelMessageSending()
        self.msg_worker.moveToThread(self.msg_thread)

        self.msg_thread.started.connect(self.msg_worker.run)
        self.msg_worker.finished.connect(self.msg_thread.quit)
        self.msg_worker.finished.connect(self.msg_worker.deleteLater)
        self.msg_thread.finished.connect(self.msg_thread.deleteLater)

        self.msg_thread.started.connect(
            lambda: self.views["msg_edit"].setStyleSheet("background: rightblue")
        )
        self.msg_thread.finished.connect(
            lambda: self.views["msg_edit"].setStyleSheet("background-color: #f5d6c1;")
        )

        # Step 6: Start the thread
        self.msg_thread.start()

        # 중복 로그는 남기지 않음
        self.msg_worker.need_msg.connect(self.send_msg)
        self.msg_worker.one_processed.connect(self.log_sending)
        # self.msg_worker.inserted.connect(self.inserted_handle)

    def setup_log_capture_thread(self):
        # Log Capture Thread 설정
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

        # 중복 로그는 남기지 않음
        # self.worker.dupped.connect(self.dup_handle)
        self.worker.inserted.connect(self.inserted_handle)

    def __del__(self):
        # self.logCapture.loop_flag = False
        DEBUG(f"LogViewModel destroyed!!")

    def log_sending(self, user_msg):
        INFO(f"{user_msg}")
        self.model.update_sent_dtm(user_msg)

    def send_msg(self):
        # 첫번째 데이터를 꺼내서 msg_worker로 전송
        data = self.msg_model.deque_msg()
        if data:
            self.msg_worker.user_msgs.append(data)

    def date_change(self):
        self.model.today = self.views["today_edit"].text()
        INFO(f"date changed = [{self.model.today}]")
        self.model.current_page = 1
        self.model.query_total_page()
        self.model.query_page()
        self.paging_mapper.toFirst()

    def del_msg(self, model):
        row = self.msg_view.currentIndex().row()
        # column = self.view.currentIndex().column()
        self.msg_model.del_msg(row)
        DEBUG(f"delete row = [{row}]")

    def add_msg(self, model):
        row = self.view.currentIndex().row()
        # column = self.view.currentIndex().column()
        rows = self.model.getRows(row)
        DEBUG(f"rows = [{rows}]")
        if not rows["send_dtm"]:
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
        # Log Tab
        self.view.setModel(self.model.model)
        self.paging_mapper.addMapping(self.page_edit, 0)
        self.paging_mapper.toFirst()
        self.today_mapper.addMapping(self.views["today_edit"], 0)
        self.today_mapper.toFirst()
        self.adjust_log_view_column()

        # User Tab
        self.user_view.setModel(self.user_model.model)
        self.adjust_user_view_column()

        # Left Top (List)
        self.msg_view.setModel(self.msg_model.model)

    def before_page(self):
        self.model.before_page()
        self.paging_mapper.toFirst()

    def next_page(self):
        self.model.next_page()
        self.paging_mapper.toFirst()

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


class UserDetailDlg(QDialog, UserDetailDialog):
    """User Detail Dialog."""
    def __init__(self, parent=None, user_name=None):
        super().__init__(parent)
        self.setupUi(self)

        self.user_name = user_name

        self.views = {}

        self.views["user_name_edit"] = self.user_name_edit
        self.views["chat_room_edit"] = self.chat_room_edit
        self.views["reg_dtm_edit"]   = self.reg_dtm_edit

        if self.user_name:
            self.setWindowTitle("사용자 정보 수정")
        else:
            self.setWindowTitle("사용자 정보 등록")

class MainWindow(QMainWindow, ui_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.views = {}
        ## Log Tab
        self.views["table_view"] = self.logTableView
        self.views["page_edit"] = self.pageEdit
        self.views["today_edit"] = self.todayEdit
        self.views["before_button"] = self.beforeBtn
        self.views["before_button2"] = self.beforeBtn2
        self.views["next_button"] = self.nextBtn
        self.views["next_button2"] = self.nextBtn2

        ## User Tab
        self.views["user_table_view"] = self.userTableView
        self.views["regist_user_button"] = self.registUserBtn
        self.views["regist_user_button2"] = self.registUserBtn2

        ## Left Bottom List
        self.views["scrap_log_edit"] = self.scrapLogEdit
        ## Right Bottom List
        self.views["log_edit"] = self.logEdit
        ## Left Top List
        self.views["msg_view"] = self.msgListView

        ## Dialog
        #self.views["user_detail_dialog"] = UserDetailDlg(self)

        self.models = {}
        ## table_view의 모델
        self.models["log_model"] = LogsModel()
        ## msg_view의 모델
        self.models["msg_model"] = MsgsModel()
        ## user_table_view의 모델
        self.models["user_model"] = UsersModel()

        self.logViewModel = LogViewModel(self, self.views, self.models)

        self.adjustColumnSize()

        # self.setGeometry(300, 300, 1280, 768)
        self.setGeometry(300, 300, 1024, 768)
        self.center()
        self.show()

    # def resizeEvent(self, resizeEvent: QtGui.QResizeEvent) -> None:
    #     self.gridLayout.setFixedSize(resizeEvent.size)

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
