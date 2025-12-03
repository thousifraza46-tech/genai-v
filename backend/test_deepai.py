import sys
import os
sys.path.append('.')

from PIL import Image
from huggingface_service import HuggingFaceService

# Create test image
print("Creating test image...")
img = Image.new('RGB', (512, 512), color=(100, 150, 200))
img.save("test_deepai_input.png")
print("✅ Test image saved: test_deepai_input.png")

# Test DeepAI service
print("\n" + "="*60)
print("Testing DeepAI Image-to-Video Service")
print("="*60)

hf = HuggingFaceService()
print("\nGenerating video...")
result = hf.image_to_video("test_deepai_input.png", "test_deepai_output.mp4")

print(f"\n{'='*60}")
if result and os.path.exists(result):
    import os
    size = os.path.getsize(result)
    print(f"✅ SUCCESS! Video generated: {result}")
    print(f"   File size: {size:,} bytes ({size/1024/1024:.2f} MB)")
else:
    print(f"❌ FAILED: {result}")
