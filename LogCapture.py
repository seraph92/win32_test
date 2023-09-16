from MemTrace import MemTrace
from PyQt5.QtCore import QObject, pyqtSignal

import sys
import warnings

warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

# from pywinauto.application import Application

# import pywinauto
import time
import re
import sqlite3

from DBM import DBMgr
from BKLOG import DEBUG, INFO, ERROR

from WindowsObject import WindowsObject, ChildObject
from Config import CONFIG

GLOBAL_WIN = "AGENT"
#GLOBAL_WIN = "EDIT"


class LogCaptureWin32Worker(QObject):
    started = pyqtSignal()
    running = pyqtSignal()
    finished = pyqtSignal()
    inserted = pyqtSignal(str)
    dupped = pyqtSignal(str, str)
    in_processing = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.loop_flag = True

        try:
            if GLOBAL_WIN == "AGENT":
                # self.w = WindowsObject("KRC-EC100 에이전트 v1.2.5.0 학원번호 : test - [  ]")
                # self.w = WindowsObject(
                #     r"KRC-EC100 에이전트 v[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ 학원번호 : .* - \[.*\]"
                # )
                self.w = WindowsObject(
                    r"KRC-EC100 에이전트*"
                )
            else:
                self.w = WindowsObject(r".*sample.txt - Windows 메모장")

            DEBUG(f"w={self.w.win_objs}")
            DEBUG(
                "w.handle,text=[%08X][%s]" % (self.w.obj["handle"], self.w.obj["text"])
            )

            self.hwnd = self.w.obj["handle"]
            if GLOBAL_WIN == "AGENT":
                self.logwin = ChildObject(self.hwnd, CONFIG["class_name"])
            else:
                self.logwin = ChildObject(self.hwnd, r"Edit")

        except ValueError as ve:
            self.loop_flag = False
            ERROR(f"Log Capture 생성 오류 [{ve}]")

    def stop(self):
        self.loop_flag = False

    def run(self):
        self.running.emit()
        processing_pattern = re.compile(
            r"\[(?P<dtm>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] 출입 확인 \(이름: (?P<name>.*), 체온: (?P<temper>[0-9.]{3,5}) 출입시간 : (?P<dtm2>.{19})\)"
        )

        if self.loop_flag:
            edit_control = self.logwin

        # mt = MemTrace()

        while self.loop_flag:
            line_cnt = edit_control.line_count()
            INFO(f"line_cnt:[{line_cnt}]")

            for i in range(0, line_cnt):
                line = edit_control.get_line(i)
                self.log_processing(processing_pattern, line)
            DEBUG("")
            self.in_processing.emit(line_cnt)
            time.sleep(3)
            # mt.end_print(5)
            # mt.print_mem_trace()

        self.finished.emit()

    def log_processing(self, compiled_pattern, strLog):
        dbm = DBMgr.instance()
        DEBUG(f"strLog=[{strLog}]")
        # 외부로 이동
        # p = re.compile(r"\[(?P<dtm>[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\] 출입 확인 \(이름: (?P<name>.*), 체온: (?P<temper>[0-9.]{5}) 출입시간 : (?P<dtm2>.{19})\)")
        p = compiled_pattern
        m = p.match(strLog)

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
        # 등록하려는 정보의 앞뒤 1기간 가량안에 동일 사용자의 로그가 있다면 등록하지 않고 무시
        sql = " \n".join(
            (
                f"SELECT count(*) cnt",
                f"FROM inout_history a",
                f"WHERE",
                f"name = '{m.group('name')}'",
                f"and datetime(a.dtm) BETWEEN datetime('{m.group('dtm')}', '-1 hours') and datetime('{m.group('dtm')}', '+1 hours')",
            )
        )

        with dbm as conn:
            datas = dbm.query(sql)

        dup_cnt = datas[0]["cnt"]

        if dup_cnt:
            DEBUG(f"sql = [{sql}]")
            DEBUG(f"datas = [{datas}]")
            DEBUG(f"dup_cnt = [{dup_cnt}][{type(dup_cnt)}]")

        if not dup_cnt:
            with dbm as conn:
                try:
                    dbm.execute_param(
                        dbm.INSERT_HISTORY,
                        (
                            m.group("dtm"),
                            m.group("name"),
                            m.group("temper"),
                            m.group("dtm2"),
                        ),
                    )
                except sqlite3.IntegrityError as si:
                    # Insert 무결성은 무시
                    self.dupped.emit(strLog, str(si))
                    conn.rollback()
                    DEBUG(f"INSERT 무결성은 무시 [{si}]")
                else:
                    conn.commit()
                    self.inserted.emit(strLog)
                    INFO(f"로그등록:[{strLog}]")
        # history_mgr.close()
        # del history_mgr


if __name__ == "__main__":
    logCapture = LogCaptureWin32Worker()
    logCapture.run()
    # log_capture_main()
