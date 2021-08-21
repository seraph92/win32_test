from BKLOG import DEBUG
import sqlite3


class HistoryMgr:
    # SELECT strftime('%Y-%m-%d %H:%M:%S','now') as dtm, strftime('%Y-%m-%d %H:%M:%f','now') as udtm, strftime('%s','now') as unixdtm, date('now') as dt
    def __init__(self, dbconn=None):
        self.INSERT_HISTORY = "INSERT INTO inout_history(dtm, name, temper, dtm2, reg_dtm) values (?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%f','now'))"
        self.dbconn = dbconn
        if self.dbconn == None:
            self.dbconn = sqlite3.connect("data/log.db")

        self.dbconn.row_factory = self.dic_factory

        self.cur = self.dbconn.cursor()

    def dic_factory(self, cursor, row):
        d = {}

        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]

        return d

    # def query_total_page(self, page=20):
    #     sql = f"select count(*) / {page} + case count(*) % {page} when 0 then 0 else 1 END as total_page from inout_history;"
    #     rslt = self.query(sql)

    #     return rslt[0]["total_page"]

    def execute_param(self, exec_str, param):
        if param != None:
            result = self.cur.execute(exec_str, param)
        else:
            result = self.cur.execute(exec_str)

        DEBUG(f"exec result=[{result}]")
        return result

    def execute(self, exec_str):
        result = self.dbconn.execute(exec_str)
        DEBUG(f"exec result=[{result}]")
        return result

    def query(self, exec_str, param=None):
        if param != None:
            cur = self.cur.execute(exec_str, param)
        else:
            cur = self.cur.execute(exec_str)

        DEBUG(f"query result(cur)=[{cur}]")
        rows = cur.fetchall()
        return rows

    def query_param(self, exec_str, param=None):
        if param != None:
            cur = self.cur.execute(exec_str, param)
        else:
            cur = self.cur.execute(exec_str)

        DEBUG(f"query result(cur)=[{cur}]")
        rows = cur.fetchall()
        return rows

    def commit(self):
        self.dbconn.commit()

    def rollback(self):
        self.dbconn.rollback()

    def __del__(self):
        self.cur.close()
        self.dbconn.close()
        DEBUG(f"db Connection Closed!!")


if __name__ == "__main__":
    historyDBM = HistoryMgr()
    sql = "SELECT dtm, name, temper, dtm2, reg_dtm \n"
    sql += "FROM inout_history \n"
    sql += "WHERE \n"
    sql += "name like '%%'"
    print(f"sql = [{sql}]")

    rows = historyDBM.query(sql)
    print(f"rows = [{rows}]")

    total_page = historyDBM.query_total_page()
    print(f"total_page = [{total_page}]")
