# Photo-based Blender reel

Choose motion when a slow reveal or actual detail helps explain the product. Skip when fidelity is unresolved or motion adds only decoration; record the reason.

Stage an approved transparent product cutout as a flat plane in a 3D scene. Use restrained front-facing camera movement and background depth. Never orbit behind the plane, invent a product model, animate assembly or add unobserved light modes. Inspect the cutout against the original first.

Default: 10 seconds, 1080×1920, 24 fps, detail-to-full reveal and a final hold. No music without rights. `scripts/blender_reel.py` creates a neutral scene and editable blend file; it does not add brand text or reconstruct the item.

```sh
blender --background --python-exit-code 1 --python scripts/blender_reel.py -- \
  --image /absolute/private/approved-cutout.png \
  --output /absolute/private/reel.blend --render
ffmpeg -framerate 24 -i /absolute/private/reel-frames/%04d.png \
  -c:v libx264 -pix_fmt yuv420p -movflags +faststart /absolute/private/reel.mp4
```

`--preview` renders first/middle/final frames at reduced resolution. Inspect alpha edges, clipping, distortion and pacing. A blend file or frames alone is not a completed reel: verify MP4 metadata and playback before delivery. Follow platform permission rules for any required software installation; do not silently add dependencies for optional motion work.
