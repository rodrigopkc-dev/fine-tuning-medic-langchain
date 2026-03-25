$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$appPath = Join-Path $PSScriptRoot "src\app.py"

if (-not (Test-Path $pythonExe)) {
    Write-Error "Ambiente virtual nao encontrado. Crie a .venv e instale as dependencias antes de executar."
    exit 1
}

if (-not (Test-Path $appPath)) {
    Write-Error "Arquivo da interface nao encontrado em src\\app.py."
    exit 1
}

& $pythonExe -m streamlit run $appPath
