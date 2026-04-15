import sqlite3

conn = sqlite3.connect('backend/app/skillsprint.db')
cur = conn.cursor()
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS custom_module_progress (
        user_id INTEGER NOT NULL,
        module_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        completed_at DATETIME,
        PRIMARY KEY (user_id, module_id, question_id)
    )
    """
)
conn.commit()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='custom_module_progress'")
print('table:', cur.fetchone())

conn.close()
