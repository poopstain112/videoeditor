#!/usr/bin/env python3
"""
GPU Job Dispatcher - Central control for video factory.

Claude uses this to:
1. Check GPU availability
2. Submit jobs to ComfyUI
3. Monitor job status
4. Coordinate parallel rendering

Usage:
    python dispatcher.py status              # Check all GPUs
    python dispatcher.py test                # Test ComfyUI connection
    python dispatcher.py generate <prompt>   # Generate video
"""

import json
import time
import subprocess
import urllib.request
import urllib.error
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Configuration
COMFYUI_URL = "http://localhost:8188"
CHATTERBOX_URL = "http://localhost:8880"
JOBS_DIR = Path(__file__).parent.parent / "jobs"
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"

# GPU Configuration (your actual hardware)
GPU_CONFIG = {
    0: {"name": "RTX 5090", "role": "primary", "vram_gb": 32, "service": "comfyui"},
    1: {"name": "RTX 3090 #1", "role": "worker", "vram_gb": 24, "service": None},
    2: {"name": "RTX 3090 #2", "role": "worker", "vram_gb": 24, "service": None},
    3: {"name": "RTX 3090 #3", "role": "worker", "vram_gb": 24, "service": None},
    4: {"name": "RTX 3090 #4", "role": "worker", "vram_gb": 24, "service": "chatterbox"},
    5: {"name": "RTX 4080 Super", "role": "control", "vram_gb": 16, "service": None},
}


def get_gpu_status():
    """Get status of all GPUs via nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.used,memory.total,utilization.gpu", 
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return None
        
        gpus = {}
        for line in result.stdout.strip().split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 5:
                idx = int(parts[0])
                gpus[idx] = {
                    "name": parts[1],
                    "memory_used_mb": int(parts[2]),
                    "memory_total_mb": int(parts[3]),
                    "utilization": int(parts[4]),
                    "busy": int(parts[4]) > 50 or int(parts[2]) > int(parts[3]) * 0.8
                }
        return gpus
    except Exception as e:
        print(f"Error getting GPU status: {e}")
        return None


def check_comfyui():
    """Check if ComfyUI is running and responsive."""
    try:
        req = urllib.request.Request(f"{COMFYUI_URL}/system_stats")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return {
                "online": True,
                "version": data.get("system", {}).get("comfyui_version"),
                "gpu": data.get("devices", [{}])[0].get("name"),
                "vram_free_gb": round(data.get("devices", [{}])[0].get("vram_free", 0) / 1e9, 2)
            }
    except Exception as e:
        return {"online": False, "error": str(e)}


def check_comfyui_queue():
    """Check ComfyUI queue status."""
    try:
        req = urllib.request.Request(f"{COMFYUI_URL}/queue")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return {
                "running": len(data.get("queue_running", [])),
                "pending": len(data.get("queue_pending", []))
            }
    except:
        return {"running": 0, "pending": 0}


def queue_workflow(workflow: dict, client_id: str = "dispatcher"):
    """Queue a workflow to ComfyUI."""
    payload = {
        "prompt": workflow,
        "client_id": client_id
    }
    
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return {"success": True, "prompt_id": result.get("prompt_id")}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else str(e)
        return {"success": False, "error": error_body}
    except Exception as e:
        return {"success": False, "error": str(e)}


def print_status():
    """Print formatted status of all GPUs and services."""
    print("\n" + "="*70)
    print("VIDEO FACTORY STATUS")
    print("="*70)
    
    # GPU Status
    gpus = get_gpu_status()
    if gpus:
        print("\nGPU STATUS:")
        print("-"*70)
        for idx, info in sorted(gpus.items()):
            config = GPU_CONFIG.get(idx, {})
            role = config.get("role", "unknown")
            service = config.get("service", "")
            
            state = "[BUSY]" if info["busy"] else "[READY]"
            mem_pct = round(info["memory_used_mb"] / info["memory_total_mb"] * 100)
            
            svc_str = f" <{service}>" if service else ""
            print(f"  GPU {idx}: {info['name'][:25]:<25} {state:<8} "
                  f"VRAM: {mem_pct:>3}% ({info['memory_used_mb']:>5}/{info['memory_total_mb']}MB) "
                  f"[{role}]{svc_str}")
    else:
        print("\n  WARNING: Could not get GPU status")
    
    # ComfyUI Status
    print("\nSERVICES:")
    print("-"*70)
    
    comfy = check_comfyui()
    if comfy["online"]:
        queue = check_comfyui_queue()
        print(f"  ComfyUI:    ONLINE (v{comfy['version']}) - "
              f"Queue: {queue['running']} running, {queue['pending']} pending - "
              f"VRAM free: {comfy['vram_free_gb']}GB")
    else:
        print(f"  ComfyUI:    OFFLINE - {comfy.get('error', 'Unknown error')}")
    
    # Check Chatterbox
    try:
        req = urllib.request.Request(f"{CHATTERBOX_URL}/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"  Chatterbox: ONLINE (TTS ready)")
    except:
        print(f"  Chatterbox: OFFLINE or no health endpoint")
    
    print("\n" + "="*70)


def test_comfyui():
    """Run a simple test on ComfyUI."""
    print("\nTesting ComfyUI connection...")
    
    status = check_comfyui()
    if not status["online"]:
        print(f"FAIL: ComfyUI is offline: {status.get('error')}")
        return False
    
    print(f"OK: ComfyUI is online")
    print(f"   Version: {status['version']}")
    print(f"   GPU: {status['gpu']}")
    print(f"   VRAM Free: {status['vram_free_gb']}GB")
    
    queue = check_comfyui_queue()
    print(f"   Queue: {queue['running']} running, {queue['pending']} pending")
    
    return True


if __name__ == "__main__":
    # Ensure directories exist
    JOBS_DIR.mkdir(exist_ok=True)
    OUTPUTS_DIR.mkdir(exist_ok=True)
    
    if len(sys.argv) < 2:
        print("Usage: dispatcher.py <command> [args]")
        print("Commands:")
        print("  status    - Show GPU and service status")
        print("  test      - Test ComfyUI connection")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "status":
        print_status()
    elif cmd == "test":
        test_comfyui()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
