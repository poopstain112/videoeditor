# Video Factory Architecture

## The Core Idea

This is a **video assembly line**, not "running models."

Each GPU has a role. Claude is the director, not the worker.

---

## GPU Role Assignment (Your Actual Hardware)

| GPU | Card | Role | Purpose |
|-----|------|------|---------|
| 0 | RTX 5090 (32GB) | Primary Generator | High-res video, long clips, final quality |
| 1-3 | RTX 3090 ×3 (24GB each) | Parallel Workers | Scene generation, batch rendering |
| 4 | RTX 3090 (24GB) | Worker/Backup | Additional capacity |
| 5 | RTX 4080 Super (16GB) | Control + Fast Inference | Keyframes, previews, orchestration |

### Current Status
- **GPU 0 (5090)**: Running ComfyUI on port 8188
- **GPU 1-4 (3090s)**: Available for parallel work
- **GPU 5 (4080 Super)**: Available for control tasks

---

## What Claude Does

Claude is **not** generating video. Claude is:
- Planning scenes
- Dispatching jobs to GPUs
- Monitoring completion
- Iterating on failures
- Assembling final output

**Claude never blocks a GPU. GPUs do work. Claude thinks.**

---

## The Pipeline

```
STEP 1: Concept → Shot List (Claude)
└── Break video into scenes with prompts, durations, styles

STEP 2: Keyframes (GPU 5 - 4080 Super)  
└── Generate reference images for each scene

STEP 3: Parallel Scene Generation (GPU 1-4 - 3090s)
└── Each GPU renders one scene simultaneously

STEP 4: Hero Shots (GPU 0 - 5090)
└── Final quality pass on best scenes

STEP 5: Assembly (Claude + FFmpeg)
└── Combine clips, add audio, export
```

---

## API Endpoints

### ComfyUI (GPU 0)
- **URL**: http://localhost:8188
- **Queue workflow**: POST /prompt
- **Check status**: GET /queue
- **Get history**: GET /history

### Chatterbox TTS (GPU 4)
- **URL**: http://localhost:8880
- **Generate speech**: POST /generate

---

## Quick Commands

```bash
# Check GPU status
python scripts/dispatcher.py status

# Submit a video job
python scripts/dispatcher.py generate "warrior in mystical forest" --duration 30

# Test ComfyUI connection
python scripts/comfyui_api.py test
```
