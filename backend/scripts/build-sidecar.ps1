# Build FastAPI sidecar for Tauri (Windows x64)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$RepoRoot = Split-Path $Root -Parent
$OutDir = Join-Path $RepoRoot "src-tauri\binaries"
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

Set-Location $Root
uv sync

$Entry = Join-Path $Root "src\face_gallery\main.py"
$Schema = Join-Path $Root "src\face_gallery\db\schema.sql"
$BuildDir = Join-Path $Root "build\pyinstaller"
$DistDir = Join-Path $Root "dist"

if (-not (Test-Path $Schema)) {
  throw "Database schema not found: $Schema"
}

# Tauri externalBin expects a single executable per target triple (--onefile).
# Do not use --onedir: copying only api.exe leaves out _internal/ and the sidecar cannot start.
uv run pyinstaller `
  --noconfirm `
  --clean `
  --onefile `
  --name api `
  --distpath $DistDir `
  --workpath $BuildDir `
  --paths (Join-Path $Root "src") `
  --add-data "${Schema};face_gallery/db" `
  --hidden-import=face_gallery `
  --hidden-import=face_gallery.main `
  --hidden-import=face_gallery.config `
  --hidden-import=face_gallery.ml.model_setup `
  --hidden-import=face_gallery.ml.insightface_app `
  --hidden-import=uvicorn.logging `
  --hidden-import=uvicorn.loops `
  --hidden-import=uvicorn.loops.auto `
  --hidden-import=uvicorn.protocols `
  --hidden-import=uvicorn.protocols.http `
  --hidden-import=uvicorn.protocols.http.auto `
  --hidden-import=uvicorn.protocols.websockets `
  --hidden-import=uvicorn.protocols.websockets.auto `
  --hidden-import=uvicorn.lifespan `
  --hidden-import=uvicorn.lifespan.on `
  --collect-all insightface `
  --collect-all onnxruntime `
  $Entry

$TargetName = "api-x86_64-pc-windows-msvc.exe"
$SourceExe = Join-Path $DistDir "api.exe"
if (-not (Test-Path $SourceExe)) {
  throw "PyInstaller output not found: $SourceExe"
}
Copy-Item $SourceExe (Join-Path $OutDir $TargetName) -Force
Write-Host "Sidecar built: $(Join-Path $OutDir $TargetName)"
Write-Host ""
Write-Host "Rebuild the installer from repo root: pnpm tauri:build"
