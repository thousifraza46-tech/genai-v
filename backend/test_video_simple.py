import sys
import os
sys.path.append(os.path.dirname(__file__))

from PIL import Image
from huggingface_service import HuggingFaceService

# Create test image
print("Creating test image...")
img = Image.new('RGB', (512, 512), color=(100, 150, 200))
img.save("test_img.png")
print("Test image saved: test_img.png")

# Test service
print("\nTesting HuggingFace service...")
hf = HuggingFaceService()
result = hf.image_to_video("test_img.png", "output_test.mp4")
print(f"\nResult: {result}")

if os.path.exists(result):
    size = os.path.getsize(result)
    print(f"SUCCESS! Video file: {result} ({size:,} bytes)")
else:
    print("FAILED: No output file")
