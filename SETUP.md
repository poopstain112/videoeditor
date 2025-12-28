# IP-Adapter Setup Guide

## Quick Start

```powershell
cd D:\videoeditor

# 1. Download models (~3.4GB)
python scripts/download_ipadapter.py

# 2. Install to ComfyUI
python scripts/setup_comfyui.py

# 3. Restart ComfyUI
```

## What Gets Installed

### Models
| Model | Size | Purpose |
|-------|------|---------|
| flux-ip-adapter.safetensors | 2.5GB | XLabs IP-Adapter v2 for Flux |
| clip-vit-large-patch14.safetensors | 890MB | CLIP Vision encoder |

### Custom Node
- **x-flux-comfyui** - XLabs custom nodes for Flux IP-Adapter

## Manual Installation

If the scripts fail, install manually:

### 1. Download Models

Download from HuggingFace:
- [flux-ip-adapter-v2](https://huggingface.co/XLabs-AI/flux-ip-adapter-v2/resolve/main/ip_adapter.safetensors)
- [clip-vit-large-patch14](https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/model.safetensors)

### 2. Place Models

```
ComfyUI/models/
├── xlabs/
│   └── ipadapters/
│       └── flux-ip-adapter.safetensors
└── clip_vision/
    └── clip-vit-large-patch14.safetensors
```

### 3. Install Custom Node

```powershell
cd ComfyUI/custom_nodes
git clone https://github.com/XLabs-AI/x-flux-comfyui.git
cd x-flux-comfyui
python setup.py
```

## Usage in ComfyUI

1. **Load IP-Adapter**: Use `LoadFluxIPAdapter` node
2. **Apply IP-Adapter**: Use `ApplyFluxIPAdapter` node
3. **Load reference image**: Use `LoadImage` node

### Key Parameters

| Parameter | Recommended | Description |
|-----------|-------------|-------------|
| steps | 40-50 | Sampling steps |
| guidance | 1.0-3.5 | IP-Adapter strength |
| weight | 0.5-1.0 | How much to follow reference |

## Troubleshooting

### "LoadFluxIPAdapter not found"
- Restart ComfyUI after installing x-flux-comfyui
- Check custom_nodes folder has x-flux-comfyui

### "Model not found"
- Verify model paths match exactly
- Check file wasn't corrupted (re-download)

### Out of VRAM
- Use fp8 quantized models
- Reduce resolution to 512x512
- Close other GPU applications
