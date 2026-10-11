import os
from PIL import Image
import numpy as np

src_image_path = r"C:\Users\vitor.henrique\.gemini\antigravity\brain\22fbd3a0-fb8b-4bc3-b93d-afdfef91713c\.user_uploaded\media_1791570732231_a7e05cd4.png"
output_dir = r"C:\Users\vitor.henrique\.gemini\antigravity\scratch\creature_assistant\assets"
os.makedirs(output_dir, exist_ok=True)

img = Image.open(src_image_path).convert("RGBA")
arr = np.array(img)
alpha = arr[:, :, 3]

# Segments
col_alpha = np.max(alpha, axis=0)
segments = []
in_seg = False
start_x = 0
for x in range(img.width):
    if col_alpha[x] > 10 and not in_seg:
        in_seg = True
        start_x = x
    elif col_alpha[x] <= 10 and in_seg:
        in_seg = False
        if x - start_x > 15:
            segments.append((start_x, x))
if in_seg:
    segments.append((start_x, img.width))

print(f"Extracting {len(segments)} frames...")

for idx, (x1, x2) in enumerate(segments):
    # Crop with small margin
    margin = 2
    crop_x1 = max(0, x1 - margin)
    crop_x2 = min(img.width, x2 + margin)
    sprite = img.crop((crop_x1, 0, crop_x2, img.height))
    bbox = sprite.getbbox()
    if bbox:
        sprite = sprite.crop(bbox)
    
    out_path = os.path.join(output_dir, f"frame_{idx}.png")
    sprite.save(out_path)
    print(f"Saved {out_path} - Size: {sprite.size}")

print("Extraction complete!")
