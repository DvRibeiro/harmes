import os
from PIL import Image
import numpy as np

src_image_path = r"C:\Users\vitor.henrique\.gemini\antigravity\brain\22fbd3a0-fb8b-4bc3-b93d-afdfef91713c\.user_uploaded\media_1791570732231_a7e05cd4.png"
output_dir = r"C:\Users\vitor.henrique\.gemini\antigravity\scratch\creature_assistant\assets"
os.makedirs(output_dir, exist_ok=True)

img = Image.open(src_image_path).convert("RGBA")
w, h = img.size
print(f"Original image size: {w}x{h}")

# Convert white background to transparent while keeping the creature sketch antialiased
# We can analyze pixel luminosity
arr = np.array(img, dtype=np.float32)
r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

# Luminance / brightness (0 = black, 255 = white)
lum = 0.299 * r + 0.587 * g + 0.114 * b

# If brightness is close to white (e.g. > 240), make transparent
# Alpha should be proportional to darkness: 255 when lum <= 50, decreasing to 0 when lum >= 245
alpha = np.clip((250.0 - lum) / (250.0 - 50.0) * 255.0, 0, 255)

# Also let's keep the creature's interior if it's filled or sketched
# Let's inspect: The creature has drawn lines and shading. The background is pure white / near white.
# For pixels with alpha > 0, make RGB dark or preserve shading:
arr[:, :, 3] = alpha

# Save full transparent sheet to test
trans_img = Image.fromarray(arr.astype(np.uint8))
trans_img.save(os.path.join(output_dir, "spritesheet_transparent.png"))

# Find columns with content to slice each figure
# Find vertical projection of non-zero alpha
col_max = np.max(arr[:, :, 3], axis=0)
col_has_content = col_max > 25

# Find continuous segments of content
segments = []
in_seg = False
start_x = 0

for x in range(w):
    if col_has_content[x] and not in_seg:
        in_seg = True
        start_x = x
    elif not col_has_content[x] and in_seg:
        in_seg = False
        if x - start_x > 20: # ignore noise
            segments.append((start_x, x))
if in_seg:
    segments.append((start_x, w))

print(f"Found {len(segments)} segments: {segments}")

# Crop each sprite and trim transparent borders
for idx, (x1, x2) in enumerate(segments):
    # Add a little padding
    p_x1 = max(0, x1 - 5)
    p_x2 = min(w, x2 + 5)
    sprite = trans_img.crop((p_x1, 0, p_x2, h))
    
    # Bounding box of content
    bbox = sprite.getbbox()
    if bbox:
        sprite = sprite.crop(bbox)
        # Pad slightly
        padded = Image.new("RGBA", (sprite.width + 10, sprite.height + 10), (0, 0, 0, 0))
        padded.paste(sprite, (5, 5))
        sprite = padded
    
    out_path = os.path.join(output_dir, f"frame_{idx}.png")
    sprite.save(out_path)
    print(f"Saved frame {idx}: {sprite.size} to {out_path}")
