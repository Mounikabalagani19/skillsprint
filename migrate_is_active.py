import sqlite3
conn = sqlite3.connect("backend/app/skillsprint.db")
cur = conn.cursor()
cur.execute("PRAGMA table_info(challenges)")
cols = [r[1] for r in cur.fetchall()]
print("Existing columns:", cols)
if "is_active" not in cols:
    cur.execute("ALTER TABLE challenges ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1")
    conn.commit()
    print("Column is_active added successfully.")
else:
    print("Column is_active already exists.")
# Verify
cur.execute("SELECT id, title, is_active FROM challenges LIMIT 5")
print("Sample rows:", cur.fetchall())
conn.close()
