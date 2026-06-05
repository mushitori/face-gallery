# Face Gallery

Offline desktop app to organize photos by person. **Vue 3 + Tauri v2** UI, **FastAPI + InsightFace** Python backend, **SQLite** index. All processing stays on your machine — no cloud uploads.

## Features

- Add local photo folders as libraries and scan them on demand
- Detect faces with InsightFace and cluster them into people
- Browse people and photos with a virtualized grid and lightbox
- FIFO scan queue with progress, history, and safe resume after restarts
- Fully offline after models are installed

## Stack

| Layer | Tech |
|-------|------|
| Desktop shell | Tauri v2 |
| UI | Vue 3, TypeScript, Vite, Pinia |
| API | FastAPI, SQLite |
| ML | InsightFace (`buffalo_l`), ONNX Runtime |

## Prerequisites (Windows)

- [Node.js](https://nodejs.org/) 20+
- [pnpm](https://pnpm.io/) 9+
- [uv](https://docs.astral.sh/uv/) (Python 3.11)
- [Rust](https://rustup.rs/) + MSVC (for Tauri builds only)
- **New terminal** after installing Rust so `cargo` is on `PATH` (`%USERPROFILE%\.cargo\bin`)
- Network access on first API startup (InsightFace `buffalo_l` models download automatically; see [Offline models](#offline-models))

## Project layout

| Path | Role |
|------|------|
| `frontend/` | Vue + TypeScript + Vite UI |
| `backend/` | FastAPI, ML, SQLite (`uv` venv) |
| `src-tauri/` | Tauri shell (spawn sidecar, dialogs) |

## Troubleshooting

**`WinError 10013` or port in use** — Another process is holding the API port. Check with `netstat -ano | findstr :28765`, then stop that PID in Task Manager, or use a different port:

```powershell
$env:FACE_GALLERY_API_PORT = "28766"
.\scripts\dev.ps1
```

Update `frontend/.env` to match: `VITE_API_BASE=http://127.0.0.1:28766`

**Tauri: "Couldn't recognize the current folder"** — Run `pnpm tauri:dev` from `face-gallery/` (repo root), not from `frontend/`.

**`cargo` not found** — Close and reopen PowerShell (or VS Code/Cursor terminal) after `rustup` install.

## Development

### 1. Backend (terminal 1)

```powershell
cd backend
uv sync
.\scripts\dev.ps1
```

API: http://127.0.0.1:28765/docs

### 3. Tauri desktop (terminal 2)

Start the API first, then from the **repo root** (not `frontend/`):

```powershell
pnpm install
pnpm tauri:dev
```

First `pnpm install` in `frontend/` may prompt to allow `esbuild` build scripts — accept, or run `pnpm approve-builds` in `frontend/`.

In **debug** mode, Tauri does not spawn Python; it waits for the API from step 1. No Python `.exe` sidecar is needed for dev.

## Production build (Windows)

```powershell
# 1. Python sidecar
cd backend
.\scripts\build-sidecar.ps1

# 2. Enable sidecar in tauri.conf.json (add under "bundle"):
#    "externalBin": ["binaries/api"]

# 3. UI + installer
cd ..
pnpm install
pnpm build:ui
pnpm tauri:build
```

Output under `src-tauri/target/release/bundle/`.

## Scan queue

- One global worker runs scans **FIFO** (`queued` → `indexing` → `clustering` → `done`/`failed`).
- `POST /libraries/{id}/scan` only enqueues; returns **409** if that library already has a job in `queued`, `indexing`, or `clustering`.
- On API startup, jobs stuck in `indexing`/`clustering` are reset to `queued` and picked up again.
- UI: **Home** (libraries + scan actions), **Scans** (`/scans`) for active job, pending queue, and history.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/jobs/dashboard` | Active + queue + history |
| GET | `/jobs?bucket=active\|queue\|history` | Job lists |
| GET | `/jobs/{id}` | Single job (+ queue position if queued) |
| POST | `/libraries/{id}/scan?force=` | Enqueue scan |

## Smoke test checklist

- [ ] `uv run pytest` in `backend/` passes
- [ ] `GET /health` returns `ok`
- [ ] Add library folder via UI or `POST /libraries`
- [ ] Enqueue two scans (different libraries): one active, one pending on `/scans`
- [ ] Second `POST /scan` on same library while first is queued → 409
- [ ] Restart API during scan: job returns to queue and completes
- [ ] Scan job completes; `GET /persons?library_id=` returns thumbnails
- [ ] Click person; photo grid loads without rescan
- [ ] Quit app; no zombie `python`/`api.exe` (use `POST /shutdown` in prod)

## Configuration

Environment prefix `FACE_GALLERY_`:

| Variable | Default |
|----------|---------|
| `FACE_GALLERY_API_PORT` | `28765` |
| `FACE_GALLERY_MODEL_DIR` | auto (`%LOCALAPPDATA%\FaceGallery\models\buffalo_l\`, or repo bundle if present) |
| `FACE_GALLERY_DBSCAN_EPS` | `0.45` |
| `FACE_GALLERY_SCAN_RESIZE_LONG_EDGE` | `1024` |

Data directory: `%LOCALAPPDATA%\FaceGallery\` (database + thumb cache).

## Offline models

On first API startup, the backend downloads InsightFace `buffalo_l` into `%LOCALAPPDATA%\FaceGallery\models\buffalo_l\` (requires network once). On every restart it verifies required model files are present and re-downloads if any are missing. If download fails, the API exits immediately.

If you see an extra nested `models\models\buffalo_l` folder from an older build, restart the API once — it will move `.onnx` files to the correct location automatically.

For fully offline installs, extract [buffalo_l.zip](https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip) into `backend/models/buffalo_l/` or `%LOCALAPPDATA%\FaceGallery\models\buffalo_l\` before starting the API.


## Third-party models

Face detection uses the InsightFace [`buffalo_l`](https://github.com/deepinsight/insightface) model pack. Download and license terms are provided by the InsightFace project. Model binaries are not included in this repository.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) — free to use, modify, and distribute.
