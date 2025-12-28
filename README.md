# AI Video Production Pipeline

Generate images, videos, and audio using ComfyUI + DaVinci Resolve.

## Quick Start

### 1. Run Setup (One Time)
```powershell
cd D:\videoeditor\scripts
powershell -ExecutionPolicy Bypass -File setup.ps1
```

This installs:
- x-flux-comfyui custom node (IP-Adapter support)
- flux-ip-adapter.safetensors model
- CLIP Vision model

### 2. Restart ComfyUI

### 3. Load a Workflow
Open ComfyUI and drag any workflow from `workflows/` into the interface.

---

## Workflows

| Workflow | Purpose |
|----------|---------|
| `ip_adapter_flux.json` | Generate images with character/style consistency |
| `ltx_video_gen.json` | Text/Image to video with LTX-Video 13B |
| `workflow_working.json` | General purpose tested workflow |

---

## Stack

| Component | Model | Purpose |
|-----------|-------|---------|
| Image Gen | Flux Kontext | High quality images |
| IP-Adapter | XLabs Flux IP-Adapter | Character consistency |
| Video Gen | LTX-Video 13B | Text/Image to video |
| Video Edit | VACE/Wan 2.2 | Edit existing video |
| Audio Sync | MMAudio | Add sound to video |
| TTS | Chatterbox | Voiceovers |
| Editor | DaVinci Resolve | Timeline editing |

---

## Project Structure

```
workflows/           # ComfyUI workflow JSONs
  templates/         # Reusable workflow pieces
projects/            # Video projects (gitignored)
  {project}/
    references/      # Input images, style refs
    scenes/          # Generated scenes  
    audio/           # Music, voiceovers
    exports/         # Final videos
scripts/             # Automation helpers
  setup.ps1          # One-time setup script
  comfyui_api.py     # Queue workflows via API
```

---

## Usage

1. **Create character reference**: Generate or load an image of your character
2. **Use IP-Adapter workflow**: Load `ip_adapter_flux.json`, add your reference image
3. **Generate consistent scenes**: The model will maintain character appearance
4. **Create video**: Use `ltx_video_gen.json` to animate your scenes
5. **Add audio**: Use MMAudio workflow (coming soon)
6. **Edit in Resolve**: Combine clips, add music, export

---

## Model Locations

See [MODELS.md](MODELS.md) for full inventory.

Active ComfyUI: `D:\AI-Workspace\univa\comfyui\ComfyUI\models`
