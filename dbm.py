from sqlite3.dbapi2 import Connection, Cursor, Error
from BKLOG import DEBUG, ERROR, INFO
import sqlite3
from typing import Any, Iterable

class HistoryMgr:
    # SELECT strftime('%Y-%m-%d %H:%M:%S','now') as dtm, strftime('%Y-%m-%d %H:%M:%f','now') as udtm, strftime('%s','now') as unixdtm, date('now') as dt
    def __init__(self, dbconn: Connection=None):
        self.INSERT_HISTORY: str = "INSERT INTO inout_history(dtm, name, temper, dtm2, reg_dtm) values (?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%f','now'))"
        self.dbconn: Connection = dbconn
        if self.dbconn == None:
            self.dbconn = sqlite3.connect("data/log.db")

        self.dbconn.row_factory = self.dic_factory

        #self.cur = self.dbconn.cursor()

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
        try:
            cur: Cursor = self.dbconn.cursor()

            if param != None:
                cur.execute(exec_str, param)
            else:
                cur.execute(exec_str)

            #DEBUG(f"exec result=[{result}]")
            datas: list = cur.fetchall()
            cur.close()
            return datas
        except Error as e:
            raise Error(e)

    def execute(self, exec_str: str) -> list:
        try:
            cursor: Cursor = self.dbconn.execute(exec_str)
            datas: list = cursor.fetchall()
            DEBUG(f"exec data=[{datas}]")
            cursor.close()
            return datas
        except Error as e:
            raise Error(e)

    def query(self, exec_str: str, param: Iterable[Any]=None):
        cur: Cursor = self.dbconn.cursor()

        try:
            if param != None:
                cur.execute(exec_str, param)
            else:
                cur.execute(exec_str)
                #INFO(f"refcnt of dbconn = [{sys.getrefcount(self.dbconn)}]")

            #DEBUG(f"query result=[{result}]")
            rows: list = cur.fetchall()
            cur.close()
            return rows
        except Error as e:
            ERROR(f"SQL ERROR = [{e}]")
            raise Error(e)

    def query_param(self, exec_str: str, param: Iterable[Any]=None):
        cur: Cursor = self.dbconn.cursor()

        try:
            if param != None:
                cur.execute(exec_str, param)
            else:
                cur.execute(exec_str)

            #DEBUG(f"query result=[{result}]")
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
    sql: str = " \n".join((
        "SELECT dtm, name, temper, dtm2, reg_dtm",
        "FROM inout_history",
        "WHERE",
        "name like '%%'",
    ))
    print(f"sql = [{sql}]")

    rows: list = historyDBM.query(sql)
    print(f"rows = [{rows}]")

    #total_page = historyDBM.query_total_page()
    #print(f"total_page = [{total_page}]")
