"""
Download IP-Adapter models for Flux.

Downloads:
- XLabs-AI flux-ip-adapter-v2 
- CLIP Vision encoder (OpenAI CLIP ViT-L/14)

Usage:
    python scripts/download_ipadapter.py
"""

import os
import urllib.request
import sys
import ssl

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

# Create unverified SSL context for downloads
ssl._create_default_https_context = ssl._create_unverified_context

MODELS = {
    "ip_adapter": {
        "url": "https://huggingface.co/XLabs-AI/flux-ip-adapter-v2/resolve/main/ip_adapter.safetensors",
        "filename": "flux-ip-adapter.safetensors",
        "subfolder": "xlabs/ipadapters",
        "size_mb": 2560
    },
    "clip_vision": {
        "url": "https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/model.safetensors",
        "filename": "model.safetensors",
        "subfolder": "clip_vision",
        "size_mb": 890
    }
}

def download_file(url: str, filepath: str, desc: str = ""):
    """Download file with progress."""
    print(f"\nDownloading {desc or os.path.basename(filepath)}...")
    print(f"  URL: {url}")
    print(f"  To: {filepath}")
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_down = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(f"\r  {percent:.1f}% ({mb_down:.1f}/{mb_total:.1f} MB)")
            sys.stdout.flush()
    
    try:
        urllib.request.urlretrieve(url, filepath, progress_hook)
        print("\n  [OK] Done!")
        return True
    except Exception as e:
        print(f"\n  [ERROR] Error: {e}")
        return False

def main():
    print("=" * 50)
    print("IP-Adapter Model Downloader for Flux")
    print("=" * 50)
    
    success = True
    for name, info in MODELS.items():
        subfolder = os.path.join(MODELS_DIR, info["subfolder"])
        filepath = os.path.join(subfolder, info["filename"])
        
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"\n[OK] {info['filename']} already exists ({size_mb:.1f} MB)")
            continue
        
        print(f"\n{name}: ~{info['size_mb']} MB")
        if not download_file(info["url"], filepath, info["filename"]):
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("Download Complete!")
        print(f"Models saved to: {MODELS_DIR}")
        print("\nNext steps:")
        print("1. Install x-flux-comfyui custom node in ComfyUI")
        print("2. Run: python scripts/setup_comfyui.py")
        print("3. Restart ComfyUI")
    else:
        print("Some downloads failed. Please retry.")
    print("=" * 50)

if __name__ == "__main__":
    main()
