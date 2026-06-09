# FaceChat 🤖📷
### AI-Powered Face Recognition Chatbot with Secure Session Reporting

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-green?style=for-the-badge&logo=opencv&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-LLaMA3-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**A fully offline, privacy-first AI assistant that recognises your face, remembers who you are, chats intelligently, and generates secure session reports - all running locally on your machine.**

[Features](#-features) • [Demo](#-demo) • [Tech Stack](#-tech-stack) • [Architecture](#-architecture) • [Setup](#-setup) • [Usage](#-usage) • [Security](#-security)

</div>

---

## 🎯 What is FaceChat?

FaceChat is an end-to-end AI application that combines **computer vision**, **natural language processing**, and **secure data management** into a single cohesive system.

When you launch it, the app opens your camera and scans for a face. If it recognises you from the database, it greets you by name and starts a personalised conversation. If you're new, it registers your face and details on the spot. Throughout the chat, it randomly takes snapshots, logs every message, and generates a locked-down PDF report that only an admin can access.

> Built entirely from scratch - no cloud APIs, no external AI services. Everything runs on your local machine.

---

## ✨ Features

### 👤 Face Recognition
- Real-time face detection using OpenCV
- Face encoding and matching with the `face_recognition` library (dlib under the hood)
- Automatic new user registration with photo capture
- Returning user identification with personalised greeting

### 🤖 AI Chatbot (100% Offline)
- Powered by **Ollama + LLaMA 3** running locally - no internet required
- Full conversation memory within each session
- Context-aware responses - knows your name, remembers what you said
- Natural, human-like conversation flow

### 📸 Passive Monitoring
- Random snapshots taken silently during conversations
- Configurable interval (default: every 30–90 seconds)
- All snapshots stored securely outside the project directory

### 📄 Session Reports
- Auto-generated PDF report at the end of every session
- Includes: user profile, full conversation log, embedded snapshots, timestamps
- Reports saved with SHA-256 hashed filenames (non-guessable)
- Watermarked as **CONFIDENTIAL**

### 🔐 Admin Security Layer
- Separate admin login with bcrypt-hashed password
- 3-attempt lockout with 2-second delay (brute force protection)
- UUID session tokens with 5-minute auto-expiry
- Admin-only access to reports, user data, and session history

### 🗄️ Database
- Full PostgreSQL backend with relational schema
- Stores users, sessions, messages, snapshots, and reports
- Role-based DB users (app user vs admin user)

---

## 🎬 Demo

```
==================================================
         FaceChat - Startup Menu
==================================================
  [1]  User  - Start face recognition & chat
  [2]  Admin - Access reports & user data
  [Q]  Quit
==================================================

[✅ Recognised: Sree Harsha Kuragayala]

[🤖 FaceChat]: Hi Sree Harsha! Great to see you again!
               How's your day going?

You: I'm feeling really excited today!

[🤖 FaceChat]: That's wonderful! What's got you feeling
               so thrilled? I'd love to hear about it!

[📸 Snapshot saved silently...]

You: bye

[🤖 FaceChat]: Goodbye! It was great chatting with you 👋
[📄 Confidential session report generated.]
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | Python 3.11 | Core application |
| **Face Detection** | OpenCV 4.9 | Real-time camera & face detection |
| **Face Recognition** | face_recognition + dlib | Face encoding & matching |
| **AI / LLM** | Ollama + LLaMA 3 | Offline conversational AI |
| **Database** | PostgreSQL 16 | Persistent data storage |
| **DB Driver** | psycopg2 | Python-PostgreSQL bridge |
| **PDF Generation** | FPDF2 | Secure session report creation |
| **Security** | bcrypt | Password hashing |
| **Terminal UI** | Rich | Beautiful admin panel tables |
| **Config** | python-dotenv | Environment variable management |

---

## 🏗 Architecture

```
facechat/
│
├── main.py                    # Entry point + startup menu
│
├── config/
│   └── settings.py            # Centralised config from .env
│
├── database/
│   ├── db_connect.py          # PostgreSQL connection handler
│   ├── models.py              # All DB queries (users, sessions, reports)
│   └── migrations/
│       └── init.sql           # Database schema
│
├── face/
│   ├── detector.py            # OpenCV face detection
│   ├── recognizer.py          # Face encoding + identity matching
│   └── capture.py             # Camera management + random snapshots
│
├── chatbot/
│   ├── ollama_client.py       # Ollama API wrapper
│   └── conversation.py        # Session manager + message history
│
├── reports/
│   ├── generator.py           # PDF report builder
│   └── admin.py               # Secured admin panel
│
└── assets/                    # (gitignored) faces, snapshots, reports
```

### Data Flow

```
Camera Input
    │
    ▼
Face Detection (OpenCV)
    │
    ├── Known Face ──► Greet by name ──► Start Chat Session
    │
    └── Unknown Face ──► Collect Details ──► Register ──► Start Chat Session
                                                │
                                                ▼
                                        Random Snapshots (background)
                                                │
                                                ▼
                                        End Session ──► Generate PDF Report
                                                              │
                                                              ▼
                                                    Stored in Secure Folder
                                                    (Admin access only)
```

---

## ⚙️ Setup

### Prerequisites

| Requirement | Version | Link |
|-------------|---------|------|
| Python | 3.11.x | [python.org](https://python.org) |
| PostgreSQL | 14+ | [postgresql.org](https://postgresql.org) |
| Ollama | Latest | [ollama.com](https://ollama.com) |
| CMake | 3.x | [cmake.org](https://cmake.org) |
| VS C++ Build Tools | 2022 | [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/SreeHarshaKuragayala/facechat.git
cd facechat
```

**2. Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
```

**3. Install dlib (Windows - use pre-built wheel)**
```bash
pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.1-cp311-cp311-win_amd64.whl
```

**4. Install all dependencies**
```bash
pip install -r requirements.txt
```

**5. Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

**6. Set up PostgreSQL**
```sql
CREATE USER facechat_user WITH PASSWORD 'your_password';
CREATE DATABASE facechat_db OWNER facechat_user;
GRANT ALL PRIVILEGES ON DATABASE facechat_db TO facechat_user;
```
```bash
psql -U facechat_user -d facechat_db -f database/migrations/init.sql
```

**7. Pull the LLaMA 3 model**
```bash
ollama pull llama3
```

**8. Generate admin password hash**
```bash
python -c "import bcrypt; print(bcrypt.hashpw('yourpassword'.encode(), bcrypt.gensalt()).decode())"
# Paste output into .env → ADMIN_PASSWORD_HASH=...
```

**9. Create secure storage directories**
```bash
mkdir C:\facechat_secure\faces
mkdir C:\facechat_secure\snapshots
mkdir C:\facechat_secure\reports
```

**10. Run**
```bash
python main.py
```

---

## 🚀 Usage

### User Mode
```bash
python main.py
# Select [1] - camera opens, face is detected/registered, chat begins
```

### Admin Mode
```bash
python main.py
# Select [2] - enter admin credentials to access reports and user data

# Or directly via CLI:
python main.py --admin
python main.py --users
```

### Admin Panel Options
```
[1]  View session reports     → lists all PDFs, enter ID to open
[2]  View registered users    → full user table
[3]  Regenerate missing reports
[B]  Back
```

---

## 🔐 Security

FaceChat is built with a **security-first mindset**:

| Layer | Implementation |
|-------|---------------|
| **Passwords** | bcrypt hashing with salt - never stored in plain text |
| **Admin login** | 3-attempt lockout + 2s delay to prevent brute force |
| **Session tokens** | UUID-based with 5-minute auto-expiry |
| **Report filenames** | SHA-256 hashed - non-guessable, non-sequential |
| **File storage** | Stored outside project directory with Windows ACL |
| **PDF watermark** | Every report marked CONFIDENTIAL |
| **Secrets** | All credentials in `.env`, never committed to Git |
| **DB users** | Separate app user and admin user with restricted privileges |
| **Git** | `.env`, assets, reports all in `.gitignore` |

---

## 🗃 Database Schema

```sql
users        - id, name, age, email, phone, face_encoding, photo_path
sessions     - id, user_id, started_at, ended_at, is_guest
messages     - id, session_id, role, content, sent_at
snapshots    - id, session_id, photo_path, taken_at
reports      - id, session_id, report_path, access_token, generated_at
admins       - id, username, password_hash
```

---

## 🧠 Skills Demonstrated

This project showcases a range of real-world engineering skills:

- **Computer Vision** - real-time face detection and recognition pipeline
- **Machine Learning** - face encoding vectors, similarity matching with tolerance thresholds
- **LLM Integration** - local LLM orchestration with conversation context management
- **Backend Development** - PostgreSQL schema design, parameterised queries, connection pooling pattern
- **Security Engineering** - bcrypt, session tokens, access control, file system permissions
- **System Design** - modular architecture, separation of concerns, config management
- **PDF Generation** - dynamic document creation with images and structured data
- **Python Best Practices** - virtual environments, `.env` config, type hints, error handling

---

## 📋 Requirements

```txt
opencv-python==4.9.0.80
face-recognition==1.3.0
dlib==19.24.1
numpy==1.26.4
Pillow==10.3.0
psycopg2-binary==2.9.9
python-dotenv==1.0.1
ollama==0.2.1
reportlab==4.1.0
fpdf2==2.7.9
rich==13.7.1
bcrypt==4.1.3
```

---

## 🗺 Roadmap

- [ ] Web dashboard for admin panel (Flask/FastAPI)
- [ ] Email notification when report is generated
- [ ] Multi-camera support
- [ ] Face mask detection
- [ ] Export reports to CSV
- [ ] Docker containerisation
- [ ] REST API for remote access

---

## 👨‍💻 Author

**Sree Harsha Kuragayala**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/SreeHarshaKuragayala)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sree-harsha-kuragayala-95782b230/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**If you found this project interesting, please consider giving it a ⭐**

*Built with Python, powered by local AI, secured end-to-end.*

</div>