#!/usr/bin/env python3
"""
Test script for Conversation Management endpoints

This script tests the new conversation management endpoints to ensure they work correctly.
"""

import os
import sys
import requests
import json
import uuid
from datetime import datetime

# Configuración
BASE_URL = "https://redmag-chatbot-api-prod-324789362064.us-east1.run.app"
USER_ID = str(uuid.uuid4())
CONVERSATION_ID = str(uuid.uuid4())

def test_health_check():
    """Test health check endpoint"""
    print("🏥 === TESTING HEALTH CHECK ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat_interaction():
    """Test basic chat interaction to create conversation data"""
    print("\n💬 === TESTING CHAT INTERACTION ===")
    try:
        payload = {
            "user_id": USER_ID,
            "conversation_id": CONVERSATION_ID,
            "message": "Hola, ¿qué es MentorIA?"
        }
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat interaction successful")
            print(f"Response type: {data.get('response_type')}")
            return True
        else:
            print(f"❌ Chat interaction failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat interaction error: {e}")
        return False

def test_get_conversation_messages():
    """Test getting conversation messages"""
    print("\n📝 === TESTING GET CONVERSATION MESSAGES ===")
    try:
        response = requests.get(
            f"{BASE_URL}/conversations/{CONVERSATION_ID}/messages?page=1&size=8",
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get messages successful")
            print(f"Total messages: {data.get('total', 0)}")
            print(f"Page: {data.get('page', 0)}")
            print(f"Size: {data.get('size', 0)}")
            print(f"Has next: {data.get('has_next', False)}")
            print(f"Has previous: {data.get('has_previous', False)}")
            return True
        else:
            print(f"❌ Get messages failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get messages error: {e}")
        return False

def test_get_latest_conversation():
    """Test getting latest conversation for user"""
    print("\n🔄 === TESTING GET LATEST CONVERSATION ===")
    try:
        response = requests.get(
            f"{BASE_URL}/users/{USER_ID}/latest-conversation",
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get latest conversation successful")
            print(f"Conversation ID: {data.get('conversation_id')}")
            print(f"User ID: {data.get('user_id')}")
            print(f"Message count: {data.get('message_count', 0)}")
            print(f"Is active: {data.get('is_active', False)}")
            return True
        else:
            print(f"❌ Get latest conversation failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get latest conversation error: {e}")
        return False

def test_get_conversation_info():
    """Test getting conversation information"""
    print("\nℹ️ === TESTING GET CONVERSATION INFO ===")
    try:
        response = requests.get(
            f"{BASE_URL}/conversations/{CONVERSATION_ID}",
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get conversation info successful")
            print(f"Conversation ID: {data.get('conversation_id')}")
            print(f"User ID: {data.get('user_id')}")
            print(f"Message count: {data.get('message_count', 0)}")
            print(f"Is active: {data.get('is_active', False)}")
            return True
        else:
            print(f"❌ Get conversation info failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get conversation info error: {e}")
        return False

def test_content_creation_redirect():
    """Test content creation redirect functionality"""
    print("\n🔗 === TESTING CONTENT CREATION REDIRECT ===")
    try:
        payload = {
            "user_id": USER_ID,
            "conversation_id": str(uuid.uuid4()),
            "message": "¿Cómo puedo crear una planeación?"
        }
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Content creation redirect successful")
            print(f"Response type: {data.get('response_type')}")
            
            if data.get('response_type') == 'content_cards':
                content_cards = data.get('data', {}).get('content_cards', [])
                print(f"Number of redirect cards: {len(content_cards)}")
                for card in content_cards:
                    print(f"  - {card.get('title')}: {card.get('url')}")
            return True
        else:
            print(f"❌ Content creation redirect failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Content creation redirect error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 === CONVERSATION ENDPOINTS TEST ===")
    print(f"Base URL: {BASE_URL}")
    print(f"User ID: {USER_ID}")
    print(f"Conversation ID: {CONVERSATION_ID}")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Chat Interaction", test_chat_interaction),
        ("Get Conversation Messages", test_get_conversation_messages),
        ("Get Latest Conversation", test_get_latest_conversation),
        ("Get Conversation Info", test_get_conversation_info),
        ("Content Creation Redirect", test_content_creation_redirect),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 === TEST RESULTS ===")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The conversation endpoints are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 