from pysqlite2 import dbapi2 as sqlite3
import xbmc

__author__ = 'twinther'

class Database(object):
    def __init__(self):
        self.db_file = xbmc.translatePath('special://masterprofile/Database/MyVideos34.db')

    def fetchall(self, sql, parameters = list()):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite_dict_factory
        c = conn.cursor()
        c.execute(sql, parameters)
        result = c.fetchall()
        conn.close()

        return result

    def fetchone(self, sql, parameters = list()):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite_dict_factory
        c = conn.cursor()
        c.execute(sql, parameters)
        result = c.fetchone()
        conn.close()
        
        return result



def sqlite_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d