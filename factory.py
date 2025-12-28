"""
VIDEO FACTORY - Claude's Pipeline
One script. Images, Videos, Audio. Done.
"""
import json
import time
import requests
import random
from pathlib import Path

COMFY = "http://localhost:8188"

def queue(workflow):
    """Queue workflow, wait for completion, return output path."""
    r = requests.post(f"{COMFY}/prompt", json={"prompt": workflow}, timeout=10)
    if r.status_code != 200:
        raise Exception(f"Queue failed: {r.text[:200]}")
    
    prompt_id = r.json()['prompt_id']
    print(f"  Queued: {prompt_id[:8]}...", end="", flush=True)
    
    # Wait for completion
    for i in range(120):  # 10 min max
        time.sleep(5)
        hist = requests.get(f"{COMFY}/history/{prompt_id}").json()
        if prompt_id in hist:
            status = hist[prompt_id]['status']['status_str']
            if status == 'success':
                print(f" Done ({i*5}s)")
                return hist[prompt_id]['outputs']
            elif status == 'error':
                msgs = hist[prompt_id]['status'].get('messages', [])
                err = [m for m in msgs if m[0] == 'execution_error']
                if err:
                    raise Exception(err[0][1].get('exception_message', 'Unknown error'))
                raise Exception("Workflow failed")
        print(".", end="", flush=True)
    raise Exception("Timeout")

# ============ WORKFLOWS ============

def text_to_video(prompt, seed=None, frames=65, width=768, height=512):
    """Generate video from text prompt."""
    seed = seed or random.randint(0, 2**32)
    print(f"[TEXTâ†’VIDEO] {prompt[:50]}...")
    
    workflow = {
        "1": {"inputs": {"clip_name": "t5xxl_fp16.safetensors", "type": "ltxv"}, "class_type": "CLIPLoader"},
        "2": {"inputs": {"ckpt_name": "ltxv-13b-0.9.8-distilled-fp8.safetensors"}, "class_type": "CheckpointLoaderSimple"},
        "3": {"inputs": {"max_shift": 2.05, "base_shift": 0.95, "model": ["2", 0]}, "class_type": "ModelSamplingLTXV"},
        "4": {"inputs": {"text": prompt, "clip": ["1", 0]}, "class_type": "CLIPTextEncode"},
        "5": {"inputs": {"text": "low quality, blurry, distorted", "clip": ["1", 0]}, "class_type": "CLIPTextEncode"},
        "6": {"inputs": {"frame_rate": 24.0, "positive": ["4", 0], "negative": ["5", 0]}, "class_type": "LTXVConditioning"},
        "7": {"inputs": {"width": width, "height": height, "length": frames, "batch_size": 1}, "class_type": "EmptyLTXVLatentVideo"},
        "8": {"inputs": {"sampler_name": "euler"}, "class_type": "KSamplerSelect"},
        "9": {"inputs": {"scheduler": "linear_quadratic", "steps": 25, "denoise": 1.0, "model": ["3", 0]}, "class_type": "BasicScheduler"},
        "10": {"inputs": {"noise_seed": seed}, "class_type": "RandomNoise"},
        "11": {"inputs": {"cfg": 1.0, "model": ["3", 0], "positive": ["6", 0], "negative": ["6", 1]}, "class_type": "CFGGuider"},
        "12": {"inputs": {"noise": ["10", 0], "guider": ["11", 0], "sampler": ["8", 0], "sigmas": ["9", 0], "latent_image": ["7", 0]}, "class_type": "SamplerCustomAdvanced"},
        "13": {"inputs": {"samples": ["12", 0], "vae": ["2", 2]}, "class_type": "VAEDecode"},
        "14": {"inputs": {"images": ["13", 0], "fps": 24.0}, "class_type": "CreateVideo"},
        "15": {"inputs": {"video": ["14", 0], "filename_prefix": f"t2v_{seed}", "format": "mp4", "codec": "h264"}, "class_type": "SaveVideo"}
    }
    return queue(workflow)

def image_to_video(image_path, prompt, seed=None, frames=65):
    """Generate video from image + prompt."""
    seed = seed or random.randint(0, 2**32)
    print(f"[IMAGEâ†’VIDEO] {image_path} | {prompt[:30]}...")
    
    workflow = {
        "1": {"inputs": {"clip_name": "t5xxl_fp16.safetensors", "type": "ltxv"}, "class_type": "CLIPLoader"},
        "2": {"inputs": {"ckpt_name": "ltxv-13b-0.9.8-distilled-fp8.safetensors"}, "class_type": "CheckpointLoaderSimple"},
        "3": {"inputs": {"max_shift": 2.05, "base_shift": 0.95, "model": ["2", 0]}, "class_type": "ModelSamplingLTXV"},
        "4": {"inputs": {"text": prompt, "clip": ["1", 0]}, "class_type": "CLIPTextEncode"},
        "5": {"inputs": {"text": "low quality, blurry, distorted", "clip": ["1", 0]}, "class_type": "CLIPTextEncode"},
        "6": {"inputs": {"frame_rate": 24.0, "positive": ["4", 0], "negative": ["5", 0]}, "class_type": "LTXVConditioning"},
        "20": {"inputs": {"image": image_path}, "class_type": "LoadImage"},
        "21": {"inputs": {"positive": ["6", 0], "negative": ["6", 1], "vae": ["2", 2], "image": ["20", 0], "width": 768, "height": 512, "length": frames, "batch_size": 1, "strength": 0.9}, "class_type": "LTXVImgToVideo"},
        "8": {"inputs": {"sampler_name": "euler"}, "class_type": "KSamplerSelect"},
        "9": {"inputs": {"scheduler": "linear_quadratic", "steps": 25, "denoise": 1.0, "model": ["3", 0]}, "class_type": "BasicScheduler"},
        "10": {"inputs": {"noise_seed": seed}, "class_type": "RandomNoise"},
        "11": {"inputs": {"cfg": 1.0, "model": ["3", 0], "positive": ["21", 0], "negative": ["21", 1]}, "class_type": "CFGGuider"},
        "12": {"inputs": {"noise": ["10", 0], "guider": ["11", 0], "sampler": ["8", 0], "sigmas": ["9", 0], "latent_image": ["21", 2]}, "class_type": "SamplerCustomAdvanced"},
        "13": {"inputs": {"samples": ["12", 0], "vae": ["2", 2]}, "class_type": "VAEDecode"},
        "14": {"inputs": {"images": ["13", 0], "fps": 24.0}, "class_type": "CreateVideo"},
        "15": {"inputs": {"video": ["14", 0], "filename_prefix": f"i2v_{seed}", "format": "mp4", "codec": "h264"}, "class_type": "SaveVideo"}
    }
    return queue(workflow)

def text_to_image(prompt, seed=None, width=1024, height=576):
    """Generate image from text using Flux."""
    seed = seed or random.randint(0, 2**32)
    print(f"[TEXTâ†’IMAGE] {prompt[:50]}...")
    
    workflow = {
        "1": {"inputs": {"unet_name": "flux1-dev-kontext_fp8_scaled.safetensors", "weight_dtype": "default"}, "class_type": "UNETLoader"},
        "2": {"inputs": {"clip_name1": "clip_l.safetensors", "clip_name2": "t5xxl_fp16.safetensors", "type": "flux"}, "class_type": "DualCLIPLoader"},
        "3": {"inputs": {"vae_name": "ae.safetensors"}, "class_type": "VAELoader"},
        "4": {"inputs": {"text": prompt, "clip": ["2", 0]}, "class_type": "CLIPTextEncode"},
        "5": {"inputs": {"text": "", "clip": ["2", 0]}, "class_type": "CLIPTextEncode"},
        "6": {"inputs": {"width": width, "height": height, "batch_size": 1}, "class_type": "EmptySD3LatentImage"},
        "7": {"inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "seed": seed, "steps": 20, "cfg": 3.5, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}, "class_type": "KSampler"},
        "8": {"inputs": {"samples": ["7", 0], "vae": ["3", 0]}, "class_type": "VAEDecode"},
        "9": {"inputs": {"images": ["8", 0], "filename_prefix": f"img_{seed}"}, "class_type": "SaveImage"}
    }
    return queue(workflow)

def video_to_audio(video_frames_or_path, prompt, duration=8, seed=None):
    """Generate audio for video using MMAudio."""
    seed = seed or random.randint(0, 2**32)
    print(f"[VIDEOâ†’AUDIO] {prompt[:50]}...")
    
    workflow = {
        "1": {"inputs": {"mmaudio_model": "mmaudio_large_44k_v2_fp16.safetensors"}, "class_type": "MMAudioModelLoader"},
        "2": {"inputs": {}, "class_type": "MMAudioFeatureUtilsLoader"},
        "3": {"inputs": {"mmaudio_model": ["1", 0], "feature_utils": ["2", 0], "duration": duration, "steps": 25, "cfg": 4.5, "seed": seed, "prompt": prompt, "negative_prompt": "noise, static, distortion", "mask_away_clip": False, "force_offload": True}, "class_type": "MMAudioSampler"},
        "4": {"inputs": {"audio": ["3", 0], "filename_prefix": f"audio_{seed}"}, "class_type": "SaveAudio"}
    }
    return queue(workflow)


# ============ MAIN ============

if __name__ == "__main__":
    print("=" * 50)
    print("VIDEO FACTORY TEST")
    print("=" * 50)
    
    # Test text-to-video
    result = text_to_video("A boat sailing on calm ocean water, golden sunset, cinematic", seed=42)
    print(f"Output: {result}")

