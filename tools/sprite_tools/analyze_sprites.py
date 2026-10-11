import os
from PIL import Image
import numpy as np

src_image_path = r"C:\Users\vitor.henrique\.gemini\antigravity\brain\22fbd3a0-fb8b-4bc3-b93d-afdfef91713c\.user_uploaded\media_1791570732231_a7e05cd4.png"
output_dir = r"C:\Users\vitor.henrique\.gemini\antigravity\scratch\creature_assistant\assets"
os.makedirs(output_dir, exist_ok=True)

img = Image.open(src_image_path).convert("RGB")
w, h = img.size
print(f"Original image size: {w}x{h}")

# Convert to grayscale numpy array
gray = np.array(img.convert("L"))

# Background is white (> 240). Let's see darkness: (255 - gray)
darkness = 255 - gray

# Let's inspect column darkness sum
col_sum = np.sum(darkness, axis=0)
print(f"Col sum min: {col_sum.min()}, max: {col_sum.max()}, mean: {col_sum.mean()}")

# Threshold for column having figure
threshold = 300  # adjust based on min/max
has_content = col_sum > threshold

# Let's find segments
segments = []
in_seg = False
start_x = 0

for x in range(w):
    if has_content[x] and not in_seg:
        in_seg = True
        start_x = x
    elif not has_content[x] and in_seg:
        in_seg = False
        if x - start_x > 25: # filter small noise
            segments.append((start_x, x))
if in_seg:
    segments.append((start_x, w))

print(f"Found {len(segments)} segments:")
for idx, (x1, x2) in enumerate(segments):
    print(f"  Segment {idx}: x={x1}..{x2} (width={x2-x1})")

# If segments is less or more than 8, let's print detailed column profile
