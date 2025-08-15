# 🤖 RedMAG Chatbot - Demo en Google Colab

Este notebook de Google Colab te permite interactuar con el chatbot RedMAG de forma fácil y rápida, sin necesidad de configurar nada localmente.

## 🚀 Cómo Usar

### 1. Abrir el Notebook
- Ve a [Google Colab](https://colab.research.google.com/)
- Sube el archivo `redmag_chatbot_demo.ipynb`
- O copia y pega el contenido en un nuevo notebook

### 2. Configurar la URL de la API
Antes de usar el notebook, necesitas actualizar la URL de la API:

```python
API_BASE_URL = "https://tu-servicio-xxxxx-uc.a.run.app"
```

Reemplaza `tu-servicio-xxxxx-uc.a.run.app` con la URL real de tu servicio desplegado en Google Cloud Run.

### 3. Ejecutar las Celdas
1. **Ejecuta la primera celda** para instalar dependencias
2. **Ejecuta la segunda celda** para cargar el cliente
3. **Ejecuta la celda de verificación** para confirmar que la API funciona
4. **¡Comienza a chatear!**

## 🎮 Características del Demo

### Interfaz de Texto Simple
- **Botones**: Se muestran como opciones numeradas (1, 2, 3...)
- **Content Cards**: Se muestran con título, descripción, tipo y URL
- **Mensajes**: Formato claro y fácil de leer

### Comandos Disponibles
- **Números (1, 2, 3...)**: Seleccionar opciones del menú
- **Texto libre**: Enviar consultas personalizadas
- **'salir'**: Terminar la conversación

### Personalidad Jarvis
- Respuestas con personalidad de Iron Man
- Mensajes de bienvenida interactivos
- Recomendaciones de contenido educativo

## 📋 Ejemplos de Uso

### Ejemplo 1: Menú Principal
```
🤖 Jarvis: ¡Hola! Soy Jarvis, tu asistente educativo personal...

📋 Opciones disponibles:
   1. Buscar Planeaciones Didácticas
   2. Buscar MEDs (Materiales Educativos Digitales)
   3. Configurar Mi Perfil
   4. Escribir Consulta Personalizada

💡 Escribe el número de la opción que deseas seleccionar.

👤 Tú: 1
```

### Ejemplo 2: Content Cards
```
📚 Contenido recomendado:

   📖 1. Planeación de Matemáticas - Fracciones
      📝 Material completo para enseñar fracciones en primaria
      🏷️ Tipo: planeacion
      🔗 URL: https://ejemplo.com/planeacion-fracciones
      🏷️ Tags: matemáticas, fracciones, primaria
```

### Ejemplo 3: Configuración de Perfil
```
🤖 Jarvis: Perfecto, vamos a configurar tu perfil...

📋 Opciones disponibles:
   1. Soy docente de primaria
   2. Soy docente de secundaria
   3. Soy estudiante
   4. Soy padre de familia

👤 Tú: 1
```

## 🔧 Solución de Problemas

### Error de Conexión
Si ves este error:
```
❌ No se pudo conectar a la API
```

**Soluciones:**
1. Verifica que la URL en `API_BASE_URL` sea correcta
2. Asegúrate de que el servicio esté desplegado en Cloud Run
3. Verifica que el servicio esté funcionando

### Error de Respuesta
Si ves errores en las respuestas:
```
❌ Error 500: Internal Server Error
```

**Soluciones:**
1. Verifica los logs del servicio en Google Cloud Console
2. Asegúrate de que las credenciales estén configuradas
3. Verifica que BigQuery y Vertex AI estén funcionando

## 🎯 Ventajas del Demo

### Para Usuarios
- ✅ **Sin instalación**: Solo necesitas un navegador
- ✅ **Interfaz simple**: Fácil de usar
- ✅ **Acceso inmediato**: No requiere configuración
- ✅ **Gratuito**: Google Colab es gratuito

### Para Desarrolladores
- ✅ **Testing rápido**: Prueba la API fácilmente
- ✅ **Demo para clientes**: Muestra el funcionamiento
- ✅ **Debugging**: Identifica problemas rápidamente
- ✅ **Documentación**: Sirve como ejemplo de uso

## 🔗 Enlaces Útiles

- [Google Colab](https://colab.research.google.com/)
- [Google Cloud Run](https://cloud.google.com/run)
- [Documentación de la API](README.md)

## 📞 Soporte

Si tienes problemas:
1. Verifica que la API esté funcionando
2. Revisa los logs en Google Cloud Console
3. Asegúrate de que la URL sea correcta

---

**¡Disfruta probando el chatbot RedMAG! 🤖✨** 