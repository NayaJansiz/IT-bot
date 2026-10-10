"""
تخزين الإحصائيات (دائم).

- إذا وُجد DATABASE_URL  -> PostgreSQL خارجي (Neon / Supabase ...) والبيانات ما بتنمحي مع Render.
- إذا ما وُجد             -> ملف SQLite محلي stats.db (للتجربة على الكمبيوتر فقط).

كل الدوال متزامنة (sync)؛ البوت بيستدعيها عبر asyncio.to_thread.
"""
import logging
import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone

log = logging.getLogger("qbank.stats")

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
LOCAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.db")
USE_PG = bool(DATABASE_URL)

SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users(
        user_id BIGINT PRIMARY KEY, username TEXT, first_name TEXT,
        first_seen TEXT, last_seen TEXT)""",
    # كل poll أرسله البوت (عشان نعرف أي سؤال انجاب عليه لما توصل الإجابة)
    """CREATE TABLE IF NOT EXISTS poll_map(
        poll_id TEXT PRIMARY KEY, user_id BIGINT, batch_id TEXT, question_key TEXT,
        subject_id INTEGER, subject_name TEXT, year INTEGER, semester INTEGER,
        correct_index INTEGER, sent_at TEXT)""",
    "CREATE INDEX IF NOT EXISTS ix_pm_batch ON poll_map(batch_id)",
    # محاولة = طالب فتح مادة وأخذ كل دفعاتها؛ تنتهي لما يوصل آخر سؤال
    """CREATE TABLE IF NOT EXISTS runs(
        run_id TEXT PRIMARY KEY, user_id BIGINT, subject_id INTEGER, finished_at TEXT)""",
    # إجابات الطلاب
    """CREATE TABLE IF NOT EXISTS answers(
        poll_id TEXT, user_id BIGINT, question_key TEXT,
        subject_id INTEGER, subject_name TEXT, year INTEGER, semester INTEGER,
        chosen INTEGER, is_correct INTEGER, answered_at TEXT,
        PRIMARY KEY (poll_id, user_id))""",
    "CREATE INDEX IF NOT EXISTS ix_ans_user_subj ON answers(user_id, subject_id)",
    # أحداث التصفح: اختيار سنة / فتح مادة / زر التالي
    """CREATE TABLE IF NOT EXISTS events(
        user_id BIGINT, kind TEXT, year INTEGER, semester INTEGER,
        subject_id INTEGER, subject_name TEXT, ts TEXT)""",
]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _q(sql):
    return sql.replace("?", "%s") if USE_PG else sql


_lock = threading.RLock()
_con = None
_ready = False


def _open():
    if USE_PG:
        import psycopg
        return psycopg.connect(DATABASE_URL, autocommit=True, connect_timeout=8,
                               keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=3)
    con = sqlite3.connect(LOCAL_PATH, timeout=10, check_same_thread=False)
    con.isolation_level = None  # autocommit
    return con


def _reset():
    global _con, _ready
    try:
        if _con is not None:
            _con.close()
    except Exception:
        pass
    _con = None
    _ready = False


def _get():
    """اتصال واحد مستمر (بدل فتح اتصال جديد لكل عملية = بطيء). ينشئ الجداول أول مرة."""
    global _con, _ready
    if _con is None:
        _con = _open()
        _ready = False
    if not _ready:
        for s in SCHEMA:
            _con.execute(s)
        old = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat(timespec="seconds")
        _con.execute(_q("DELETE FROM poll_map WHERE sent_at < ?"), (old,))
        _ready = True
        log.info("stats storage ready (%s)", "postgres" if USE_PG else "local sqlite: " + LOCAL_PATH)
    return _con


def _run(fn):
    """ينفّذ عملية على الاتصال المستمر؛ إذا انقطع الاتصال (Neon بينيّم) يعيد المحاولة مرة."""
    with _lock:
        for attempt in (1, 2):
            try:
                return fn(_get())
            except Exception:
                _reset()
                if attempt == 2:
                    raise


def execute(sql, params=()):
    _run(lambda con: con.execute(_q(sql), params))


def executemany(sql, rows):
    def go(con):
        cur = con.cursor()
        cur.executemany(_q(sql), rows)
    _run(go)


def fetch(sql, params=()):
    return _run(lambda con: con.execute(_q(sql), params).fetchall())


def warmup():
    fetch("SELECT 1")


# ---------------------------------------------------------------- كتابة
def touch_user(user_id, username, first_name):
    t = now()
    execute(
        "INSERT INTO users(user_id, username, first_name, first_seen, last_seen) VALUES(?,?,?,?,?) "
        "ON CONFLICT(user_id) DO UPDATE SET last_seen=excluded.last_seen, "
        "username=excluded.username, first_name=excluded.first_name",
        (user_id, username, first_name, t, t))


def log_event(user_id, kind, year=None, semester=None, subject_id=None, subject_name=None):
    execute("INSERT INTO events(user_id, kind, year, semester, subject_id, subject_name, ts) VALUES(?,?,?,?,?,?,?)",
            (user_id, kind, year, semester, subject_id, subject_name, now()))


def save_poll(poll_id, user_id, batch_id, question_key, subject_id, subject_name, year, semester, correct_index):
    execute(
        "INSERT INTO poll_map(poll_id, user_id, batch_id, question_key, subject_id, subject_name, year, semester, "
        "correct_index, sent_at) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(poll_id) DO NOTHING",
        (poll_id, user_id, batch_id, question_key, subject_id, subject_name, year, semester, correct_index, now()))


def save_polls(rows):
    """rows: (poll_id, user_id, batch_id, question_key, subject_id, subject_name, year, semester, correct_index)"""
    t = now()
    executemany(
        "INSERT INTO poll_map(poll_id, user_id, batch_id, question_key, subject_id, subject_name, year, semester, "
        "correct_index, sent_at) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(poll_id) DO NOTHING",
        [tuple(r) + (t,) for r in rows])


def insert_answer(poll_id, user_id, question_key, subject_id, subject_name, year, semester, chosen, correct):
    ok = 1 if chosen == correct else 0
    execute(
        "INSERT INTO answers(poll_id, user_id, question_key, subject_id, subject_name, year, semester, chosen, "
        "is_correct, answered_at) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(poll_id, user_id) DO NOTHING",
        (poll_id, user_id, question_key, subject_id, subject_name, year, semester, chosen, ok, now()))
    return ok


def record_answer(poll_id, user_id, chosen):
    """يسجّل إجابة. يرجع (batch_id, subject_id, is_correct) أو None إذا الـ poll غير معروف."""
    rows = fetch("SELECT batch_id, question_key, subject_id, subject_name, year, semester, correct_index "
                 "FROM poll_map WHERE poll_id=?", (poll_id,))
    if not rows:
        return None
    batch_id, key, sid, sname, year, sem, correct = rows[0]
    ok = 1 if chosen == correct else 0
    execute(
        "INSERT INTO answers(poll_id, user_id, question_key, subject_id, subject_name, year, semester, chosen, "
        "is_correct, answered_at) VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(poll_id, user_id) DO NOTHING",
        (poll_id, user_id, key, sid, sname, year, sem, chosen, ok, now()))
    return batch_id, sid, ok


# ---------------------------------------------------------------- نتيجة الطالب
def finish_run(run_id, user_id, subject_id):
    """يُستدعى بعد إرسال آخر دفعة من المادة."""
    execute("INSERT INTO runs(run_id, user_id, subject_id, finished_at) VALUES(?,?,?,?) "
            "ON CONFLICT(run_id) DO NOTHING", (run_id, user_id, subject_id, now()))


def run_status(user_id, run_id):
    """(انتهى الإرسال؟, عدد أسئلة المحاولة, صح, غلط) باستعلام واحد"""
    r = fetch(
        "SELECT (SELECT COUNT(*) FROM runs WHERE run_id=?), (SELECT COUNT(*) FROM poll_map WHERE batch_id=?), "
        "(SELECT COALESCE(SUM(a.is_correct),0) FROM answers a JOIN poll_map p ON p.poll_id=a.poll_id "
        " WHERE p.batch_id=? AND a.user_id=?), "
        "(SELECT COUNT(*) FROM answers a JOIN poll_map p ON p.poll_id=a.poll_id WHERE p.batch_id=? AND a.user_id=?)",
        (run_id, run_id, run_id, user_id, run_id, user_id))[0]
    fin, total, right, answered = int(r[0]), int(r[1]), int(r[2]), int(r[3])
    return bool(fin), total, right, answered - right


# ---------------------------------------------------------------- قراءة (تحليل الأدمن)
def _pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "-"


def _bar(right, total, n=10):
    """شريط نسبة بالإيموجي (ما بيتأثر باتجاه العربي): 🟩🟩🟩⬜⬜"""
    if not total:
        return "⬜" * n
    g = round(n * right / total)
    return "🟩" * g + "⬜" * (n - g)


def _medal(i):
    return ["🥇", "🥈", "🥉"][i] if i < 3 else "▫️"


def overview():
    """تقرير HTML منسّق لتيليجرام (parse_mode=HTML). كل معلومة بسطر لحالها."""
    from html import escape as e
    week = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(timespec="seconds")
    day = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(timespec="seconds")
    users = fetch("SELECT COUNT(*) FROM users")[0][0]
    u7 = fetch("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (week,))[0][0]
    u1 = fetch("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (day,))[0][0]
    tot = fetch("SELECT COUNT(*), COALESCE(SUM(is_correct),0) FROM answers")[0]
    n, right = int(tot[0]), int(tot[1])
    by_year = fetch("SELECT year, COUNT(*), SUM(is_correct), COUNT(DISTINCT user_id) FROM answers "
                    "GROUP BY year ORDER BY year")
    opens_year = fetch("SELECT year, COUNT(*) FROM events WHERE kind='year' GROUP BY year ORDER BY COUNT(*) DESC")
    top_subj = fetch("SELECT subject_name, year, COUNT(*), SUM(is_correct), COUNT(DISTINCT user_id) FROM answers "
                     "GROUP BY subject_id, subject_name, year ORDER BY COUNT(*) DESC LIMIT 8")
    opens_subj = fetch("SELECT subject_name, year, COUNT(*) FROM events WHERE kind='subject' "
                       "GROUP BY subject_id, subject_name, year ORDER BY COUNT(*) DESC LIMIT 5")
    hardest = fetch("SELECT question_key, subject_name, COUNT(*) n, SUM(is_correct) r FROM answers "
                    "GROUP BY question_key, subject_name HAVING COUNT(*) >= 5 "
                    "ORDER BY (1.0*SUM(is_correct)/COUNT(*)) ASC, COUNT(*) DESC LIMIT 5")

    L = ["📊 <b>إحصائيات البوت</b>", "━━━━━━━━━━━━━━", "",
         "👥 <b>الطلاب</b>",
         f"▫️ المجموع: <b>{users}</b>",
         f"▫️ نشطين آخر 7 أيام: <b>{u7}</b>",
         f"▫️ نشطين آخر 24 ساعة: <b>{u1}</b>", "",
         "📝 <b>الإجابات</b>",
         f"▫️ المجموع: <b>{n}</b>",
         f"✅ صح: <b>{right}</b>",
         f"❌ غلط: <b>{n - right}</b>",
         f"🎯 النسبة العامة: <b>{_pct(right, n)}</b>",
         _bar(right, n)]

    if by_year:
        L += ["", "━━━━━━━━━━━━━━", "📅 <b>حسب السنة</b>"]
        for y, c, r, u in by_year:
            r = int(r or 0)
            L += ["", f"📘 <b>السنة {y}</b>",
                  f"{_bar(r, c)}  <b>{_pct(r, c)}</b>",
                  f"✅ {r}   ❌ {c - r}   (المجموع {c})",
                  f"👤 عدد الطلاب: {u}"]

    if opens_year:
        L += ["", "━━━━━━━━━━━━━━", "👆 <b>أكتر السنوات اختياراً</b>"]
        for i, (y, c) in enumerate(opens_year):
            L.append(f"{_medal(i)} السنة {y} — {c} مرة")

    if top_subj:
        L += ["", "━━━━━━━━━━━━━━", "📚 <b>أكتر المواد حلاً</b>"]
        for i, (name, y, c, r, u) in enumerate(top_subj):
            r = int(r or 0)
            L += ["", f"{_medal(i)} <b>{e(name)}</b> (سنة {y})",
                  f"{_bar(r, c)}  <b>{_pct(r, c)}</b>",
                  f"✅ {r}   ❌ {c - r}   👤 {u} طالب"]

    if opens_subj:
        L += ["", "━━━━━━━━━━━━━━", "🔎 <b>أكتر المواد فتحاً</b>"]
        for i, (name, y, c) in enumerate(opens_subj):
            L.append(f"{_medal(i)} {e(name)} (سنة {y}) — {c} مرة")

    if hardest:
        L += ["", "━━━━━━━━━━━━━━", "⚠️ <b>أصعب الأسئلة</b>",
              "(نسبة صح قليلة، يمكن إجابتها بالبنك غلط، راجعها)"]
        for key, name, c, r in hardest:
            r = int(r or 0)
            L += ["", f"❓ {e(str(key))}", f"المادة: {e(name)}",
                  f"{_bar(r, c)}  <b>{_pct(r, c)}</b> صح من {c} إجابة"]
    text = "\n".join(L)
    return text[:4000]


def export_csv():
    import csv
    import io
    rows = fetch("SELECT a.answered_at, a.user_id, u.username, a.year, a.semester, a.subject_name, a.question_key, "
                 "a.chosen, a.is_correct FROM answers a LEFT JOIN users u ON u.user_id=a.user_id "
                 "ORDER BY a.answered_at")
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["answered_at_utc", "user_id", "username", "year", "semester", "subject", "question_key",
                "chosen_index", "is_correct"])
    w.writerows(rows)
    return ("﻿" + buf.getvalue()).encode("utf-8")  # BOM عشان Excel يقرأ العربي
