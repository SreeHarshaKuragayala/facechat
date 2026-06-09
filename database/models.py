from database.db_connect import run_query
import pickle

# --- USERS ---

def save_user(name, age, email, phone, encoding, photo_path):
    encoding_bytes = pickle.dumps(encoding)
    query = """
        INSERT INTO users (name, age, email, phone, face_encoding, photo_path)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """
    result = run_query(query, (name, age, email, phone, encoding_bytes, photo_path), fetch=True)
    return result[0][0]

def get_all_users_with_encodings():
    rows = run_query("SELECT id, name, face_encoding FROM users", fetch=True)
    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "name": row[1],
            "encoding": pickle.loads(row[2])
        })
    return users

def get_user_by_id(user_id):
    rows = run_query("SELECT id, name, age, email, phone FROM users WHERE id=%s", (user_id,), fetch=True)
    if rows:
        r = rows[0]
        return {"id": r[0], "name": r[1], "age": r[2], "email": r[3], "phone": r[4]}
    return None

# --- SESSIONS ---

def create_session(user_id=None, is_guest=False, guest_name=None):
    query = "INSERT INTO sessions (user_id, is_guest, guest_name) VALUES (%s, %s, %s) RETURNING id"
    result = run_query(query, (user_id, is_guest, guest_name), fetch=True)
    return result[0][0]

def end_session(session_id):
    run_query("UPDATE sessions SET ended_at=NOW() WHERE id=%s", (session_id,))

# --- MESSAGES ---

def save_message(session_id, role, content):
    run_query("INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
              (session_id, role, content))

def get_messages(session_id):
    rows = run_query("SELECT role, content, sent_at FROM messages WHERE session_id=%s ORDER BY sent_at",
                     (session_id,), fetch=True)
    return [{"role": r[0], "content": r[1], "sent_at": r[2]} for r in rows]

# --- SNAPSHOTS ---

def save_snapshot(session_id, photo_path):
    run_query("INSERT INTO snapshots (session_id, photo_path) VALUES (%s, %s)", (session_id, photo_path))

# --- REPORTS ---

def save_report(session_id, report_path, access_token):
    run_query("INSERT INTO reports (session_id, report_path, access_token) VALUES (%s, %s, %s)",
              (session_id, report_path, access_token))

def get_all_reports():
    return run_query("""
        SELECT r.id, r.session_id, r.report_path, r.generated_at,
               s.guest_name, u.name
        FROM reports r
        JOIN sessions s ON r.session_id = s.id
        LEFT JOIN users u ON s.user_id = u.id
        ORDER BY r.generated_at DESC
    """, fetch=True)