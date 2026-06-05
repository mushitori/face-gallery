# Contributing

Thanks for your interest in Face Gallery. This project is open source under the [MIT License](LICENSE).

## Getting started

1. Fork the repository and clone your fork.
2. Follow the setup steps in [README.md](README.md).
3. Create a branch for your change.

## Development workflow

```powershell
# Terminal 1 — API
cd backend
uv sync
.\scripts\dev.ps1

# Terminal 2 — desktop shell 
pnpm install          # from repo root
pnpm tauri:dev
```

Run backend tests before opening a pull request:

```powershell
cd backend
uv run pytest
```

## Pull requests

- Keep changes focused and easy to review.
- Update documentation when behavior or setup steps change.
- Do not commit secrets, personal photo libraries, or InsightFace model binaries (`.onnx` files).
- Describe what changed and how you tested it.

## Reporting issues

When filing a bug, include:

- Windows version
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs from the API terminal or browser devtools

## Code style

- **Python:** `ruff` conventions used in `backend/`
- **TypeScript / Vue:** Composition API with `<script setup>` in `frontend/`

Questions and ideas are welcome in GitHub Issues.
