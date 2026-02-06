# Personal AI Operating System (Personal AI OS)

## Philosophy
This project is a transparent cognitive infrastructure. It externalizes memory, identity, goals, and reasoning into inspectable modules with explicit persistence and audit logging. The system is not a chatbot; it is a kernel with governed state and a visual control room.

## Architecture
- **Kernel (`ai_os/`)**: Memory, identity, goals, reasoning, audit, decay, and CLI orchestration.
- **Multi-agent (`multi_agent/`)**: Coordinator and agent roles that run in a visible pipeline.
- **GUI (`gui/`)**: FastAPI backend and a simple frontend dashboard.
- **Storage (`storage/`)**: JSON state files, audit log, and snapshot checkpoints.

## Safety Rules
- No hidden state; all memory and identity data is stored in JSON.
- Deletions are immediate and audited.
- Audit logging is always enabled.
- Snapshots support rollback to exact previous states.
- Agents cannot override human authority.
- No silent persistence or invisible learning.

## Setup Instructions (Beginner-Friendly)
### 1) Install Python
Download and install Python 3.10+ from https://www.python.org/downloads/.

### 2) Clone the repository
```bash
git clone <your-repo-url>
cd personal-ai-os
```

### 3) Create a virtual environment
```bash
python -m venv venv
```

### 4) Activate the environment
- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```

### 5) Install dependencies
```bash
pip install -r requirements.txt
```

### 6) Create a `.env` file
```bash
cp .env.example .env
```
Add your OpenAI key if you want real model responses:
```
OPENAI_API_KEY=your_key_here
```

## Run Instructions
### Start the GUI backend
```bash
uvicorn gui.backend.server:app --host 0.0.0.0 --port 8000
```

### Open the dashboard
Open `gui/frontend/index.html` in a browser or serve it with a simple server:
```bash
python -m http.server 8001 --directory gui/frontend
```
Then visit `http://localhost:8001`.

### Open the multi-agent control room
Visit `http://localhost:8001/agents.html` to inspect the agent pipeline.

### Run the CLI
```bash
python -m ai_os.main
```

## CLI Commands
- `/remember text`
- `/identity trait`
- `/goal text`
- `/delete memory_id`
- `/show memory`
- `/show goals`
- `/show identity`
- `/snapshot`
- `/rollback snapshot_id`
- `/exit`

## Troubleshooting
- **Port already in use**: Change the port for `uvicorn` or `http.server`.
- **No OpenAI key**: The system returns mock responses without breaking.
- **Missing dependencies**: Re-run `pip install -r requirements.txt`.

## Extension Guide
- Add new modules under `ai_os/` and wire them into `AIOperatingSystem`.
- Add new agents in `multi_agent/agents.py`.
- Extend FastAPI routes in `gui/backend/`.
- Add UI panels in `gui/frontend/`.

This repository is designed to be modular, inspectable, and safe to extend.
