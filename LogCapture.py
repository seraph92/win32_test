from PyQt5.QtCore import QObject, QRunnable, pyqtSignal
import win32gui
from pywinauto.application import Application

# import pywinauto
import time
import re

import sqlite3

from BKLOG import *

GLOBAL_WIN = "AGENT"
#GLOBAL_WIN = "EDIT"


class HistoryMgr:
    # SELECT strftime('%Y-%m-%d %H:%M:%S','now') as dtm, strftime('%Y-%m-%d %H:%M:%f','now') as udtm, strftime('%s','now') as unixdtm, date('now') as dt
    def __init__(self, dbconn=None):
        self.INSERT_HISTORY = "INSERT INTO inout_history(dtm, name, temper, dtm2, reg_dtm) values (?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%f','now'))"
        self.dbconn = dbconn
        if self.dbconn == None:
            self.dbconn = sqlite3.connect("data/log.db")

        self.cur = self.dbconn.cursor()

    def execute_param(self, exec_str, param):
        result = self.cur.execute(exec_str, param)
        DEBUG(f"exec result=[{result}]")
        return result

    def execute(self, exec_str):
        result = self.dbconn.execute(exec_str)
        DEBUG(f"exec result=[{result}]")
        return result

    def query(self, exec_str):
        cur = self.cur.execute(exec_str)
        DEBUG(f"query result(cur)=[{cur}]")
        rows = cur.fetchall()
        return rows

    def commit(self):
        self.dbconn.commit()

    def rollback(self):
        self.dbconn.rollback()

    def __del__(self):
        self.dbconn.close()
        DEBUG(f"db Connection Closed!!")


class WindowsObject:
    def __init__(self, text=None, parent_hwnd=None):
        self.win_objs = []
        win32gui.EnumWindows(self.__EnumWindowsHandler, text)
        if len(self.win_objs) < 1:
            raise ValueError("Windows Object를 발견하지 못하였습니다.")
        self.obj = self.win_objs[0]

    def getFirstObj(self):
        if len(self.win_objs) < 1:
            return None
        else:
            return self.win_objs[0]

    def __EnumWindowsHandler(self, hwnd, find_text):
        wintext = win32gui.GetWindowText(hwnd)
        if find_text:
            if wintext.find(find_text) != -1:
                obj = {}
                obj["handle"] = hwnd
                obj["text"] = wintext
                self.win_objs.append(obj)
        else:
            obj = {}
            obj["handle"] = hwnd
            obj["text"] = wintext
            self.win_objs.append(obj)
        # print ("%08X: %s" % (hwnd, wintext))


def log_processing(compiled_pattern, strLog):
    history_mgr = HistoryMgr()
    DEBUG(f"strLog=[{strLog}]")
    # 외부로 이동
    # p = re.compile(r"\[(?P<dtm>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] 출입 확인 \(이름: (?P<name>.*), 체온: (?P<temper>[0-9.]{5}) 출입시간 : (?P<dtm2>.{19})\)")
    p = compiled_pattern
    m = p.match(strLog)

    # DEBUG(f"m          = [{m}]")
    # DEBUG(f"m.group(0) = [{m.group(0)}]")
    # DEBUG(f"m.group(1) = [{m.group(1)}]")
    # DEBUG(f"m.group(2) = [{m.group(2)}]")
    # DEBUG(f"m.group(3) = [{m.group(3)}]")
    # DEBUG(f"m.group(4) = [{m.group(4)}]")

    try:
        DEBUG(f"m.group(dtm)    = [{m.group('dtm')}]")
        DEBUG(f"m.group(name)   = [{m.group('name')}]")
        DEBUG(f"m.group(temper) = [{m.group('temper')}]")
        DEBUG(f"m.group(dtm2)   = [{m.group('dtm2')}]")
    except AttributeError as ae:
        # 파싱 오류
        DEBUG(f"파싱 오류 무시 DB처리 하지 않음 [{ae}]")
        return

    # DB처리 (Cache 검증 및 insert)
    try:
        history_mgr.execute_param(
            history_mgr.INSERT_HISTORY,
            (m.group("dtm"), m.group("name"), m.group("temper"), m.group("dtm2")),
        )
    except sqlite3.IntegrityError as si:
        # Insert 무결성은 무시
        DEBUG(f"INSERT 무결성은 무시 [{si}]")
    else:
        history_mgr.commit()
        INFO(f"로그등록:[{strLog}]")


def monitoring(edit_control, loop_flag=True):
    loop_flag = True
    processing_pattern = re.compile(
        r"\[(?P<dtm>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] 출입 확인 \(이름: (?P<name>.*), 체온: (?P<temper>[0-9.]{5}) 출입시간 : (?P<dtm2>.{19})\)"
    )

    while loop_flag:
        #        try:
        line_cnt = edit_control.line_count()
        DEBUG(f"line_cnt:[{line_cnt}]")

        for i in range(0, line_cnt):
            # INFO(f"Line[{i}]:[{edit_control.get_line(i)}]")
            log_processing(processing_pattern, edit_control.get_line(i))
        DEBUG("")
        time.sleep(3)
    #        except:
    #            loop_flag=False

    return loop_flag


def log_capture_main():
    w = WindowsObject("KRC-EC100 에이전트 v1.2.5.0 학원번호 : test - [  ]")
    # w = WindowsObject("sample.txt - Windows 메모장")

    DEBUG(f"w={w.win_objs}")
    DEBUG("w.handle,text=[%08X][%s]" % (w.obj["handle"], w.obj["text"]))

    # app = Application(backend="uia").start('notepad.exe') # process 실행
    # app = Application(backend="uia").connect(handle=0x000808B4)
    # app = Application(backend="win32").start('notepad.exe') # process 실행
    # app = Application(backend="win32").start(r'C:\Program Files (x86)\드림시큐리티\KRC-EC100 에이전트\ACT Agent.exe') # process 실행
    # app = Application(backend="win32").start(r'C:\Program Files (x86)\드림시큐리티\KRC-EC100 에이전트\ACT Agent.exe') # process 실행
    # app = Application(backend="win32").connect(handle=0x000B0916)
    # app = Application().connect(title_re=".*Notepad", class_name="Notepad")
    # app = Application(backend="win32").connect(path=r"C:\Program Files (x86)\드림시큐리티\KRC-EC100 에이전트\ACT Agent.exe")
    hwnd = w.obj["handle"]
    app = Application(backend="win32").connect(handle=hwnd)

    # dig = app.window(title='KRC-EC100 에이전트 v1.2.5.0 학원번호 : test - [  ]')
    dig = app.window(handle=hwnd)
    # dig.print_control_identifiers()

    # WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1
    logwin = dig.child_window(
        class_name="WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1"
    )
    # logwin = dig.child_window(class_name="Edit")

    result = monitoring(logwin)

    # print(f"메모장내용:[{logwin.text_block()}]")
    # print(f"메모장내용:[{logwin.window_text()}]")


class LogCaptureWin32Worker(QObject):
    finished = pyqtSignal()
    inserted = pyqtSignal(str)
    dupped = pyqtSignal(str, str)
    in_processing = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.loop_flag = True
        if GLOBAL_WIN == "AGENT":
            self.w = WindowsObject("KRC-EC100 에이전트 v1.2.5.0 학원번호 : test - [  ]")
        else:
            self.w = WindowsObject("sample.txt - Windows 메모장")

        DEBUG(f"w={self.w.win_objs}")
        DEBUG("w.handle,text=[%08X][%s]" % (self.w.obj["handle"], self.w.obj["text"]))

        self.hwnd = self.w.obj["handle"]
        self.app = Application(backend="win32").connect(handle=self.hwnd)

        self.dig = self.app.window(handle=self.hwnd)
        # dig.print_control_identifiers()

        if GLOBAL_WIN == "AGENT":
            self.logwin = self.dig.child_window(
                class_name="WindowsForms10.RichEdit20W.app.0.1bb715_r7_ad1"
            )
        else:
            self.logwin = self.dig.child_window(class_name="Edit")

        # result = monitoring(logwin)

    def stop(self):
        self.loop_flag = False

    def run(self):
        edit_control = self.logwin

        print("돌고있나?")

        processing_pattern = re.compile(
            r"\[(?P<dtm>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] 출입 확인 \(이름: (?P<name>.*), 체온: (?P<temper>[0-9.]{5}) 출입시간 : (?P<dtm2>.{19})\)"
        )

        while self.loop_flag:
            line_cnt = edit_control.line_count()
            INFO(f"line_cnt:[{line_cnt}]")

            for i in range(0, line_cnt):
                line = edit_control.get_line(i)
                self.log_processing(processing_pattern, line)
            DEBUG("")
            self.in_processing.emit(line_cnt)
            time.sleep(3)

    def log_processing(self, compiled_pattern, strLog):
        history_mgr = HistoryMgr()
        DEBUG(f"strLog=[{strLog}]")
        # 외부로 이동
        # p = re.compile(r"\[(?P<dtm>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] 출입 확인 \(이름: (?P<name>.*), 체온: (?P<temper>[0-9.]{5}) 출입시간 : (?P<dtm2>.{19})\)")
        p = compiled_pattern
        m = p.match(strLog)

        # DEBUG(f"m          = [{m}]")
        # DEBUG(f"m.group(0) = [{m.group(0)}]")
        # DEBUG(f"m.group(1) = [{m.group(1)}]")
        # DEBUG(f"m.group(2) = [{m.group(2)}]")
        # DEBUG(f"m.group(3) = [{m.group(3)}]")
        # DEBUG(f"m.group(4) = [{m.group(4)}]")

        try:
            DEBUG(f"m.group(dtm)    = [{m.group('dtm')}]")
            DEBUG(f"m.group(name)   = [{m.group('name')}]")
            DEBUG(f"m.group(temper) = [{m.group('temper')}]")
            DEBUG(f"m.group(dtm2)   = [{m.group('dtm2')}]")
        except AttributeError as ae:
            # 파싱 오류
            DEBUG(f"파싱 오류 무시 DB처리 하지 않음 [{ae}]")
            return

        # DB처리 (Cache 검증 및 insert)
        try:
            history_mgr.execute_param(
                history_mgr.INSERT_HISTORY,
                (m.group("dtm"), m.group("name"), m.group("temper"), m.group("dtm2")),
            )
        except sqlite3.IntegrityError as si:
            # Insert 무결성은 무시
            self.dupped.emit(strLog, str(si))
            DEBUG(f"INSERT 무결성은 무시 [{si}]")
        else:
            history_mgr.commit()
            self.inserted.emit(strLog)
            INFO(f"로그등록:[{strLog}]")


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
    import win32com.shell.shell as shell
    import os, sys

    if uac_require():
        INFO("continue")
    else:
        ERROR("error message")
    logCapture = LogCaptureWin32Worker()
    logCapture.run()
    # log_capture_main()
