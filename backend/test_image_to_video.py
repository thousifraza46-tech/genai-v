"""
Test script for Image-to-Video conversion with fallback
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from PIL import Image
import io

# Create a simple test image
print("Creating test image...")
img = Image.new('RGB', (1024, 576), color=(70, 130, 180))
# Add some visual content
from PIL import ImageDraw, ImageFont
draw = ImageDraw.Draw(img)
draw.rectangle([100, 100, 924, 476], fill=(100, 200, 100), outline=(255, 255, 255), width=5)
draw.ellipse([300, 200, 724, 376], fill=(200, 100, 100), outline=(255, 255, 255), width=3)

# Save test image
test_image_path = "test_input.png"
img.save(test_image_path)
print(f"✅ Test image saved: {test_image_path}")

# Test the HuggingFace service
print("\n" + "="*60)
print("Testing HuggingFace Image-to-Video Service")
print("="*60)

try:
    from huggingface_service import HuggingFaceService
    
    hf = HuggingFaceService()
    print("✅ Service initialized successfully!")
    
    print("\nAttempting to convert image to video...")
    print("This will use fallback method if HuggingFace API fails...")
    
    output_path = hf.image_to_video(test_image_path, output_path="test_output_video.mp4")
    
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"\n✅ SUCCESS! Video generated: {output_path}")
        print(f"   File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        print(f"\n🎬 You can play the video with: {output_path}")
    else:
        print(f"\n❌ FAILED: Output file not found")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

