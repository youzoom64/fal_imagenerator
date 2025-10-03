# test/table_structure.py
import sqlite3

conn = sqlite3.connect("C:\\project_root\\app_workspaces\\ncv_special_monitor\\data\\ncv_monitor.db")
cursor = conn.cursor()

tables = ['broadcasts', 'comments', 'special_users', 'ai_analyses']

for table in tables:
    print(f"\n=== {table} テーブル構造 ===")
    cursor.execute(f"PRAGMA table_info({table});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # サンプルデータも表示
    cursor.execute(f"SELECT * FROM {table} LIMIT 1;")
    sample = cursor.fetchone()
    if sample:
        print(f"サンプルデータ: {sample}")

conn.close()