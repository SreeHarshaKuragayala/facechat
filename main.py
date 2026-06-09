import cv2
import os
import sys
import time
from config.settings import FACES_DIR, SNAPSHOTS_DIR, REPORTS_DIR

# Safely create all required directories
for folder in [FACES_DIR, SNAPSHOTS_DIR, REPORTS_DIR, "logs/sessions"]:
    try:
        os.makedirs(folder, exist_ok=True)
    except FileExistsError:
        pass

from face.detector import detect_faces
from face.recognizer import encode_face, identify_face
from face.capture import capture_frame, save_face_photo, RandomSnapshotter
from database.models import save_user, create_session, end_session
from chatbot.conversation import ConversationManager
from reports.generator import generate_report


def collect_new_user_info(frame):
    print("\n[👋 New face detected! Let's get your details.]")
    name  = input("Your name  : ").strip()
    age   = input("Your age   : ").strip()
    email = input("Your email : ").strip()
    phone = input("Your phone : ").strip()

    encoding = encode_face(frame)
    if encoding is None:
        print("[⚠️  Could not encode face. Please try again.]")
        return None, None

    photo_path = save_face_photo(frame, name, FACES_DIR)
    user_id = save_user(
        name,
        int(age) if age.isdigit() else 0,
        email, phone, encoding, photo_path
    )
    print(f"[✅ Registered as {name}!]")
    return user_id, name


def run_chat_session(cap, user_id, user_name, is_guest):
    session_id = create_session(
        user_id=user_id,
        is_guest=is_guest,
        guest_name=user_name if is_guest else None
    )
    manager  = ConversationManager(session_id, user_name)
    snapper  = RandomSnapshotter(session_id)

    greeting = manager.greet(is_known=not is_guest, name=user_name)
    print(f"\n[🤖 FaceChat]: {greeting}\n")
    print("(Type 'bye' or 'exit' to end the chat)\n")

    while True:
        ret, frame = cap.read()
        if ret:
            snapper.check_and_snap(frame)
            cv2.imshow("FaceChat - Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        user_input = input("You: ").strip()
        if user_input.lower() in ("bye", "exit", "quit"):
            print("[🤖 FaceChat]: Goodbye! It was great chatting with you. 👋")
            break
        if not user_input:
            continue

        reply = manager.respond(user_input)
        print(f"[🤖 FaceChat]: {reply}\n")

    end_session(session_id)
    report_path, token = generate_report(session_id)
    print(f"\n[📄 Session report generated.]")


def run_user_mode():
    print("=" * 50)
    print("       Welcome to FaceChat 🤖📷")
    print("=" * 50)
    print("Looking for your face... (press Q to quit)\n")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[❌ Camera not found. Check your webcam.]")
        return

    detected_user_id = None
    detected_name    = None
    is_guest         = False
    face_found       = False

    while not face_found:
        frame = capture_frame(cap)
        if frame is None:
            continue

        faces = detect_faces(frame)
        cv2.imshow("FaceChat - Camera", frame)

        if len(faces) > 0:
            encoding = encode_face(frame)
            if encoding is not None:
                match = identify_face(encoding)
                if match:
                    detected_user_id = match["id"]
                    detected_name    = match["name"]
                    is_guest         = False
                    print(f"[✅ Recognised: {detected_name}]")
                else:
                    detected_user_id, detected_name = collect_new_user_info(frame)
                    if detected_user_id is None:
                        continue
                    is_guest = False
                face_found = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return

    run_chat_session(cap, detected_user_id, detected_name, is_guest)
    cap.release()
    cv2.destroyAllWindows()


def startup_menu():
    print("\n" + "=" * 50)
    print("         FaceChat — Startup Menu")
    print("=" * 50)
    print("  [1]  User  — Start face recognition & chat")
    print("  [2]  Admin — Access reports & user data")
    print("  [Q]  Quit")
    print("=" * 50)

    while True:
        choice = input("Select an option: ").strip().lower()
        if choice == "1":
            return "user"
        elif choice == "2":
            return "admin"
        elif choice in ("q", "quit", "exit"):
            return "quit"
        else:
            print("  Please enter 1, 2, or Q.")


def admin_menu():
    from reports.admin import show_reports, show_user_data, regenerate_missing_reports
    print("\n" + "=" * 50)
    print("         FaceChat — Admin Menu")
    print("=" * 50)
    print("  [1]  View session reports")
    print("  [2]  View registered users")
    print("  [3]  Regenerate missing reports")
    print("  [B]  Back")
    print("=" * 50)

    choice = input("Select an option: ").strip().lower()
    if choice == "1":
        show_reports()
    elif choice == "2":
        show_user_data()
    elif choice == "3":
        regenerate_missing_reports()
    else:
        print("Returning to main menu.")


def main():
    # Allow direct CLI flags too: python main.py --admin
    if len(sys.argv) > 1:
        if sys.argv[1] == "--admin":
            admin_menu()
        elif sys.argv[1] == "--user":
            run_user_mode()
        return

    # Interactive startup menu
    role = startup_menu()
    if role == "user":
        run_user_mode()
    elif role == "admin":
        admin_menu()
    elif role == "quit":
        print("Goodbye!")


if __name__ == "__main__":
    main()