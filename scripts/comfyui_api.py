"""
ComfyUI API helper - queue workflows from command line.

Usage:
    python comfyui_api.py workflow.json
    python comfyui_api.py workflow.json --prompt "your prompt here"
"""

import json
import argparse
import urllib.request
import urllib.parse

COMFYUI_URL = "http://localhost:8188"

def queue_workflow(workflow_path: str, replacements: dict = None):
    """Load workflow JSON and queue it to ComfyUI."""
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    # Apply any text replacements
    if replacements:
        workflow_str = json.dumps(workflow)
        for key, value in replacements.items():
            workflow_str = workflow_str.replace(f"{{{key}}}", value)
        workflow = json.loads(workflow_str)
    
    # Queue to ComfyUI
    data = json.dumps({"prompt": workflow}).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"Queued: {result.get('prompt_id', 'unknown')}")
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", help="Path to workflow JSON")
    parser.add_argument("--prompt", help="Text prompt to inject")
    args = parser.parse_args()
    
    replacements = {}
    if args.prompt:
        replacements["PROMPT"] = args.prompt
    
    queue_workflow(args.workflow, replacements)
