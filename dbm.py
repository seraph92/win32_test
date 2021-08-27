from sqlite3.dbapi2 import Connection, Cursor, Error
from BKLOG import DEBUG, ERROR, INFO
import sqlite3
from typing import Any, Iterable
import threading

class PoolSingleton:
    # {
    #   'obj': instance
    #   'run': [True|False]
    # }
    __instance: list[dict] = []
    __MAX = 3

    @classmethod
    def __getInstance(cls):
        for instance in cls.__instance:
            if instance['tid'] == threading.get_ident():
                DEBUG(f"현재 thread instance 있음 [{instance}] [{threading.get_ident()}]")
                return instance['obj']
        ERROR(f"instance 없음  th:[{threading.get_ident()}]")
        cls.print_status()
        return None

    @classmethod
    def print_status(cls):
        for i, instance in enumerate(cls.__instance):
            print(f" {i}th pool = [{instance}]")

    @classmethod
    def __getAvailableInstance(cls):
        for instance in cls.__instance:
            if not instance['run']:
                DEBUG(f"가용 instance 있음 [{instance}] [{threading.get_ident()}]")
                # 사용자 thread_id기록
                instance['tid'] = threading.get_ident()
                return instance['obj']
        return None

    @classmethod
    def instance(cls, *args, **kargs):
        # 가용Pool확인
        #instance = cls.__getAvailableInstance()
        instance = cls.__getInstance()

        # 해당 thread에 맞는 Pool이 없다면 추가 slot이 남아 있나?
        if not instance:
            DEBUG(f"가용 instance 없음 [{threading.get_ident()}]")
            # Max 확인
            if len(cls.__instance) < cls.__MAX:
                # Max에 도달되지 않으면 instance생성하여 Pool에 추가
                instance_dict = {
                    "obj": cls(*args, **kargs),
                    "tid": threading.get_ident(),
                    "run": True,
                }

                cls.__instance.append(instance_dict)
                INFO(f"instance 추가 [{threading.get_ident()}]")
                #cls.instance = cls.__getInstance
                return instance_dict['obj']
            else:
                # 가용Pool도 없고 추가 slot도 없으면, Error 발생
                raise Error("가용Pool이 남아 있지 않습니다.")
        
        return instance

class DBPool(PoolSingleton):
    def __init__(self):
        self.db_path = "data/log.db"
        self.dbconn = sqlite3.connect(self.db_path)

class DBMgr(PoolSingleton):
    def __init__(self):
        self.INSERT_HISTORY: str = "INSERT INTO inout_history(dtm, name, temper, dtm2, reg_dtm) values (?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%f','now'))"
        self.db_path = "data/log.db"
        self.dbconn = sqlite3.connect(self.db_path)
        self.dbconn.row_factory = self.dic_factory

    def __enter__(self):
        return self.dbconn

    def __exit__(self, type, value, traceback):
        #INFO(f"[자원반납] 지금은 할게 없음")
        pass
        #self.dbconn.close()
        # INFO(f"[자원반납]db Connection Closed!!")

    def dic_factory(self, cursor, row) -> dict:
        d: dict = {}

        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]

        return d

    def execute_param(self, exec_str: str, param: Iterable[Any]) -> list:
        cur: Cursor = self.dbconn.cursor()
        try:
            if param != None:
                cur.execute(exec_str, param)
            else:
                cur.execute(exec_str)
            datas: list = cur.fetchall()
            return datas
        finally:
            cur.close()

    def execute(self, exec_str: str) -> list:
        cursor: Cursor = self.dbconn.execute(exec_str)
        try:
            datas: list = cursor.fetchall()
            DEBUG(f"exec data=[{datas}]")
            return datas
        finally:
            cursor.close()

    def query(self, exec_str: str, param: Iterable[Any] = None):
        cur: Cursor = self.dbconn.cursor()
        try:
            if param != None:
                cur.execute(exec_str, param)
            else:
                cur.execute(exec_str)
                # INFO(f"refcnt of dbconn = [{sys.getrefcount(self.dbconn)}]")

            # DEBUG(f"query result=[{result}]")
            rows: list = cur.fetchall()
            return rows
        finally:
            cur.close()

    def query_param(self, exec_str: str, param: Iterable[Any] = None):
        cur: Cursor = self.dbconn.cursor()
        try:
            if param != None:
                cur.execute(exec_str, param)
            else:
                cur.execute(exec_str)

            # DEBUG(f"query result=[{result}]")
            rows = cur.fetchall()
            return rows
        finally:
            cur.close()

    def commit(self):
        self.dbconn.commit()

    def rollback(self):
        self.dbconn.rollback()

    def __del__(self):
        self.dbconn.close()
        INFO(f"[자원반납]객체 반납!!")


class HistoryMgr:
    # SELECT strftime('%Y-%m-%d %H:%M:%S','now') as dtm, strftime('%Y-%m-%d %H:%M:%f','now') as udtm, strftime('%s','now') as unixdtm, date('now') as dt
    # def __init__(self, dbconn: Connection = None):
    def __init__(self):
        self.INSERT_HISTORY: str = "INSERT INTO inout_history(dtm, name, temper, dtm2, reg_dtm) values (?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%f','now'))"
        self.dbconn = sqlite3.connect("data/log.db")
        self.dbconn.row_factory = self.dic_factory

        # self.cur = self.dbconn.cursor()

    def __enter__(self):
        return self.dbconn

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.dbconn.close()

    def dic_factory(self, cursor, row) -> dict:
        d: dict = {}

        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]

        return d

    # def query_total_page(self, page=20):
    #     sql = f"select count(*) / {page} + case count(*) % {page} when 0 then 0 else 1 END as total_page from inout_history;"
    #     rslt = self.query(sql)

    #     return rslt[0]["total_page"]

    def execute_param(self, exec_str: str, param: Iterable[Any]) -> list:
        cur: Cursor = self.dbconn.cursor()

        if param != None:
            cur.execute(exec_str, param)
        else:
            cur.execute(exec_str)

        # DEBUG(f"exec result=[{result}]")
        datas: list = cur.fetchall()
        cur.close()
        return datas

    def execute(self, exec_str: str) -> list:
        try:
            cursor: Cursor = self.dbconn.execute(exec_str)
            datas: list = cursor.fetchall()
            DEBUG(f"exec data=[{datas}]")
            cursor.close()
            return datas
        except Error as e:
            raise Error(e)

    def query(self, exec_str: str, param: Iterable[Any] = None):
        cur: Cursor = self.dbconn.cursor()

        try:
            if param != None:
                cur.execute(exec_str, param)
            else:
                cur.execute(exec_str)
                # INFO(f"refcnt of dbconn = [{sys.getrefcount(self.dbconn)}]")

            # DEBUG(f"query result=[{result}]")
            rows: list = cur.fetchall()
            cur.close()
            return rows
        except Error as e:
            ERROR(f"SQL ERROR = [{e}]")
            raise Error(e)

    def query_param(self, exec_str: str, param: Iterable[Any] = None):
        cur: Cursor = self.dbconn.cursor()

        try:
            if param != None:
                cur.execute(exec_str, param)
            else:
                cur.execute(exec_str)

            # DEBUG(f"query result=[{result}]")
            rows = cur.fetchall()
            return rows
        except Error as e:
            ERROR(f"SQL ERROR = [{e}]")
            raise Error(e)

    def commit(self):
        self.dbconn.commit()

    def rollback(self):
        self.dbconn.rollback()

    def __del__(self):
        self.dbconn.close()
        INFO(f"[자원반납]db Connection Closed!!")


if __name__ == "__main__":
    historyDBM = HistoryMgr()
    sql: str = " \n".join(
        (
            "SELECT dtm, name, temper, dtm2, reg_dtm",
            "FROM inout_history",
            "WHERE",
            "name like '%%'",
        )
    )
    print(f"sql = [{sql}]")

    rows: list = historyDBM.query(sql)
    print(f"rows = [{rows}]")

    d1 = DBPool.instance()
    d2 = DBPool.instance()
    del d1
    del d2
    # total_page = historyDBM.query_total_page()
    # print(f"total_page = [{total_page}]")
