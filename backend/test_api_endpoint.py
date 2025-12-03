import requests
from PIL import Image
import os

# Create test image
print("Creating test image...")
img = Image.new('RGB', (512, 512), color=(100, 150, 200))
img.save("test_upload.png")
print("OK Test image created: test_upload.png")

# Test API endpoint
print("\nTesting /api/huggingface/image-to-video endpoint...")
url = "http://localhost:5000/api/huggingface/image-to-video"

with open("test_upload.png", "rb") as f:
    files = {"image": f}
    response = requests.post(url, files=files, timeout=60)

print(f"\nResponse status: {response.status_code}")

if response.status_code == 200:
    # Save video
    with open("test_api_output.mp4", "wb") as f:
        f.write(response.content)
    
    size = os.path.getsize("test_api_output.mp4")
    print(f"SUCCESS! Video saved: test_api_output.mp4")
    print(f"   File size: {size:,} bytes ({size/1024/1024:.2f} MB)")
else:
    print(f"FAILED!")
    print(f"Response: {response.text[:500]}")
