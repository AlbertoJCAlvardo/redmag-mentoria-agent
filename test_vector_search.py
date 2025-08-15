#!/usr/bin/env python3
"""
Test script for Vector Search functionality

This script tests the vector search adapter to ensure it works correctly.
"""

import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_vector_search():
    """Test vector search functionality"""
    try:
        from adapters.vector_search_adapter import VectorSearchAdapter
        from config import config
        
        print("🧪 === TESTING VECTOR SEARCH ===")
        print(f"🌐 Project ID: {config.project_id}")
        print(f"🔍 Index ID: {config.index_id}")
        print(f"🔗 Endpoint ID: {config.endpoint_id}")
        print(f"📊 Deployed Index ID: {config.deployed_index_id}")
        
        # Crear instancia del adaptador
        print("\n🔧 Initializing VectorSearchAdapter...")
        adapter = VectorSearchAdapter()
        
        if adapter.is_initialized:
            print("✅ VectorSearchAdapter initialized successfully")
            
            # Test 1: Búsqueda simple
            print("\n🔍 Test 1: Simple search")
            query = "ecuaciones cuadráticas"
            results = adapter.search_similar(query, num_neighbors=3)
            
            print(f"📊 Found {len(results)} results")
            for i, result in enumerate(results):
                print(f"  {i+1}. ID: {result.get('id', 'N/A')}")
                print(f"     Distance: {result.get('distance', 'N/A')}")
                print(f"     Metadata: {result.get('metadata', {})}")
                print()
            
            # Test 2: Información del índice
            print("📋 Test 2: Index information")
            index_info = adapter.get_index_info()
            print(f"📊 Index info: {index_info}")
            
            # Test 3: Estadísticas del índice
            print("\n📈 Test 3: Index statistics")
            index_stats = adapter.get_index_stats()
            print(f"📊 Index stats: {index_stats}")
            
        else:
            print("⚠️ VectorSearchAdapter not initialized")
            print("🔧 This is normal if configuration is missing")
            
            # Test fallback
            print("\n🔄 Testing fallback functionality...")
            query = "ecuaciones cuadráticas"
            results = adapter.search_similar(query, num_neighbors=3)
            
            print(f"📊 Generated {len(results)} fallback results")
            for i, result in enumerate(results):
                print(f"  {i+1}. ID: {result.get('id', 'N/A')}")
                print(f"     Distance: {result.get('distance', 'N/A')}")
                print(f"     Metadata: {result.get('metadata', {})}")
                print()
        
        print("\n✅ Vector search test completed")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure you're running from the correct directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Test failed")

def test_gemini_adapter():
    """Test Gemini adapter functionality"""
    try:
        from adapters.gemini_adapter import GeminiAdapter
        
        print("\n🧪 === TESTING GEMINI ADAPTER ===")
        
        # Crear instancia del adaptador
        print("🔧 Initializing GeminiAdapter...")
        adapter = GeminiAdapter()
        
        print("✅ GeminiAdapter initialized successfully")
        
        # Test: Routing plan
        print("\n🔍 Test: Routing plan generation")
        user_message = "Necesito ayuda con ecuaciones cuadráticas"
        user_profile = {
            "name": "María García",
            "age": 25,
            "grade": "3er año",
            "subject": "Matemáticas"
        }
        conversation_context = {}
        
        routing_plan = adapter.get_routing_plan(user_message, user_profile, conversation_context)
        
        if routing_plan:
            print("✅ Routing plan generated successfully")
            print(f"📊 Intent: {routing_plan.get('intent', 'N/A')}")
            print(f"📋 Action type: {routing_plan.get('action', {}).get('type', 'N/A')}")
        else:
            print("❌ Failed to generate routing plan")
        
        print("\n✅ Gemini adapter test completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Gemini test failed")

if __name__ == "__main__":
    print("🚀 Starting Vector Search Tests")
    print("=" * 50)
    
    test_vector_search()
    test_gemini_adapter()
    
    print("\n🎉 All tests completed!") 