#!/usr/bin/env python3
"""
Script para generar token de autenticación UUID4 para la API de MentorIA

Este script genera un token único que se puede usar para autenticación en la API.
"""

import uuid
import os
from datetime import datetime

def generate_api_token():
    """Genera un token UUID4 para autenticación de la API"""
    return str(uuid.uuid4())

def update_env_file(token):
    """Actualiza el archivo .env con el nuevo token"""
    env_file = ".env"
    
    # Leer archivo .env existente si existe
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Actualizar o agregar el token
    env_vars['API_TOKEN'] = token
    env_vars['REQUIRE_AUTH'] = 'true'
    
    # Escribir archivo .env actualizado
    with open(env_file, 'w') as f:
        f.write("# MentorIA API Configuration\n")
        f.write(f"# Generated on: {datetime.now().isoformat()}\n\n")
        
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Token actualizado en {env_file}")

def main():
    """Función principal"""
    print("🔐 === GENERADOR DE TOKEN PARA MENTORIA API ===")
    print("=" * 50)
    
    # Generar token
    token = generate_api_token()
    
    print(f"🎯 Token generado: {token}")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Mostrar instrucciones
    print("📋 INSTRUCCIONES DE USO:")
    print("1. Copia el token generado arriba")
    print("2. Configúralo en tu entorno de Cloud Run:")
    print(f"   gcloud run services update redmag-chatbot-api-prod \\")
    print(f"     --region=us-east1 \\")
    print(f"     --set-env-vars=API_TOKEN={token}")
    print()
    print("3. En Postman, actualiza la variable 'api_token' con este valor")
    print("4. Usa el token en el header Authorization: Bearer <token>")
    print()
    
    # Actualizar archivo .env local si existe
    if os.path.exists(".env"):
        update_env_file(token)
        print("📝 Archivo .env actualizado localmente")
    else:
        print("📝 Para crear archivo .env local, ejecuta:")
        print(f"   echo 'API_TOKEN={token}' > .env")
        print(f"   echo 'REQUIRE_AUTH=true' >> .env")
    
    print()
    print("🔧 CONFIGURACIÓN DE POSTMAN:")
    print("1. Abre la colección 'MentorIA Chatbot API'")
    print("2. Ve a Variables de colección")
    print("3. Actualiza 'api_token' con el valor generado")
    print("4. ¡Listo para usar!")
    
    print()
    print("⚠️  IMPORTANTE:")
    print("- Guarda este token en un lugar seguro")
    print("- No lo compartas públicamente")
    print("- Puedes regenerarlo ejecutando este script nuevamente")
    print("- El token es válido hasta que lo cambies")
    
    print()
    print("🎉 ¡Token generado exitosamente!")

if __name__ == "__main__":
    main() 