# AI Video Production Pipeline

Generate images, videos, and audio using ComfyUI + DaVinci Resolve.

## Architecture

```
Prompt → ComfyUI (image/video gen) → DaVinci Resolve (editing) → Final Video
```

## Stack

| Component | Model | Purpose |
|-----------|-------|---------|
| Image Gen | Flux Kontext | High quality images |
| Video Gen | LTX-Video 13B | Text/Image to video |
| Video Edit | VACE/Wan 2.2 | Edit existing video |
| Audio Sync | MMAudio | Add sound to video |
| TTS | Chatterbox | Voiceovers |
| Editor | DaVinci Resolve | Timeline editing |

## Project Structure

```
workflows/           # ComfyUI workflow JSONs
  templates/         # Reusable workflow pieces
projects/            # Video projects (gitignored)
  {project}/
    references/      # Input images, style refs
    scenes/          # Generated scenes
    audio/           # Music, voiceovers
    exports/         # Final videos
scripts/             # Automation helpers
```

## Workflows

- `01_text_to_image.json` - Text prompt → Image
- `02_image_to_video.json` - Image → Video
- `03_consistent_character.json` - Character reference → New scene
- `04_video_edit.json` - Video → Edited video
- `05_add_audio.json` - Video + Audio → Final

## Usage

1. Describe what you want
2. Run appropriate workflow in ComfyUI
3. Iterate with edits
4. Combine in DaVinci Resolve
5. Export
