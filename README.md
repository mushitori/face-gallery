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

## Build Windows installer from source

Complete steps after cloning the repo. All commands assume **PowerShell** and that you run `pnpm` commands from the **repo root** (`face-gallery/`), not from `frontend/`.

### 1. Install prerequisites

Install these once on your build machine:

| Tool | Purpose | Install |
|------|---------|---------|
| Node.js 20+ | Frontend + Tauri CLI | [nodejs.org](https://nodejs.org/) |
| pnpm 9+ | JS package manager | [pnpm.io](https://pnpm.io/installation) |
| uv | Python 3.11 + backend deps | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |
| Rust + MSVC | Tauri desktop shell | [rustup.rs](https://rustup.rs/) (select **Desktop development with C++** in Visual Studio Build Tools if prompted) |

Close and reopen your terminal after installing Rust so `cargo` is on `PATH` (`%USERPROFILE%\.cargo\bin`).

### 2. Clone and enter the repo

```powershell
git clone https://github.com/mushitori/face-gallery.git
cd face-gallery
```

### 3. Install JavaScript dependencies

```powershell
pnpm install
```

If prompted about `esbuild` build scripts, accept the prompt or run `pnpm approve-builds` inside `frontend/`.

### 4. Install Python dependencies

```powershell
cd backend
uv sync
cd ..
```

### 5. Build the Python API sidecar

The release app bundles the FastAPI backend as a standalone `.exe` (users do not need Python installed).

```powershell
cd backend
.\scripts\build-sidecar.ps1
cd ..
```

This creates:

`src-tauri/binaries/api-x86_64-pc-windows-msvc.exe`

The repo already configures Tauri to bundle it via `"externalBin": ["binaries/api"]` in [`src-tauri/tauri.conf.json`](src-tauri/tauri.conf.json). You do **not** need to edit that file unless you change the sidecar name or path.

### 6. Build the Windows installer

```powershell
pnpm tauri:build
```

This command:

1. Builds the Vue UI into `frontend/dist/` (via `beforeBuildCommand` in Tauri config)
2. Compiles the Rust app in release mode
3. Bundles the UI, Tauri shell, and Python sidecar into a Windows installer

The first build can take several minutes while Rust compiles dependencies.

### 7. Find the output

Installers and bundles are written to:

`src-tauri/target/release/bundle/`

Typical artifacts:

| File | Description |
|------|-------------|
| `*.msi` | Windows installer (recommended for distribution) |
| `*.exe` | NSIS-style setup (if generated for your target) |

Run the `.msi` on any Windows PC to install Face Gallery. The installed app does not require Python, Node, or Rust on the target machine.

### 8. First run on an installed app

- **WebView2** — Windows 10/11 usually has it; if the app fails to open, install the [Microsoft Edge WebView2 Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/).
- **Face models** — On first launch, the bundled API downloads InsightFace `buffalo_l` to `%LOCALAPPDATA%\FaceGallery\models\buffalo_l\` (network required once). See [Offline models](#offline-models) for fully offline setup.
- **User data** — Database and thumbnails live in `%LOCALAPPDATA%\FaceGallery\`.

### 9. Optional: custom app icon

If you change the icon, regenerate platform assets and force a clean Rust rebuild before step 6:

```powershell
pnpm exec tauri icon path\to\your-icon.png
cd src-tauri
cargo clean
cd ..
pnpm tauri:build
```

Also replace `frontend/public/favicon.svg` if you want the dev UI tab icon to match.

### Build troubleshooting

| Problem | What to do |
|---------|------------|
| `cargo` not found | Reopen terminal after `rustup` install |
| Sidecar script fails | Run `uv sync` in `backend/`; ensure PyInstaller is available via dev deps |
| `sidecar("api")` / health timeout in release | Rebuild sidecar with `backend\scripts\build-sidecar.ps1`, then `pnpm tauri:build`. The sidecar must be a **single-file** PyInstaller exe (not `--onedir` with only `api.exe` copied). |
| App opens but shows "Not Responding" | Fixed in recent builds: sidecar startup no longer blocks the UI thread. Rebuild sidecar + installer. First launch may take 1–2 minutes while models load in the background. |
| Old icon in release build | Run `cargo clean` in `src-tauri/`, then `pnpm tauri:build` again |
| Build succeeds but scan fails on first run | Allow network once for model download, or pre-place models (see [Offline models](#offline-models)) |

### Dev vs production

| | Development | Production build |
|--|-------------|------------------|
| Command | `pnpm tauri:dev` + `backend\scripts\dev.ps1` | `pnpm tauri:build` |
| API | Separate Python process you start manually | Bundled `api.exe` sidecar auto-started |
| Sidecar `.exe` in `binaries/` | Not required | **Required** before `tauri:build` |

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
