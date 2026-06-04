Set-Location $PSScriptRoot\..

if (-not $env:FACE_GALLERY_API_PORT) {
    $env:FACE_GALLERY_API_PORT = "28765"
}

$port = [int]$env:FACE_GALLERY_API_PORT
$inUse = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($inUse) {
    Write-Host "Port $port is already in use (PID $($inUse.OwningProcess))."
    Write-Host "Stop that process or set another port: `$env:FACE_GALLERY_API_PORT = 28766"
    exit 1
}

Write-Host "Starting API on http://127.0.0.1:$port"
# No --reload during long scans (avoids extra process + SQLite lock issues).
uv run uvicorn face_gallery.main:app --host 127.0.0.1 --port $port
