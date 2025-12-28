# VIDEO FACTORY - MASTER CONTROL
# Claude: READ THIS FIRST. EVERY TIME.

## STATUS: ALL SYSTEMS GO

| Function | Status | Time |
|----------|--------|------|
| text_to_video() | WORKING | ~35s |
| image_to_video() | WORKING | ~10s |
| text_to_image() | WORKING | ~105s |
| text_to_audio() | WORKING | ~30s |

## THE ONLY FILE THAT MATTERS
```
D:\videoeditor\factory.py
```

## HOW TO USE
```python
from factory import text_to_video, image_to_video, text_to_image, text_to_audio

# Generate video from text
text_to_video("boat on calm water, sunset", seed=42)

# Generate video from image (image must be in ComfyUI input folder)
image_to_video("20230314_143634.jpg", "boat gliding on water", seed=42)

# Generate image
text_to_image("luxury yacht at sunset", seed=42)

# Generate audio
text_to_audio("ocean waves, seagulls", duration=5, seed=42)
```

## OUTPUT LOCATION
All outputs go to: /workspace/ComfyUI/output/ (inside container)

## COMFYUI
- URL: http://localhost:8188
- Status: RUNNING on RTX 5090
- Container: comfyui-5090

## RULES FOR CLAUDE
1. READ THIS FILE FIRST
2. USE factory.py ONLY
3. DO NOT REBUILD WORKFLOWS
4. UPDATE THIS FILE AFTER CHANGES

## NEXT: Video Editing (VACE)
Need to add: edit_video() function using Wan 2.2 VACE

## LAST UPDATED
2024-12-28 - All 4 core functions tested and working
