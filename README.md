# Face Gallery

Offline desktop app to organize photos by person. **Vue 3 + Tauri v2** UI, **FastAPI + InsightFace** Python backend, **SQLite** index. All processing stays on your machine.

## Prerequisites (Windows)

- [Node.js](https://nodejs.org/) 20+
- [pnpm](https://pnpm.io/) 9+
- [uv](https://docs.astral.sh/uv/) (Python 3.11)
- [Rust](https://rustup.rs/) + MSVC (for Tauri builds only)
- **New terminal** after installing Rust so `cargo` is on `PATH` (`%USERPROFILE%\.cargo\bin`)
- InsightFace `buffalo_l` models in `backend/models/buffalo_l/` (see [backend/models/buffalo_l/.gitkeep](backend/models/buffalo_l/.gitkeep))

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

### 2. Frontend (terminal 2)

```powershell
cd frontend
pnpm install
pnpm dev
```

Open http://localhost:5173 (browser works without Tauri).

### 3. Tauri desktop (terminal 3, optional)

Start the API first, then from the **repo root** (not `frontend/`):

```powershell
cd m:\projects\face-gallery
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

## Smoke test checklist

- [ ] `uv run pytest` in `backend/` passes
- [ ] `GET /health` returns `ok`
- [ ] Add library folder via UI or `POST /libraries`
- [ ] Scan job completes; `GET /persons?library_id=` returns thumbnails
- [ ] Click person; photo grid loads without rescan
- [ ] Quit app; no zombie `python`/`api.exe` (use `POST /shutdown` in prod)

## Configuration

Environment prefix `FACE_GALLERY_`:

| Variable | Default |
|----------|---------|
| `FACE_GALLERY_API_PORT` | `28765` |
| `FACE_GALLERY_DBSCAN_EPS` | `0.45` |
| `FACE_GALLERY_SCAN_RESIZE_LONG_EDGE` | `1024` |

Data directory: `%LOCALAPPDATA%\FaceGallery\` (database + thumb cache).

## Offline models

On first scan, InsightFace may download `buffalo_l` to its cache if models are missing from `backend/models/buffalo_l/`. For fully offline installs, extract the zip into that folder before scanning.

## License

MIT
