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


YEAR_WORDS = {1: "الأولى", 2: "الثانية", 3: "الثالثة", 4: "الرابعة", 5: "الخامسة"}
SEP = "───────────"


def _bar(right, total, n=10):
    """شريط نسبة بعرض 10: ▰▰▰▱▱▱▱▱▱▱"""
    g = int(n * right / total + 0.5) if total else 0
    return "▰" * g + "▱" * (n - g)


def _plural(n, one, two, few, many):
    """صيغة العدد بالعربي: واحد / اثنان / 3-10 / أكثر"""
    if n == 1:
        return one
    if n == 2:
        return two
    return f"{n} {few if 3 <= n <= 10 else many}"


def _answers(n):
    return _plural(n, "إجابة واحدة", "إجابتان", "إجابات", "إجابة")


def _times(n):
    return _plural(n, "مرة واحدة", "مرتان", "مرات", "مرة")


def _students(n):
    return _plural(n, "طالب واحد", "طالبان", "طلاب", "طالب")


def _year(y):
    return "السنة " + YEAR_WORDS.get(y, str(y))


def overview():
    """تقرير HTML مختصر لتيليجرام (parse_mode=HTML): b / i / code / blockquote فقط."""
    from html import escape as e
    week = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(timespec="seconds")
    day = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(timespec="seconds")
    users = fetch("SELECT COUNT(*) FROM users")[0][0]
    u7 = fetch("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (week,))[0][0]
    u1 = fetch("SELECT COUNT(*) FROM users WHERE last_seen >= ?", (day,))[0][0]
    tot = fetch("SELECT COUNT(*), COALESCE(SUM(is_correct),0) FROM answers")[0]
    n, right = int(tot[0]), int(tot[1])
    by_year = fetch("SELECT year, COUNT(*), SUM(is_correct), COUNT(DISTINCT user_id) FROM answers "
                    "GROUP BY year ORDER BY COUNT(*) DESC")
    opens_year = fetch("SELECT year, COUNT(*) FROM events WHERE kind='year' GROUP BY year ORDER BY COUNT(*) DESC")
    top_subj = fetch("SELECT subject_name, year, COUNT(*), SUM(is_correct), COUNT(DISTINCT user_id) FROM answers "
                     "GROUP BY subject_id, subject_name, year ORDER BY COUNT(*) DESC LIMIT 8")
    opens_subj = fetch("SELECT subject_name, year, COUNT(*) FROM events WHERE kind='subject' "
                       "GROUP BY subject_id, subject_name, year ORDER BY COUNT(*) DESC LIMIT 5")
    hardest = fetch("SELECT question_key, subject_name, COUNT(*) n, SUM(is_correct) r FROM answers "
                    "GROUP BY question_key, subject_name HAVING COUNT(*) >= 5 "
                    "ORDER BY (1.0*SUM(is_correct)/COUNT(*)) ASC, COUNT(*) DESC LIMIT 5")
    # أكتر مادة انفتحت بكل سنة، بعدد الطلاب الفريدين
    uniq_open = fetch("SELECT year, subject_name, COUNT(DISTINCT user_id), COUNT(*) FROM events "
                      "WHERE kind='subject' GROUP BY year, subject_id, subject_name")

    sections = []

    # العنوان + الطلاب + الإجابات
    head = ["📊 <b>إحصائيات البوت</b>", "<i>ملخص استخدام البنك</i>"]
    sections.append("\n".join(head))
    block = ["<b>الطلاب</b>",
             f"{users} طالب · {u7} نشطاء هذا الأسبوع · {u1} خلال 24 ساعة"]
    if n:
        block += ["", "<b>الإجابات</b>",
                  f"{n} إجابة · {right} صحيحة · {n - right} خاطئة",
                  f"{_bar(right, n)}  <b>{_pct(right, n)}</b>"]
    sections.append("\n".join(block))

    # السنوات الخمس مرتبة من الأكتر استخداماً (عدد الإجابات، ثم مرات الاختيار)
    ans = {int(y): (int(c), int(r or 0)) for y, c, r, _u in by_year if y is not None}
    opened = {int(y): int(c) for y, c in opens_year if y is not None}
    best = {}
    for y, name, u, t in uniq_open:
        if y is None:
            continue
        key = (int(u), int(t))
        if int(y) not in best or key > best[int(y)][0]:
            best[int(y)] = (key, name, int(u))
    years = sorted(YEAR_WORDS, key=lambda y: (-ans.get(y, (0, 0))[0], -opened.get(y, 0), y))
    ylines = ["<b>حسب السنة</b>"]
    for i, y in enumerate(years):
        c, r = ans.get(y, (0, 0))
        if i:
            ylines.append("")
        ylines.append(_year(y))
        if c:
            ylines.append(f"{_bar(r, c)}  <b>{_pct(r, c)}</b> · {_answers(c)}")
        else:
            ylines.append("لم تُستخدم بعد")
        if y in best:
            ylines.append(f"الأكثر فتحاً: {e(best[y][1])} · {_students(best[y][2])}")
    sections.append("\n".join(ylines))

    if top_subj:
        L = ["<b>أكثر المواد حلاً</b>"]
        for i, (name, y, c, r, _u) in enumerate(top_subj[:5], 1):
            r = int(r or 0)
            if i > 1:
                L.append("")
            L += [f"{i}. <b>{e(name)}</b> — {_year(y)}",
                  f"{_bar(r, c)}  <b>{_pct(r, c)}</b> · {_answers(c)}"]
        sections.append("\n".join(L))

    if opens_subj:
        L = ["<b>أكثر المواد فتحاً</b>"]
        for i, (name, y, c) in enumerate(opens_subj[:3], 1):
            L.append(f"{i}. {e(name)} · {_times(c)}")
        sections.append("\n".join(L))

    if hardest:
        L = ["<b>أصعب الأسئلة</b>",
             "<blockquote>نسبة الصواب فيها منخفضة، فقد تكون إجابتها في البنك خاطئة. راجعها.</blockquote>"]
        for i, (key, name, c, r) in enumerate(hardest[:3]):
            r = int(r or 0)
            if i:
                L.append("")
            L += [f"{e(name)} · <code>{e(str(key))}</code>",
                  f"{_bar(r, c)}  <b>{_pct(r, c)}</b> · {_answers(c)}"]
        sections.append("\n".join(L))

    return ("\n" + SEP + "\n").join(sections)[:4000]


def reset(include_users=True):
    """يمسح بيانات الإحصائيات (الجداول بتضل موجودة). include_users=False بيحتفظ بقائمة الطلاب."""
    tables = ["answers", "events", "runs", "poll_map"] + (["users"] if include_users else [])

    def go(con):
        for t in tables:
            con.execute(f"DELETE FROM {t}")
    _run(go)
    return True


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
