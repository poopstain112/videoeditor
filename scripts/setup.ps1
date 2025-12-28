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
    exit 1
}

$CustomNodesPath = Join-Path $ComfyUIPath "custom_nodes"
$ModelsPath = Join-Path $ComfyUIPath "models"

# Step 1: Check x-flux-comfyui (already installed from previous run)
Write-Host "`n[1/3] Checking x-flux-comfyui..." -ForegroundColor Yellow
$XFluxPath = Join-Path $CustomNodesPath "x-flux-comfyui"
if (Test-Path $XFluxPath) {
    Write-Host "x-flux-comfyui already installed" -ForegroundColor Green
} else {
    Write-Host "Installing x-flux-comfyui..."
    Push-Location $CustomNodesPath
    git clone https://github.com/XLabs-AI/x-flux-comfyui.git
    Pop-Location
}

# Step 2: Create model directories and download IP-Adapter
Write-Host "`n[2/3] Setting up IP-Adapter model..." -ForegroundColor Yellow
$XLabsPath = Join-Path $ModelsPath "xlabs"
$IPAdapterPath = Join-Path $XLabsPath "ipadapters"
New-Item -ItemType Directory -Force -Path $IPAdapterPath | Out-Null

$IPAdapterFile = Join-Path $IPAdapterPath "ip_adapter.safetensors"
if (Test-Path $IPAdapterFile) {
    Write-Host "IP-Adapter model already exists" -ForegroundColor Green
} else {
    Write-Host "Downloading ip_adapter.safetensors (~982MB)..."
    $IPAdapterURL = "https://huggingface.co/XLabs-AI/flux-ip-adapter/resolve/main/ip_adapter.safetensors"
    try {
        Invoke-WebRequest -Uri $IPAdapterURL -OutFile $IPAdapterFile -UseBasicParsing
        Write-Host "Downloaded: $IPAdapterFile" -ForegroundColor Green
    } catch {
        Write-Host "Download failed. Try manual download from:" -ForegroundColor Red
        Write-Host "  $IPAdapterURL" -ForegroundColor Yellow
        Write-Host "  Save to: $IPAdapterFile" -ForegroundColor Yellow
    }
}

# Step 3: Check CLIP Vision model
Write-Host "`n[3/3] Checking CLIP Vision model..." -ForegroundColor Yellow
$ClipVisionPath = Join-Path $ModelsPath "clip_vision"
New-Item -ItemType Directory -Force -Path $ClipVisionPath | Out-Null

# Check for existing CLIP model
$ClipFiles = @(
    (Join-Path $ClipVisionPath "model.safetensors"),
    (Join-Path $ClipVisionPath "clip-vit-large-patch14.safetensors"),
    (Join-Path $ClipVisionPath "CLIP-ViT-L-14-laion2B-s32B-b82K.safetensors")
)

$ClipExists = $false
foreach ($f in $ClipFiles) {
    if (Test-Path $f) {
        Write-Host "CLIP Vision model found: $f" -ForegroundColor Green
        $ClipExists = $true
        break
    }
}

if (-not $ClipExists) {
    $ClipFile = Join-Path $ClipVisionPath "model.safetensors"
    Write-Host "Downloading CLIP Vision model (~890MB)..."
    $ClipURL = "https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/model.safetensors"
    try {
        Invoke-WebRequest -Uri $ClipURL -OutFile $ClipFile -UseBasicParsing
        Write-Host "Downloaded: $ClipFile" -ForegroundColor Green
    } catch {
        Write-Host "Download failed. Try manual download from:" -ForegroundColor Red
        Write-Host "  $ClipURL" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "1. Restart ComfyUI"
Write-Host "2. Load workflow: workflows/ip_adapter_flux.json"
Write-Host "3. Set your reference image in LoadImage node"
Write-Host "4. Generate!"
