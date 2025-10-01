import pyodbc
from config import Config


class Database:
    def __init__(self):
        self.connection_string = Config.DB_CONNECTION_STRING

    def get_connection(self):
        """獲取數據庫連接"""
        try:
            conn = pyodbc.connect(self.connection_string)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """執行查詢並返回結果"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch_one:
                result = cursor.fetchone()
                return self._row_to_dict(cursor, result) if result else None
            elif fetch_all:
                results = cursor.fetchall()
                return [self._row_to_dict(cursor, row) for row in results]
            else:
                conn.commit()
                return cursor.rowcount

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Query execution error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def execute_insert(self, query, params=None):
        """執行 INSERT 並返回新插入的 ID"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # 獲取新插入的 ID
            cursor.execute("SELECT @@IDENTITY AS id")
            result = cursor.fetchone()
            new_id = result[0] if result else None

            conn.commit()
            return new_id

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Insert execution error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def _row_to_dict(cursor, row):
        """將數據庫行轉換為字典"""
        if not row:
            return None
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))


# 創建全局數據庫實例
db = Database()
