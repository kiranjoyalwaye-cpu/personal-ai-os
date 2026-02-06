# Personal AI OS Kernel v0.1

## Philosophy
This project is a modular cognitive infrastructure, not a chatbot. It externalizes memory, identity, and goals into inspectable JSON files and keeps the model stateless. All learning is mediated through explicit memory updates and auditable actions.

## Architecture
- **Kernel (`os_kernel.py`)**: Coordinates memory, identity, goals, reasoning, and snapshots.
- **Memory (`memory.py`, `decay.py`)**: Stores memories, applies deterministic decay, and retrieves relevant context.
- **Identity (`identity.py`)**: Tracks evolving user traits with version history.
- **Goals (`goals.py`)**: Persists user-controlled goals across sessions.
- **Reasoning (`reasoner.py`)**: Builds prompts that inject identity, goals, and relevant memory into model requests.
- **Audit (`audit.py`)**: Append-only audit log recording every action.
- **CLI (`main.py`)**: Command interface for operating the kernel.

## Safety Rules
- No hidden state: all state is stored in JSON under `storage/`.
- Deletion is immediate and auditable.
- Audit logging is always on.
- Rollbacks restore exact stored state.
- No model weight changes; learning is memory-driven only.

## Memory Model
Each memory entry contains:
- `id`
- `text`
- `timestamp`
- `emotion_score`
- `importance`
- `last_accessed`

Decay rules:
- Emotional memories decay slower than neutral memories.
- Importance decreases deterministically over time.
- Low-importance memories auto-delete and are audited.

## How to Run
```bash
python -m ai_os.main
```

CLI commands:
- `/remember text`
- `/identity trait`
- `/goal text`
- `/delete memory_id`
- `/show memory|identity|goals`
- `/snapshot`
- `/rollback snapshot_id`
- `/exit`

## How to Extend
- Add new modules and wire them through `AIOperatingSystem`.
- Expand memory scoring in `memory.py` and decay rules in `decay.py`.
- Implement richer reasoning adapters in `reasoner.py`.
- Add tests in `tests/` for any new module.
