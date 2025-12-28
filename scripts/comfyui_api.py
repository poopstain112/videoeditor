#!/usr/bin/env python3
"""
ComfyUI API Client - Queue and monitor workflows.

Usage:
    python comfyui_api.py test                    # Test connection
    python comfyui_api.py run <workflow.json>     # Queue a workflow
    python comfyui_api.py status <prompt_id>      # Check job status
"""

import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

COMFYUI_URL = "http://localhost:8188"


def test_connection():
    """Test if ComfyUI is running."""
    try:
        req = urllib.request.Request(f"{COMFYUI_URL}/system_stats")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            print("ComfyUI is ONLINE")
            print(f"  Version: {data.get('system', {}).get('comfyui_version')}")
            devices = data.get('devices', [])
            if devices:
                print(f"  GPU: {devices[0].get('name')}")
                vram_free = devices[0].get('vram_free', 0) / 1e9
                print(f"  VRAM Free: {vram_free:.2f}GB")
            return True
    except Exception as e:
        print(f"ComfyUI is OFFLINE: {e}")
        return False


def queue_workflow(workflow_path: str):
    """Load and queue a workflow."""
    path = Path(workflow_path)
    if not path.exists():
        print(f"Error: Workflow file not found: {workflow_path}")
        return None
    
    with open(path, 'r') as f:
        workflow = json.load(f)
    
    payload = {"prompt": workflow}
    data = json.dumps(payload).encode()
    
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            prompt_id = result.get("prompt_id")
            print(f"Workflow queued successfully!")
            print(f"  Prompt ID: {prompt_id}")
            return prompt_id
    except urllib.error.HTTPError as e:
        error = e.read().decode() if e.fp else str(e)
        print(f"Error queuing workflow: {error}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_history(prompt_id: str):
    """Get execution history for a prompt."""
    try:
        req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except:
        return None


def check_status(prompt_id: str):
    """Check the status of a queued workflow."""
    # Check queue first
    try:
        req = urllib.request.Request(f"{COMFYUI_URL}/queue")
        with urllib.request.urlopen(req, timeout=5) as resp:
            queue = json.loads(resp.read().decode())
            
        # Check if running
        for item in queue.get("queue_running", []):
            if item[1] == prompt_id:
                print(f"Status: RUNNING")
                return "running"
        
        # Check if pending
        for item in queue.get("queue_pending", []):
            if item[1] == prompt_id:
                print(f"Status: PENDING (position in queue)")
                return "pending"
        
        # Check history for completion
        history = get_history(prompt_id)
        if history and prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            if outputs:
                print(f"Status: COMPLETE")
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        for img in node_output["images"]:
                            print(f"  Output: {img.get('filename')}")
                return "complete"
            else:
                status = history[prompt_id].get("status", {})
                if status.get("status_str") == "error":
                    print(f"Status: ERROR")
                    print(f"  {status.get('messages', [])}")
                    return "error"
        
        print(f"Status: UNKNOWN (not found in queue or history)")
        return "unknown"
        
    except Exception as e:
        print(f"Error checking status: {e}")
        return "error"


def wait_for_completion(prompt_id: str, timeout: int = 300):
    """Wait for a workflow to complete."""
    print(f"Waiting for completion (timeout: {timeout}s)...")
    start = time.time()
    
    while time.time() - start < timeout:
        status = check_status(prompt_id)
        if status in ["complete", "error"]:
            return status
        time.sleep(2)
    
    print("Timeout waiting for completion")
    return "timeout"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "test":
        test_connection()
    
    elif cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: comfyui_api.py run <workflow.json>")
            sys.exit(1)
        prompt_id = queue_workflow(sys.argv[2])
        if prompt_id:
            wait_for_completion(prompt_id)
    
    elif cmd == "status":
        if len(sys.argv) < 3:
            print("Usage: comfyui_api.py status <prompt_id>")
            sys.exit(1)
        check_status(sys.argv[2])
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
