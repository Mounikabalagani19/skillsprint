import requests
import sqlite3

base = "http://localhost:8000/api/v1"

candidates = [
    ("lalithsai@gmail.com", "Lalith@123"),
    ("lalithsai@gmail.com", "12345678"),
    ("Lalith Sai", "12345678"),
    ("Lalith Sai", "Lalith@123"),
]

token = None
for u, p in candidates:
    r = requests.post(base + "/users/token", data={"username": u, "password": p}, timeout=5)
    if r.status_code == 200:
        token = r.json().get("access_token")
        print("login ok", u)
        break

print("token?", bool(token))
if not token:
    raise SystemExit(0)

headers = {"Authorization": f"Bearer {token}"}

m = requests.get(base + "/modules/custom/1", headers=headers, timeout=5)
print("module status", m.status_code)
if m.status_code != 200:
    print(m.text)
    raise SystemExit(0)

data = m.json()
if not data.get("questions"):
    print("No questions found")
    raise SystemExit(0)

q = data["questions"][0]

conn = sqlite3.connect("d:/skillsprint/backend/app/skillsprint.db")
cur = conn.cursor()
cur.execute("SELECT correct_answer FROM custom_module_questions WHERE id=?", (q["id"],))
row = cur.fetchone()
conn.close()
if not row:
    print("No DB answer found")
    raise SystemExit(0)
ans = row[0]

me_before = requests.get(base + "/users/me", headers=headers, timeout=5).json()
print("before", me_before["xp"], me_before["streak"])

s = requests.post(base + "/modules/custom/1/submit", headers=headers, json={"id": q["id"], "answer": ans}, timeout=5)
print("submit", s.status_code, s.text)

me_after = requests.get(base + "/users/me", headers=headers, timeout=5).json()
print("after", me_after["xp"], me_after["streak"])
