"""
Setup script to copy models to ComfyUI and install custom nodes.

Usage:
    python scripts/setup_comfyui.py
    python scripts/setup_comfyui.py --comfyui-path "D:\path\to\ComfyUI"
"""

import os
import shutil
import argparse
import subprocess

DEFAULT_COMFYUI = r"D:\AI-Workspace\univa\comfyui\ComfyUI"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_MODELS = os.path.join(REPO_ROOT, "models")

# Model mappings: (source subfolder, source file) -> (target subfolder, target file)
MODEL_MAPPINGS = {
    ("xlabs/ipadapters", "flux-ip-adapter.safetensors"): ("xlabs/ipadapters", "flux-ip-adapter.safetensors"),
    ("clip_vision", "model.safetensors"): ("clip_vision", "clip-vit-large-patch14.safetensors"),
}

def install_custom_node(comfyui_path: str):
    """Clone x-flux-comfyui if not exists."""
    custom_nodes = os.path.join(comfyui_path, "custom_nodes")
    xflux_path = os.path.join(custom_nodes, "x-flux-comfyui")
    
    if os.path.exists(xflux_path):
        print("[OK] x-flux-comfyui already installed")
        return True
    
    print(f"\nInstalling x-flux-comfyui custom node...")
    try:
        subprocess.run([
            "git", "clone", 
            "https://github.com/XLabs-AI/x-flux-comfyui.git",
            xflux_path
        ], check=True)
        print("[OK] x-flux-comfyui installed")
        
        # Run setup.py if exists
        setup_py = os.path.join(xflux_path, "setup.py")
        if os.path.exists(setup_py):
            print("  Running setup.py...")
            subprocess.run(["python", setup_py], cwd=xflux_path)
        return True
    except Exception as e:
        print(f"\n[ERR] Failed to install: {e}")
        return False

def setup_models(comfyui_path: str):
    """Copy models from repo to ComfyUI."""
    print(f"\n{'='*50}")
    print("ComfyUI Model Setup")
    print(f"{'='*50}")
    print(f"ComfyUI: {comfyui_path}")
    print(f"Source:  {REPO_MODELS}")
    
    if not os.path.exists(comfyui_path):
        print(f"\n[ERR] ComfyUI path does not exist!")
        return False
    
    models_base = os.path.join(comfyui_path, "models")
    
    for (src_sub, src_file), (dst_sub, dst_file) in MODEL_MAPPINGS.items():
        src = os.path.join(REPO_MODELS, src_sub, src_file)
        dst_dir = os.path.join(models_base, dst_sub)
        dst = os.path.join(dst_dir, dst_file)
        
        if not os.path.exists(src):
            print(f"\n[WARN] {src_file} not found. Run download_ipadapter.py first.")
            continue
        
        os.makedirs(dst_dir, exist_ok=True)
        
        if os.path.exists(dst):
            print(f"\n[OK] {dst_sub}/{dst_file} exists")
            continue
        
        print(f"\nCopying {src_file} -> {dst_sub}/{dst_file}")
        shutil.copy2(src, dst)
        print(f"  [OK] Done!")
    
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfyui-path", default=DEFAULT_COMFYUI)
    parser.add_argument("--skip-node", action="store_true", help="Skip custom node install")
    args = parser.parse_args()
    
    if not args.skip_node:
        install_custom_node(args.comfyui_path)
    
    setup_models(args.comfyui_path)
    
    print(f"\n{'='*50}")
    print("Setup complete! Restart ComfyUI to use IP-Adapter.")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
