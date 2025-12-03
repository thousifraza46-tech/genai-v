"""
Test Backend Module Connections
Verifies all backend modules work correctly before starting the server
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all module imports"""
    print("=" * 60)
    print("TESTING MODULE IMPORTS")
    print("=" * 60)
    
    modules_to_test = {
        'chatbot_engine': 'generate_chatbot_response',
        'script_generator': 'ScriptGenerator',
        'audio_generator': 'AudioGenerator',
        'pexels_video_generator': 'PexelsVideoGenerator',
        'scene_builder': 'combine_videos'
    }
    
    results = {}
    
    for module_name, function_name in modules_to_test.items():
        try:
            module = __import__(module_name)
            if hasattr(module, function_name):
                print(f"✅ {module_name}.{function_name} - OK")
                results[module_name] = "PASS"
            else:
                print(f"❌ {module_name}.{function_name} - NOT FOUND")
                results[module_name] = "FAIL"
        except Exception as e:
            print(f"❌ {module_name} - IMPORT ERROR: {e}")
            results[module_name] = "ERROR"
    
    print()
    return results

def test_chatbot_engine():
    """Test chatbot engine"""
    print("=" * 60)
    print("TESTING CHATBOT ENGINE")
    print("=" * 60)
    
    try:
        from chatbot_engine import generate_chatbot_response
        
        # Test with simple conversation
        response = generate_chatbot_response(
            user_message="Hello, can you help me create a video?",
            conversation_history=[]
        )
        
        if response and len(response) > 0:
            print(f"✅ Chatbot response generated ({len(response)} chars)")
            print(f"   Sample: {response[:100]}...")
            return "PASS"
        else:
            print("❌ Empty response from chatbot")
            return "FAIL"
            
    except Exception as e:
        print(f"❌ Chatbot test failed: {e}")
        return "ERROR"

def test_script_generator():
    """Test script generator"""
    print("\n" + "=" * 60)
    print("TESTING SCRIPT GENERATOR")
    print("=" * 60)
    
    try:
        from script_generator import ScriptGenerator
        
        generator = ScriptGenerator()
        result = generator.generate_script(
            video_prompt="Ocean waves at sunset",
            duration=30
        )
        
        if result and 'script' in result and result['script']:
            print(f"✅ Script generated")
            print(f"   Words: {result.get('word_count', 'N/A')}")
            print(f"   Duration: {result.get('estimated_duration', 'N/A')}s")
            print(f"   Source: {result.get('source', 'N/A')}")
            print(f"   Sample: {result['script'][:100]}...")
            return "PASS"
        else:
            print("❌ Invalid script result")
            return "FAIL"
            
    except Exception as e:
        print(f"❌ Script generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"

def test_audio_generator():
    """Test audio generator"""
    print("\n" + "=" * 60)
    print("TESTING AUDIO GENERATOR")
    print("=" * 60)
    
    try:
        from audio_generator import AudioGenerator
        
        generator = AudioGenerator()
        
        test_script = "This is a test narration for our video generation system."
        
        result = generator.generate_audio(
            script=test_script,
            filename="test_connection"
        )
        
        if result and 'audio_path' in result:
            print(f"✅ Audio generation completed")
            print(f"   Path: {result.get('audio_path', 'N/A')}")
            print(f"   Duration: {result.get('duration', 'N/A')}s")
            print(f"   Source: {result.get('source', 'N/A')}")
            print(f"   Voice: {result.get('voice', 'N/A')}")
            return "PASS"
        else:
            print("❌ Invalid audio result")
            return "FAIL"
            
    except Exception as e:
        print(f"❌ Audio generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"

def test_pexels_generator():
    """Test Pexels image generator"""
    print("\n" + "=" * 60)
    print("TESTING PEXELS IMAGE GENERATOR")
    print("=" * 60)
    
    try:
        from pexels_video_generator import PexelsVideoGenerator
        
        generator = PexelsVideoGenerator()
        
        # Test image search
        images = generator.search_images(
            query="sunset ocean",
            count=3
        )
        
        if images and len(images) > 0:
            print(f"✅ Image search completed")
            print(f"   Found: {len(images)} images")
            for i, img in enumerate(images[:3]):
                print(f"   Image {i+1}: {img.get('id', 'N/A')} - {img.get('url', 'N/A')[:60]}...")
            return "PASS"
        else:
            print("⚠️  No images found (may need Pexels API key)")
            return "WARN"
            
    except Exception as e:
        print(f"❌ Pexels generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"

def test_scene_builder():
    """Test scene builder"""
    print("\n" + "=" * 60)
    print("TESTING SCENE BUILDER")
    print("=" * 60)
    
    try:
        from scene_builder import combine_videos, get_scene_info
        
        # Just test that functions exist and are callable
        print("✅ combine_videos function available")
        print("✅ get_scene_info function available")
        
        # Test get_scene_info with sample data
        sample_clips = [
            {'duration': 5, 'quality': 'HD'},
            {'duration': 8, 'quality': 'HD'},
            {'duration': 7, 'quality': 'SD'}
        ]
        
        info = get_scene_info(sample_clips)
        print(f"✅ Scene info calculation works")
        print(f"   Total clips: {info['clip_count']}")
        print(f"   Total duration: {info['total_duration']}s")
        
        return "PASS"
            
    except Exception as e:
        print(f"❌ Scene builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"

def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r == "PASS")
    warned = sum(1 for r in results.values() if r == "WARN")
    failed = sum(1 for r in results.values() if r in ["FAIL", "ERROR"])
    total = len(results)
    
    for module, status in results.items():
        icon = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
        print(f"{icon} {module}: {status}")
    
    print(f"\nTotal: {total} | Passed: {passed} | Warnings: {warned} | Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All critical tests passed! Backend is ready.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check errors above.")
        return False

if __name__ == "__main__":
    print("\n🔍 Backend Connection Test Suite\n")
    
    results = {}
    
    # Run all tests
    import_results = test_imports()
    results.update(import_results)
    
    results['chatbot_test'] = test_chatbot_engine()
    results['script_test'] = test_script_generator()
    results['audio_test'] = test_audio_generator()
    results['pexels_test'] = test_pexels_generator()
    results['scene_test'] = test_scene_builder()
    
    # Print summary
    success = print_summary(results)
    
    if success:
        print("\n✅ Backend is ready. You can now run:")
        print("   python backend/api_server.py")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
    
    sys.exit(0 if success else 1)
