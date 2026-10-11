from PIL import Image
import numpy as np

src_image_path = r"C:\Users\vitor.henrique\.gemini\antigravity\brain\22fbd3a0-fb8b-4bc3-b93d-afdfef91713c\.user_uploaded\media_1791570732231_a7e05cd4.png"
img = Image.open(src_image_path)
arr = np.array(img)
alpha = arr[:, :, 3]

print("Alpha shape:", alpha.shape)
print("Alpha min:", alpha.min(), "max:", alpha.max())

# Max alpha per column
col_alpha = np.max(alpha, axis=0)

# Segments where col_alpha > 0
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

print(f"Found {len(segments)} segments:")
for idx, (x1, x2) in enumerate(segments):
    print(f"  Frame {idx}: x1={x1}, x2={x2}, w={x2-x1}")
