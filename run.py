import sys
import subprocess

def check_dependencies():
    required = ["fastapi", "uvicorn", "websockets", "jwt", "bcrypt"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[*] Missing dependencies: {missing}. Installing from taskflow_requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "taskflow_requirements.txt"])

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def main():
    check_dependencies()

    # Initialize SQLite database and seed initial demo data
    from taskflow.backend.database import init_db
    print("[*] Initializing TaskFlow database and demo workspace...")
    init_db()

    banner = """
======================================================================
  ⚡ TaskFlow — Collaborative Project Management Tool
======================================================================
  Web App URL:   http://localhost:8000
  API Docs:      http://localhost:8000/docs
  WebSocket:     ws://localhost:8000/ws/projects/{id}

  Demo Personas (Collaborative Testing):
  --------------------------------------------------
  1. Alice Johnson    (PM Lead)     - alice / password123
  2. Bob Smith        (Frontend)    - bob / password123
  3. Charlie Davis    (UI/UX)       - charlie / password123
  4. Diana Prince     (Backend)     - diana / password123

  💡 Tip: Open two browser tabs side-by-side to watch cards move,
         comments post, and notifications fire in real-time!
======================================================================
    """
    print(banner)

    import uvicorn
    uvicorn.run("taskflow.backend.app:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    main()
