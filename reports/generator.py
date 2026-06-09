import os
import uuid
import hashlib
from fpdf import FPDF
from datetime import datetime
from config.settings import REPORTS_DIR
from database.models import save_report, get_user_by_id
from database.db_connect import run_query

try:
    os.makedirs(REPORTS_DIR, exist_ok=True)
except FileExistsError:
    pass

def _secure_filename(session_id: int) -> str:
    """Generate a non-guessable filename using UUID + hash"""
    raw = f"{session_id}-{uuid.uuid4()}-{datetime.now().isoformat()}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()[:24]
    return f"rpt_{hashed}.pdf"

def generate_report(session_id: int):
    session = run_query(
        "SELECT user_id, guest_name, is_guest, started_at, ended_at FROM sessions WHERE id=%s",
        (session_id,), fetch=True
    )
    if not session:
        print("[⚠️ No session found for report]")
        return None, None

    user_id, guest_name, is_guest, started_at, ended_at = session[0]
    user = get_user_by_id(user_id) if user_id else None
    name = user["name"] if user else (guest_name or "Unknown")

    messages = run_query(
        "SELECT role, content, sent_at FROM messages WHERE session_id=%s ORDER BY sent_at",
        (session_id,), fetch=True
    )
    snaps = run_query(
        "SELECT photo_path, taken_at FROM snapshots WHERE session_id=%s",
        (session_id,), fetch=True
    )

    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_fill_color(30, 30, 30)
    pdf.rect(0, 0, 210, 20, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 20, "  FaceChat - Confidential Session Report", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # Watermark text
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(180, 0, 0)
    pdf.cell(0, 5, "CONFIDENTIAL - ADMIN ACCESS ONLY", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    # Session details
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Session Details", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 7, f"Name: {name}", ln=True)
    pdf.cell(0, 7, f"Type: {'Returning User' if not is_guest else 'New/Guest'}", ln=True)
    if user:
        pdf.cell(0, 7, f"Email: {user.get('email', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Phone: {user.get('phone', 'N/A')}", ln=True)
    pdf.cell(0, 7, f"Session Started: {started_at}", ln=True)
    pdf.cell(0, 7, f"Session Ended: {ended_at or 'N/A'}", ln=True)
    pdf.cell(0, 7, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(4)

    # Conversation
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Conversation Log", ln=True)
    pdf.set_font("Arial", size=10)
    for role, content, sent_at in messages:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, f"[{role.upper()}] {sent_at}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, content)
        pdf.ln(1)
    pdf.ln(4)

    # Snapshots
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Snapshots During Session: {len(snaps)}", ln=True)
    for i, (path, taken_at) in enumerate(snaps, 1):
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 6, f"  Snapshot {i} - taken at {taken_at}", ln=True)
        if os.path.exists(path):
            try:
                pdf.image(path, w=70)
                pdf.ln(2)
            except Exception:
                pdf.cell(0, 6, "  [Image could not be embedded]", ln=True)

    # Save with secure filename
    filename = _secure_filename(session_id)
    filepath = os.path.join(REPORTS_DIR, filename)
    pdf.output(filepath)

    access_token = str(uuid.uuid4())
    save_report(session_id, filepath, access_token)
    print(f"[📄 Report saved securely]")
    return filepath, access_token