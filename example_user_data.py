#!/usr/bin/env python3
"""
Ejemplo de cómo enviar datos de usuario correctamente a la API de MentorIA

Este archivo muestra la estructura correcta para enviar datos estructurados del usuario.
"""

import requests
import json
import uuid

# Configuration
API_BASE_URL = "https://redmag-chatbot-api-prod-324789362064.us-east1.run.app"
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

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

# Ejemplo 1: Datos básicos del perfil
def ejemplo_datos_basicos():
    """Ejemplo con datos básicos del perfil"""
    print("👤 === EJEMPLO 1: Datos Básicos ===")
    
    user_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    
    # ✅ CORRECTO: Mantener los tipos de datos originales
    user_data_list = [
        {"field": "name", "value": "María García"},
        {"field": "age", "value": 25},  # Número, no string
        {"field": "grade", "value": "3er año"},
        {"field": "subject", "value": "Matemáticas"},
        {"field": "learning_style", "value": "visual"}
    ]
    
    response = send_user_data(user_id, user_data_list, conversation_id)
    
    if response:
        print("✅ Datos enviados correctamente")
        print(f"🤖 Respuesta: {response.get('data', {}).get('message', 'Sin mensaje')}")
    else:
        print("❌ Error enviando datos")

# Ejemplo 2: Datos con listas
def ejemplo_datos_con_listas():
    """Ejemplo con datos que incluyen listas"""
    print("\n👤 === EJEMPLO 2: Datos con Listas ===")
    
    user_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    
    # ✅ CORRECTO: Listas se mantienen como listas
    user_data_list = [
        {"field": "name", "value": "Carlos López"},
        {"field": "age", "value": 30},
        {"field": "goals", "value": ["Mejorar en álgebra", "Entender geometría"]},  # Lista
        {"field": "subjects", "value": ["Matemáticas", "Física"]},  # Lista
        {"field": "preferences", "value": ["videos", "ejercicios", "explicaciones"]}  # Lista
    ]
    
    response = send_user_data(user_id, user_data_list, conversation_id)
    
    if response:
        print("✅ Datos con listas enviados correctamente")
        print(f"🤖 Respuesta: {response.get('data', {}).get('message', 'Sin mensaje')}")
    else:
        print("❌ Error enviando datos con listas")

# Ejemplo 3: Datos complejos
def ejemplo_datos_complejos():
    """Ejemplo con datos más complejos"""
    print("\n👤 === EJEMPLO 3: Datos Complejos ===")
    
    user_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    
    # ✅ CORRECTO: Diferentes tipos de datos
    user_data_list = [
        {"field": "name", "value": "Ana Rodríguez"},
        {"field": "age", "value": 28},
        {"field": "is_student", "value": True},  # Booleano
        {"field": "grade_level", "value": 5},  # Número
        {"field": "subjects", "value": ["Matemáticas", "Ciencias"]},  # Lista
        {"field": "learning_preferences", "value": {
            "visual": True,
            "auditory": False,
            "kinesthetic": True
        }},  # Diccionario (se convertirá a string automáticamente)
        {"field": "goals", "value": ["Aprobar el examen", "Entender conceptos básicos"]}
    ]
    
    response = send_user_data(user_id, user_data_list, conversation_id)
    
    if response:
        print("✅ Datos complejos enviados correctamente")
        print(f"🤖 Respuesta: {response.get('data', {}).get('message', 'Sin mensaje')}")
    else:
        print("❌ Error enviando datos complejos")

# ❌ EJEMPLO INCORRECTO (para comparar)
def ejemplo_incorrecto():
    """Ejemplo de cómo NO enviar datos"""
    print("\n❌ === EJEMPLO INCORRECTO ===")
    
    user_id = str(uuid.uuid4())
    conversation_id = str(uuid.uuid4())
    
    # ❌ INCORRECTO: Convertir todo a string
    user_data = {
        "name": "María García",
        "age": 25,
        "grade": "3er año",
        "subject": "Matemáticas",
        "learning_style": "visual",
        "goals": ["Mejorar en álgebra", "Entender geometría"]
    }
    
    # ❌ Esto causará error 422
    data_list = []
    for key, value in user_data.items():
        data_list.append({"field": str(key), "value": str(value)})  # Todo a string
    
    print("❌ Este enfoque causará error 422")
    print("❌ Las listas se convierten a string: ['Mejorar en álgebra', 'Entender geometría']")
    print("❌ Los números se convierten a string: 25 -> '25'")

if __name__ == "__main__":
    print("🚀 === EJEMPLOS DE ENVÍO DE DATOS DE USUARIO ===")
    print("=" * 60)
    
    # Mostrar ejemplo incorrecto
    ejemplo_incorrecto()
    
    # Mostrar ejemplos correctos
    ejemplo_datos_basicos()
    ejemplo_datos_con_listas()
    ejemplo_datos_complejos()
    
    print("\n🎯 === RESUMEN ===")
    print("✅ Mantén los tipos de datos originales")
    print("✅ Las listas deben seguir siendo listas")
    print("✅ Los números deben seguir siendo números")
    print("✅ Solo convierte a string cuando sea necesario")
    print("❌ No conviertas todo a string automáticamente") 