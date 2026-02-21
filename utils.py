import sqlite3
import pickle
from datetime import datetime

DB_PATH = "database.db"


def init_db():
    """Create the SQLite database and required tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            encoding BLOB NOT NULL
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
        """
    )

    conn.commit()
    conn.close()


def add_student(name: str, encoding) -> bool:
    """Insert a new student into the database.

    The ``encoding`` argument is expected to be a numpy array. It will be
    pickled before being written to the database.
    Returns ``True`` on success or ``False`` if the name already exists.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    blob = pickle.dumps(encoding)
    try:
        c.execute("INSERT INTO students (name, encoding) VALUES (?, ?)", (name, blob))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # name already registered
        return False
    finally:
        conn.close()


def get_students():
    """Return three parallel lists: ``ids``, ``names`` and ``encodings`` of all
    registered students.  Encodings are unpickled back to numpy arrays.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, encoding FROM students")
    rows = c.fetchall()
    conn.close()

    ids = []
    names = []
    encodings = []

    for sid, name, blob in rows:
        ids.append(sid)
        names.append(name)
        encodings.append(pickle.loads(blob))

    return ids, names, encodings


def find_matching_student(encoding, tolerance=0.5):
    """Return the ``(id, name)`` of a student whose encoding matches the given
    vector within ``tolerance``.  If no match is found, ``None`` is returned.

    This is useful for duplicate detection when registering new faces.
    """
    import numpy as np
    ids, names, encodings = get_students()
    if not encodings:
        return None
    # convert lists to numpy array for distance computation
    dists = np.linalg.norm(np.array(encodings) - encoding, axis=1)
    best = np.argmin(dists)
    if dists[best] < tolerance:
        return ids[best], names[best]
    return None


def mark_attendance(student_id: int) -> bool:
    """Record today's attendance for the given ``student_id``.

    If an entry already exists for today the function returns ``False``.  When a
    new row is inserted it returns ``True``.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id FROM attendance WHERE student_id = ? AND date = ?",
        (student_id, today),
    )
    if c.fetchone():
        conn.close()
        return False

    c.execute(
        "INSERT INTO attendance (student_id, date, time) VALUES (?, ?, ?)",
        (student_id, today, now_time),
    )
    conn.commit()
    conn.close()
    return True


def get_attendance_records():
    """Return a list of tuples (attendance_id, name, date, time) sorted by
    date/time so it can be displayed or exported.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT a.id, s.name, a.date, a.time
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date, a.time
        """
    )
    records = c.fetchall()
    conn.close()
    return records
