import sqlite3
from datetime import datetime

class GalleryDB:
    def __init__(self, db_name="gallery.db"):
        # check_same_thread=False 是为了配合 Streamlit 使用
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            file_path TEXT,
            created_at TEXT
        )
        '''
        self.cursor.execute(sql)
        self.conn.commit()

    def add_record(self, prompt, file_path):
        """存入一条新记录"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO history (prompt, file_path, created_at) VALUES (?, ?, ?)"
        # 使用 ? 占位符防止注入攻击
        print(sql)
        self.cursor.execute(sql, (prompt, file_path, current_time))
        self.conn.commit()
        print(f"💾 管家汇报：已归档 {prompt}")

    def get_all_records(self):
        """取出所有记录"""
        sql = "SELECT * FROM history ORDER BY id DESC"
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    def search_records(self, keyword):
        # SQL 进阶咒语：WHERE ... LIKE ...
        sql = "SELECT * FROM history WHERE prompt LIKE ? ORDER BY id DESC"
        search_term = f"%{keyword}%"
        self.cursor.execute(sql, (search_term,))
        return self.cursor.fetchall()
    def close(self):
        self.conn.close()