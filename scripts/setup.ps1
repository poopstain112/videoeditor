# VideoEditor Setup Script
# Run this ONCE to install IP-Adapter and required models
# Usage: Right-click -> Run with PowerShell, or: powershell -ExecutionPolicy Bypass -File setup.ps1

param(
    [string]$ComfyUIPath = "D:\AI-Workspace\univa\comfyui\ComfyUI"
)

Write-Host "=== VideoEditor Setup ===" -ForegroundColor Cyan
Write-Host "ComfyUI Path: $ComfyUIPath"

# Verify ComfyUI exists
if (-not (Test-Path $ComfyUIPath)) {
    Write-Host "ERROR: ComfyUI not found at $ComfyUIPath" -ForegroundColor Red
    Write-Host "Please provide correct path: .\setup.ps1 -ComfyUIPath 'C:\path\to\ComfyUI'"
    exit 1
}

$CustomNodesPath = Join-Path $ComfyUIPath "custom_nodes"
$ModelsPath = Join-Path $ComfyUIPath "models"

# Step 1: Install x-flux-comfyui (IP-Adapter support)
Write-Host "`n[1/4] Installing x-flux-comfyui custom node..." -ForegroundColor Yellow
$XFluxPath = Join-Path $CustomNodesPath "x-flux-comfyui"
if (Test-Path $XFluxPath) {
    Write-Host "x-flux-comfyui already exists, updating..." -ForegroundColor Green
    Push-Location $XFluxPath
    git pull
    Pop-Location
} else {
    Push-Location $CustomNodesPath
    git clone https://github.com/XLabs-AI/x-flux-comfyui.git
    Pop-Location
}

# Run setup.py
Write-Host "Running setup.py..."
Push-Location $XFluxPath
python setup.py
Pop-Location

# Step 2: Create model directories
Write-Host "`n[2/4] Creating model directories..." -ForegroundColor Yellow
$XLabsPath = Join-Path $ModelsPath "xlabs"
$IPAdapterPath = Join-Path $XLabsPath "ipadapters"
$LorasPath = Join-Path $XLabsPath "loras"
$ControlnetsPath = Join-Path $XLabsPath "controlnets"

New-Item -ItemType Directory -Force -Path $IPAdapterPath | Out-Null
New-Item -ItemType Directory -Force -Path $LorasPath | Out-Null
New-Item -ItemType Directory -Force -Path $ControlnetsPath | Out-Null
Write-Host "Created: $IPAdapterPath" -ForegroundColor Green

# Step 3: Download IP-Adapter model
Write-Host "`n[3/4] Downloading IP-Adapter model..." -ForegroundColor Yellow
$IPAdapterFile = Join-Path $IPAdapterPath "flux-ip-adapter.safetensors"
if (Test-Path $IPAdapterFile) {
    Write-Host "IP-Adapter model already exists, skipping..." -ForegroundColor Green
} else {
    Write-Host "Downloading flux-ip-adapter.safetensors (this may take a while)..."
    $IPAdapterURL = "https://huggingface.co/XLabs-AI/flux-ip-adapter/resolve/main/flux-ip-adapter.safetensors"
    Invoke-WebRequest -Uri $IPAdapterURL -OutFile $IPAdapterFile
    Write-Host "Downloaded: $IPAdapterFile" -ForegroundColor Green
}

# Step 4: Download CLIP Vision model (if not exists)
Write-Host "`n[4/4] Checking CLIP Vision model..." -ForegroundColor Yellow
$ClipVisionPath = Join-Path $ModelsPath "clip_vision"
$ClipFile = Join-Path $ClipVisionPath "clip-vit-large-patch14.safetensors"
if (Test-Path $ClipFile) {
    Write-Host "CLIP Vision model already exists" -ForegroundColor Green
} else {
    # Check for alternative names
    $AltClipFile = Join-Path $ClipVisionPath "model.safetensors"
    if (Test-Path $AltClipFile) {
        Write-Host "CLIP Vision model found (model.safetensors)" -ForegroundColor Green
    } else {
        Write-Host "Downloading CLIP Vision model..."
        New-Item -ItemType Directory -Force -Path $ClipVisionPath | Out-Null
        $ClipURL = "https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/model.safetensors"
        Invoke-WebRequest -Uri $ClipURL -OutFile $AltClipFile
        Write-Host "Downloaded: $AltClipFile" -ForegroundColor Green
    }
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "Restart ComfyUI to load the new nodes."
Write-Host "IP-Adapter workflow: workflows/ip_adapter_flux.json"
