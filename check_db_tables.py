import sqlite3, os, glob
hits = glob.glob("**/*.db", recursive=True)
if not hits:
    print("No .db file found")
else:
    conn = sqlite3.connect(hits[0])
    tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("DB:", hits[0])
    print("Tables:", tables)
    conn.close()
