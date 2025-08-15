#!/usr/bin/env python3
"""
Test script for MentorIA Chatbot API

This script tests the chatbot flow with different types of interactions.
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration
API_BASE_URL = "https://redmag-chatbot-api-prod-324789362064.us-east1.run.app"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Generate test IDs
user_id = str(uuid.uuid4())
conversation_id = str(uuid.uuid4())

print("🚀 === MENTORIA CHATBOT API TEST ===")
print(f"🌐 API URL: {API_BASE_URL}")
print(f"👤 User ID: {user_id[:8]}...")
print(f"💬 Conversation ID: {conversation_id[:8]}...")
print("=" * 60)

# Test 1: Health check
print("🏥 === TEST 1: Health Check ===")
print("-" * 30)

try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=10)
    if response.status_code == 200:
        print("✅ Health check passed")
        print(f"📊 Status: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        print(f"📝 Response: {response.text}")
except Exception as e:
    print(f"❌ Error in health check: {str(e)}")

print()

# Test 2: Root endpoint
print("🏠 === TEST 2: Root Endpoint ===")
print("-" * 30)

try:
    response = requests.get(f"{API_BASE_URL}/", timeout=10)
    if response.status_code == 200:
        print("✅ Root endpoint working")
        print(f"📊 Response: {response.json()}")
    else:
        print(f"❌ Root endpoint failed: {response.status_code}")
        print(f"📝 Response: {response.text}")
except Exception as e:
    print(f"❌ Error in root endpoint: {str(e)}")

print()

# Funciones para interactuar con el chatbot
def send_chat_message(user_id, message, conversation_id=None):
    """Envía un mensaje al chatbot"""
    payload = {
        "user_id": user_id,
        "message": message
    }
    
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat", 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error en la petición: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error enviando mensaje: {str(e)}")
        return None

def send_user_data(user_id, user_data_list, conversation_id=None):
    """Envía datos estructurados del usuario"""
    payload = {
        "user_id": user_id,
        "user_data": user_data_list
    }
    
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat", 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error en la petición: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error enviando datos: {str(e)}")
        return None

print("✅ Funciones de chat configuradas")

# Test 3: Mensaje simple
print("💬 === TEST 3: Mensaje Simple ===")
print("-" * 30)

response = send_chat_message(user_id, "Hola, ¿qué es MentorIA?", conversation_id)

if response:
    print(f"🤖 Respuesta: {response.get('data', {}).get('message', 'Sin mensaje')}")
    print(f"📋 Tipo de respuesta: {response.get('response_type', 'unknown')}")
    print(f"💬 Conversation ID: {response.get('conversation_id', 'N/A')}")
    
    # Update conversation_id if returned
    if response.get('conversation_id'):
        conversation_id = response.get('conversation_id')
else:
    print("❌ No se pudo enviar el mensaje")

print()

# Test 4: Datos del usuario (estructura correcta)
print("👤 === TEST 4: Datos del Usuario ===")
print("-" * 30)

if conversation_id:
    # Estructura correcta: lista de UserDataInput objects
    # Mantener los tipos de datos originales, no convertir todo a string
    user_data_list = [
        {"field": "name", "value": "María García"},
        {"field": "age", "value": 25},  # Mantener como número
        {"field": "grade", "value": "3er año"},
        {"field": "subject", "value": "Matemáticas"},
        {"field": "learning_style", "value": "visual"},
        {"field": "goals", "value": ["Mejorar en álgebra", "Entender geometría"]}  # Mantener como lista
    ]
    
    response = send_user_data(user_id, user_data_list, conversation_id)
    
    if response:
        print(f"👤 Datos enviados: {len(user_data_list)} campos")
        print(f"🤖 Respuesta: {response.get('data', {}).get('message', 'Sin mensaje')}")
        print(f"📋 Tipo de respuesta: {response.get('response_type', 'unknown')}")
    else:
        print("❌ No se pudo enviar los datos del usuario")
else:
    print("❌ No hay conversation_id disponible")

print()

# Test 5: Pregunta específica
print("❓ === TEST 5: Pregunta Específica ===")
print("-" * 30)

response = send_chat_message(user_id, "Necesito ayuda con ecuaciones cuadráticas", conversation_id)

if response:
    print(f"🤖 Respuesta: {response.get('data', {}).get('message', 'Sin mensaje')}")
    print(f"📋 Tipo de respuesta: {response.get('response_type', 'unknown')}")
    
    # Si hay botones, mostrarlos
    if response.get('response_type') == 'buttons':
        buttons = response.get('data', {}).get('buttons', [])
        print(f"📋 Botones disponibles: {len(buttons)}")
        for i, button in enumerate(buttons, 1):
            print(f"  {i}. {button.get('text', 'Sin texto')}")
else:
    print("❌ No se pudo enviar la pregunta")

print()

# Test 6: Solicitar contenido
print("📚 === TEST 6: Solicitar Contenido ===")
print("-" * 30)

response = send_chat_message(user_id, "Muéstrame contenido sobre matemáticas", conversation_id)

if response:
    print(f"🤖 Respuesta: {response.get('data', {}).get('message', 'Sin mensaje')}")
    print(f"📋 Tipo de respuesta: {response.get('response_type', 'unknown')}")
    
    # Si hay tarjetas de contenido, mostrarlas
    if response.get('response_type') == 'content_cards':
        cards = response.get('data', {}).get('cards', [])
        print(f"📚 Tarjetas de contenido: {len(cards)}")
        for i, card in enumerate(cards, 1):
            print(f"  📄 Tarjeta {i}: {card.get('title', 'Sin título')}")
else:
    print("❌ No se pudo solicitar contenido")

print()

print("🎯 === RESUMEN DE PRUEBAS ===")
print("-" * 30)
print(f"✅ Tests completados para usuario: {user_id[:8]}...")
print(f"✅ Conversation ID final: {conversation_id[:8]}...")
print(f"✅ API URL: {API_BASE_URL}")
print("🎉 ¡Pruebas terminadas!") 