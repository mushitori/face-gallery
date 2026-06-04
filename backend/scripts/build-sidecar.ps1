# Build FastAPI sidecar for Tauri (Windows x64)
$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$RepoRoot = Split-Path $Root -Parent
$OutDir = Join-Path $RepoRoot "src-tauri\binaries"
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

Set-Location $Root
uv sync

$Entry = Join-Path $Root "src\face_gallery\main.py"
$BuildDir = Join-Path $Root "build\pyinstaller"
$DistDir = Join-Path $Root "dist\api"

uv run pyinstaller `
  --noconfirm `
  --clean `
  --onedir `
  --name api `
  --distpath (Join-Path $Root "dist") `
  --workpath $BuildDir `
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
Write-Host "Before pnpm tauri:build, add to src-tauri/tauri.conf.json under bundle:"
Write-Host '  "externalBin": ["binaries/api"]'
