from PIL import Image
import numpy as np

src_image_path = r"C:\Users\vitor.henrique\.gemini\antigravity\brain\22fbd3a0-fb8b-4bc3-b93d-afdfef91713c\.user_uploaded\media_1791570732231_a7e05cd4.png"
img = Image.open(src_image_path)
print("Format:", img.format, "Mode:", img.mode, "Size:", img.size)

arr = np.array(img)
print("Shape:", arr.shape, "Dtype:", arr.dtype)
print("Min per channel:", np.min(arr, axis=(0,1)))
print("Max per channel:", np.max(arr, axis=(0,1)))
print("Top-left 5x5 pixel values:\n", arr[0:5, 0:5])
