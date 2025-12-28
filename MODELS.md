# Model Inventory

All models available on this system for video production.

## Active ComfyUI Installation
**Location:** `D:\AI-Workspace\univa\comfyui\ComfyUI\models`

### Video Generation
| Model | File | Purpose |
|-------|------|---------|
| LTX-Video 13B | `checkpoints/ltx-video-13b-distilled.safetensors` | Text/Image to video |
| LTX-Video 13B FP8 | `checkpoints/ltxv-13b-0.9.8-distilled-fp8.safetensors` | Text/Image to video (quantized) |
| Wan 2.2 VACE High | `diffusion_models/wan2.2_fun_vace_high_noise_14B_fp8_scaled.safetensors` | Video editing (high noise) |
| Wan 2.2 VACE Low | `diffusion_models/wan2.2_fun_vace_low_noise_14B_fp8_scaled.safetensors` | Video editing (low noise) |

### Image Generation
| Model | File | Purpose |
|-------|------|---------|
| Flux Kontext | `diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors` | High quality images |

### Audio
| Model | File | Purpose |
|-------|------|---------|
| MMAudio Large | `mmaudio/mmaudio_large_44k_v2_fp16.safetensors` | Video to audio |
| MMAudio Synchformer | `mmaudio/mmaudio_synchformer_fp16.safetensors` | Audio sync |
| MMAudio VAE | `mmaudio/mmaudio_vae_44k_fp16.safetensors` | Audio encoding |
| CLIP Vision | `mmaudio/apple_DFN5B-CLIP-ViT-H-14-384_fp16.safetensors` | Vision encoding for audio |

### Text Encoders
| Model | File | Purpose |
|-------|------|---------|
| T5-XXL FP8 | `text_encoders/t5xxl_fp8_e4m3fn_scaled.safetensors` | LTX text encoding |
| T5-XXL FP16 | `text_encoders/t5xxl_fp16.safetensors` | LTX text encoding |
| UMT5-XXL | `text_encoders/umt5-xxl-enc-bf16.safetensors` | Wan text encoding |
| CLIP-L | `text_encoders/clip_l.safetensors` | Flux text encoding |
| Qwen 2.5 VL 7B | `text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors` | HunyuanVideo text |
| ByT5 Small | `text_encoders/byt5_small_glyphxl_fp16.safetensors` | Glyph rendering |

### VAEs
| Model | File | Purpose |
|-------|------|---------|
| LTX VAE | `vae/ltxv-vae.safetensors` | LTX decoding |
| Wan 2.1 VAE | `vae/wan_2.1_vae.safetensors` | Wan decoding |
| Flux AE | `vae/ae.safetensors` | Flux decoding |
| HunyuanVideo VAE | `vae/hunyuanvideo15_vae_fp16.safetensors` | HunyuanVideo decoding |

### Upscalers
| Model | File | Purpose |
|-------|------|---------|
| LTX Spatial | `latent_upscale_models/ltxv-spatial-upscaler-0.9.8.safetensors` | LTX upscaling |
| HunyuanVideo 1080p | `latent_upscale_models/hunyuanvideo15_latent_upsampler_1080p.safetensors` | HunyuanVideo upscaling |

---

## Backup Models (D:\_REVIEW_BEFORE_DELETE)
**Location:** `D:\_REVIEW_BEFORE_DELETE\HunyuanVideo_models\HunyuanVideo\split_files\`

### HunyuanVideo 1.5 Complete Set
| Category | Models |
|----------|--------|
| diffusion_models | 480p/720p/1080p t2v/i2v variants (fp16 & fp8) |
| text_encoders | qwen_2.5_vl_7b, byt5_small_glyphxl |
| vae | hunyuanvideo15_vae_fp16 |
| clip_vision | sigclip_vision_patch14_384 |
| latent_upscale | 720p & 1080p upsamplers |
| loras | lightx2v 4step lora |

---

## Custom Nodes Installed
**Location:** `D:\AI-Workspace\univa\comfyui\ComfyUI\custom_nodes\`

- ComfyUI-HunyuanVideoWrapper
- ComfyUI-MMAudio  
- ComfyUI-WanVideoWrapper
- comfyui-videohelpersuite
- ComfyUI-Manager

---

## Reference Media
**Location:** `D:\boats\` - Boat images and videos for testing
