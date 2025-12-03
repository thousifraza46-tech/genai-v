import requests
import json

# Test the chatbot API endpoint
url = "http://localhost:5000/api/chat"
data = {
    "message": "Hello! Can you help me create a video?",
    "sessionId": "test_api_session"
}

print("🧪 Testing Chatbot API with Gen AI...\n")
print(f"URL: {url}")
print(f"Message: {data['message']}\n")

try:
    response = requests.post(url, json=data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Response received:")
        print(f"\nBot: {result['response']}\n")
        print(f"Session ID: {result['session_id']}")
        print(f"Status: {response.status_code} OK")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("\nMake sure backend is running on http://localhost:5000")
