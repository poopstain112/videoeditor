"""
Test IP-Adapter workflow by generating an image with a reference.

Usage:
    python scripts/test_ipadapter.py
    python scripts/test_ipadapter.py --reference path/to/image.jpg
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
import base64

COMFYUI_URL = "http://localhost:8188"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_comfyui():
    """Check if ComfyUI is running."""
    try:
        req = urllib.request.Request(f"{COMFYUI_URL}/system_stats")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return True
    except:
        return False

def upload_image(image_path: str) -> str:
    """Upload image to ComfyUI and return filename."""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    filename = os.path.basename(image_path)
    
    # Create multipart form data
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f'Content-Type: image/jpeg\r\n\r\n'
    ).encode() + image_data + f'\r\n--{boundary}--\r\n'.encode()
    
    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        return result.get('name', filename)

def queue_workflow(workflow: dict) -> str:
    """Queue workflow and return prompt_id."""
    data = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
        return result.get('prompt_id')

def wait_for_completion(prompt_id: str, timeout: int = 300) -> bool:
    """Wait for prompt to complete."""
    start = time.time()
    while time.time() - start < timeout:
        req = urllib.request.Request(f"{COMFYUI_URL}/history/{prompt_id}")
        try:
            with urllib.request.urlopen(req) as resp:
                history = json.loads(resp.read().decode())
                if prompt_id in history:
                    return True
        except:
            pass
        time.sleep(2)
        print(".", end="", flush=True)
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", help="Reference image path")
    parser.add_argument("--prompt", default="A warrior in mystical forest, cinematic lighting")
    args = parser.parse_args()
    
    print("IP-Adapter Test")
    print("=" * 50)
    
    # Check ComfyUI
    print("\n[1] Checking ComfyUI...")
    if not check_comfyui():
        print("[ERR] ComfyUI not running at", COMFYUI_URL)
        print("      Start ComfyUI first, then run this test.")
        sys.exit(1)
    print("[OK] ComfyUI is running")
    
    # Load workflow
    print("\n[2] Loading workflow...")
    workflow_path = os.path.join(REPO_ROOT, "workflows", "ip_adapter_api.json")
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    print("[OK] Workflow loaded")
    
    # Upload reference image if provided
    if args.reference:
        print(f"\n[3] Uploading reference image: {args.reference}")
        if not os.path.exists(args.reference):
            print("[ERR] Reference image not found")
            sys.exit(1)
        filename = upload_image(args.reference)
        # Update workflow to use uploaded image (API format)
        if "5" in workflow:  # LoadImage node
            workflow["5"]["inputs"]["image"] = filename
        print(f"[OK] Uploaded as: {filename}")
    else:
        print("\n[3] No reference image provided, using default")
    
    # Update prompt (API format)
    if "8" in workflow:  # Positive prompt node
        workflow["8"]["inputs"]["clip_l"] = args.prompt
        workflow["8"]["inputs"]["t5xxl"] = args.prompt
    
    # Queue workflow
    print(f"\n[4] Queueing workflow...")
    print(f"    Prompt: {args.prompt}")
    
    try:
        prompt_id = queue_workflow(workflow)
        print(f"[OK] Queued: {prompt_id}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"[ERR] Failed to queue: {e.code}")
        print(f"      {error_body[:500]}")
        sys.exit(1)
    
    # Wait for completion
    print("\n[5] Waiting for completion", end="")
    if wait_for_completion(prompt_id):
        print("\n[OK] Generation complete!")
        print(f"\nCheck ComfyUI output folder for result.")
    else:
        print("\n[ERR] Timeout waiting for completion")
        sys.exit(1)

if __name__ == "__main__":
    main()
