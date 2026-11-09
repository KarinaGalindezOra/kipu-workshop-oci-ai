param([int]$Port = 8503)
$ErrorActionPreference = 'Stop'
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../..')).Path
& (Join-Path $ProjectRoot '.venv/Scripts/python.exe') -m streamlit run (Join-Path $PSScriptRoot '../ui/app.py') --server.address 127.0.0.1 --server.port $Port --server.fileWatcherType none
exit $LASTEXITCODE
