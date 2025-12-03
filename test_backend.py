import requests
import json

BASE_URL = "http://localhost:5000/api"

print("Testing Backend Endpoints...")
print("=" * 50)

# Test 1: Health Check
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"✅ Health Check: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Health Check Failed: {e}")

print()

# Test 2: Script Generation
try:
    data = {"prompt": "beautiful sunset over ocean", "duration": 30}
    response = requests.post(f"{BASE_URL}/generate/script", json=data, timeout=15)
    print(f"✅ Script Generation: {response.status_code}")
    result = response.json()
    if 'script' in result:
        print(f"   Script length: {len(result['script'])} chars")
        print(f"   Word count: {result.get('word_count', 'N/A')}")
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")
except Exception as e:
    print(f"❌ Script Generation Failed: {e}")

print()

# Test 3: Image Generation
try:
    data = {"prompt": "beautiful sunset", "count": 3}
    response = requests.post(f"{BASE_URL}/generate/images", json=data, timeout=15)
    print(f"✅ Image Generation: {response.status_code}")
    result = response.json()
    if 'images' in result:
        print(f"   Images found: {len(result['images'])}")
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")
except Exception as e:
    print(f"❌ Image Generation Failed: {e}")

print()

# Test 4: Video Fetching
try:
    data = {"prompt": "ocean waves", "count": 5}
    response = requests.post(f"{BASE_URL}/generate/videos", json=data, timeout=15)
    print(f"✅ Video Fetching: {response.status_code}")
    result = response.json()
    if 'videos' in result:
        print(f"   Videos found: {len(result['videos'])}")
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")
except Exception as e:
    print(f"❌ Video Fetching Failed: {e}")

print()
print("=" * 50)
print("Backend testing complete!")
