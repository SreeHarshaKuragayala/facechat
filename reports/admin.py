import bcrypt
import uuid
import time
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from database.models import get_all_reports
from database.db_connect import run_query
from config.settings import ADMIN_USERNAME, ADMIN_PASSWORD_HASH

console = Console()

# In-memory session store: {token: expiry_timestamp}
_admin_sessions: dict = {}
SESSION_TIMEOUT = 300  # 5 minutes

MAX_ATTEMPTS = 3
_failed_attempts = 0

def _create_session() -> str:
    token = str(uuid.uuid4())
    _admin_sessions[token] = time.time() + SESSION_TIMEOUT
    return token

def _is_valid_session(token: str) -> bool:
    expiry = _admin_sessions.get(token)
    if not expiry:
        return False
    if time.time() > expiry:
        del _admin_sessions[token]
        console.print("[bold red]⏰ Session expired. Please log in again.[/bold red]")
        return False
    # Refresh on activity
    _admin_sessions[token] = time.time() + SESSION_TIMEOUT
    return True

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def admin_login() -> str | None:
    global _failed_attempts
    console.print("\n[bold yellow]🔐 FaceChat Admin Panel[/bold yellow]")
    console.print("[dim]Access restricted. All login attempts are logged.[/dim]\n")

    if _failed_attempts >= MAX_ATTEMPTS:
        console.print("[bold red]🚫 Too many failed attempts. Access locked.[/bold red]")
        return None

    username = input("Username: ").strip()
    password = input("Password: ").strip()  # visible temporarily for debugging

    # Debug output
    print(f"[DEBUG] Entered username: '{username}'")
    print(f"[DEBUG] ADMIN_USERNAME from config: '{ADMIN_USERNAME}'")
    print(f"[DEBUG] Hash loaded: {bool(ADMIN_PASSWORD_HASH)}")
    print(f"[DEBUG] Hash preview: {ADMIN_PASSWORD_HASH[:10] if ADMIN_PASSWORD_HASH else 'EMPTY'}")

    if not ADMIN_PASSWORD_HASH:
        console.print("[bold red]❌ Admin not configured. Run setup first.[/bold red]")
        return None

    import bcrypt
    try:
        match = bcrypt.checkpw(password.encode(), ADMIN_PASSWORD_HASH.encode())
        print(f"[DEBUG] Password match: {match}")
    except Exception as e:
        print(f"[DEBUG] bcrypt error: {e}")
        match = False

    if username == ADMIN_USERNAME and match:
        _failed_attempts = 0
        token = _create_session()
        console.print("[bold green]✅ Access granted.[/bold green]\n")
        return token
    else:
        _failed_attempts += 1
        remaining = MAX_ATTEMPTS - _failed_attempts
        console.print(f"[bold red]❌ Invalid credentials. {remaining} attempt(s) remaining.[/bold red]")
        time.sleep(2)
        return None

def show_reports():
    token = admin_login()
    if not token:
        return

    while True:
        if not _is_valid_session(token):
            return

        reports = get_all_reports()

        console.print("\n[bold cyan]📋 All Session Reports[/bold cyan]")
        table = Table(show_lines=True)
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Session", style="cyan", width=8)
        table.add_column("User", style="green", width=20)
        table.add_column("Generated At", style="yellow", width=22)
        table.add_column("Report File", style="white")

        for r in reports:
            rid, sid, path, gen_at, guest_name, user_name = r
            name = user_name or guest_name or "Unknown"
            # Show only filename, not full path, in the table
            table.add_row(str(rid), str(sid), name, str(gen_at), os.path.basename(path))

        console.print(table)

        console.print("\n[dim]Options: enter Report ID to open | 'refresh' | 'logout'[/dim]")
        choice = Prompt.ask("Action").strip().lower()

        if choice == "logout":
            if token in _admin_sessions:
                del _admin_sessions[token]
            console.print("[yellow]👋 Logged out.[/yellow]")
            return

        elif choice == "refresh":
            continue

        elif choice.isdigit():
            if not _is_valid_session(token):
                return
            row = run_query(
                "SELECT report_path FROM reports WHERE id=%s",
                (int(choice),), fetch=True
            )
            if row:
                path = row[0][0]
                if os.path.exists(path):
                    os.startfile(path)
                    console.print(f"[green]📂 Opening report...[/green]")
                else:
                    console.print(f"[red]❌ File not found: {path}[/red]")
            else:
                console.print("[red]❌ Report ID not found.[/red]")
        else:
            console.print("[red]Invalid option.[/red]")

def show_user_data():
    """View all registered users — admin only"""
    token = admin_login()
    if not token:
        return

    if not _is_valid_session(token):
        return

    rows = run_query(
        "SELECT id, name, age, email, phone, created_at FROM users ORDER BY created_at DESC",
        fetch=True
    )

    table = Table(title="👥 Registered Users", show_lines=True)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Age")
    table.add_column("Email")
    table.add_column("Phone")
    table.add_column("Registered At", style="yellow")

    for r in rows:
        table.add_row(*[str(x) for x in r])

    console.print(table)


def regenerate_missing_reports():
    """Find sessions with no report and regenerate them"""
    rows = run_query("""
        SELECT s.id, u.name, s.guest_name 
        FROM sessions s
        LEFT JOIN users u ON s.user_id = u.id
        LEFT JOIN reports r ON r.session_id = s.id
        WHERE r.id IS NULL AND s.ended_at IS NOT NULL
    """, fetch=True)

    if not rows:
        console.print("[yellow]No missing reports found.[/yellow]")
        return

    console.print(f"[cyan]Found {len(rows)} session(s) without reports. Regenerating...[/cyan]")
    from reports.generator import generate_report
    for session_id, name, guest_name in rows:
        display = name or guest_name or "Unknown"
        console.print(f"  Generating report for session {session_id} ({display})...")
        try:
            path, token = generate_report(session_id)
            console.print(f"  [green]✅ Saved: {path}[/green]")
        except Exception as e:
            console.print(f"  [red]❌ Failed: {e}[/red]")