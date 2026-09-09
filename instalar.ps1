# ============================================================================
# Instalador — Clonar Funil & Detectar Cloaking (Windows / PowerShell)
# ============================================================================
# Roda tudo do zero: checa/instala Node.js, Git, ffmpeg e o Claude Code,
# clona este repositório (se ainda não estiver clonado) e instala a skill
# em %USERPROFILE%\.claude\skills\clonar-funil-detectar-cloaking\
#
# Uso:
#   1. Clone este repo primeiro (precisa de acesso de colaborador, é privado):
#        git clone https://github.com/smallfiver/clonar-funil-detectar-cloaking.git
#   2. Entre na pasta clonada e rode este script:
#        cd clonar-funil-detectar-cloaking
#        powershell -ExecutionPolicy Bypass -File .\instalar.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

function Test-Comando($nome) {
    return [bool](Get-Command $nome -ErrorAction SilentlyContinue)
}

Write-Host "== Verificando requisitos ==" -ForegroundColor Cyan

# ---- Node.js ----
if (Test-Comando "node") {
    Write-Host "[ok] Node.js já instalado: $(node --version)" -ForegroundColor Green
} else {
    Write-Host "[instalando] Node.js (LTS) via winget..." -ForegroundColor Yellow
    winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
    Write-Host "Node.js instalado. Pode ser necessário reabrir o terminal se o próximo passo falhar." -ForegroundColor Yellow
}

# ---- Git ----
if (Test-Comando "git") {
    Write-Host "[ok] Git já instalado: $(git --version)" -ForegroundColor Green
} else {
    Write-Host "[instalando] Git via winget..." -ForegroundColor Yellow
    winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
}

# ---- ffmpeg (necessário pra baixar/recomprimir as VSLs) ----
if (Test-Comando "ffmpeg") {
    Write-Host "[ok] ffmpeg já instalado." -ForegroundColor Green
} else {
    Write-Host "[instalando] ffmpeg via winget..." -ForegroundColor Yellow
    winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
}

# ---- Claude Code CLI ----
Write-Host ""
Write-Host "== Instalando o Claude Code ==" -ForegroundColor Cyan
if (Test-Comando "claude") {
    Write-Host "[ok] Claude Code já instalado." -ForegroundColor Green
} else {
    npm install -g @anthropic-ai/claude-code
}

# ---- Instalar a skill ----
Write-Host ""
Write-Host "== Instalando a skill ==" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$origemSkill = Join-Path $scriptDir "clonar-funil-detectar-cloaking"
$destinoSkills = Join-Path $env:USERPROFILE ".claude\skills"
$destinoSkill = Join-Path $destinoSkills "clonar-funil-detectar-cloaking"

if (-not (Test-Path $origemSkill)) {
    Write-Host "[erro] Não achei a pasta 'clonar-funil-detectar-cloaking' ao lado deste script." -ForegroundColor Red
    Write-Host "Confirme que você rodou este .ps1 de dentro da pasta do repositório clonado." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $destinoSkills)) {
    New-Item -ItemType Directory -Force -Path $destinoSkills | Out-Null
}

if (Test-Path $destinoSkill) {
    Write-Host "Já existe uma skill instalada em $destinoSkill — substituindo pela versão atual do repo." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $destinoSkill
}

Copy-Item -Recurse -Force $origemSkill $destinoSkill
Write-Host "[ok] Skill instalada em: $destinoSkill" -ForegroundColor Green

Write-Host ""
Write-Host "== Tudo pronto ==" -ForegroundColor Cyan
Write-Host "1. Feche e reabra o terminal (garante que o PATH do Node/Git/ffmpeg atualizou)."
Write-Host "2. Rode 'claude' numa pasta qualquer para autenticar (abre o navegador)."
Write-Host "3. Digite '/clonar-funil-detectar-cloaking' — se aparecer no autocomplete, a skill está instalada."
