"""
Chat service for MentorIA Chatbot API.

Handles business logic for chat interactions and hierarchical agent orchestration.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from src.adapters.bigquery_adapter import BigQueryAdapter
from src.adapters.vector_search_adapter import VectorSearchAdapter
from src.adapters.gemini_adapter import GeminiAdapter
from src.adapters.agents.welcome_agent import WelcomeAgent
from src.models.request_models import UserDataInput

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions with hierarchical agents."""

    def __init__(self):
        """Initialize ChatService with required adapters."""
        self.bq_adapter = BigQueryAdapter()
        self.vector_adapter = VectorSearchAdapter()
        self.gemini_adapter = GeminiAdapter()
        self.welcome_agent = WelcomeAgent()
        logger.info("ChatService initialized with all adapters")

    async def handle_interaction(
        self, 
        user_id: str, 
        conversation_id: str, 
        message: Optional[str], 
        user_data_input: Optional[List[UserDataInput]]
    ) -> Dict[str, Any]:
        """
        Handle user interaction through hierarchical agent system.
        
        Args:
            user_id: Unique user identifier
            conversation_id: Conversation session ID
            message: User text message
            user_data_input: Structured data from user buttons
            
        Returns:
            Response data with type and content
        """
        self._log_user_input(conversation_id, user_id, message, user_data_input)
        
        user_profile = self.bq_adapter.get_user_profile(user_id) or {}
        
        # Asegurar que user_profile sea un diccionario
        if isinstance(user_profile, str):
            try:
                import json
                user_profile = json.loads(user_profile)
                logger.info(f"Deserialized user_profile from string: {user_profile}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to deserialize user_profile: {e}")
                user_profile = {}
        
        if not isinstance(user_profile, dict):
            logger.warning(f"user_profile is not a dict: {type(user_profile)}, converting to empty dict")
            user_profile = {}
            
        logger.info(f"DEBUG - user_profile: {user_profile}, type: {type(user_profile)}")
        
        conversation_context = self.bq_adapter.get_conversation_context(conversation_id) or {}
        
        # Asegurar que conversation_context sea un diccionario
        if isinstance(conversation_context, str):
            try:
                import json
                conversation_context = json.loads(conversation_context)
                logger.info(f"Deserialized conversation_context from string: {conversation_context}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to deserialize conversation_context: {e}")
                conversation_context = {}
        
        if not isinstance(conversation_context, dict):
            logger.warning(f"conversation_context is not a dict: {type(conversation_context)}, converting to empty dict")
            conversation_context = {}

        # Debug: Imprimir información del contexto
        logger.info(f"DEBUG - conversation_context: {conversation_context}")
        logger.info(f"DEBUG - conversation_context type: {type(conversation_context)}")
        if isinstance(conversation_context, dict):
            logger.info(f"DEBUG - history: {conversation_context.get('history')}")
            logger.info(f"DEBUG - history length: {len(conversation_context.get('history', []))}")
            logger.info(f"DEBUG - history is empty: {not conversation_context.get('history')}")
        else:
            logger.info(f"DEBUG - conversation_context is not a dict")

        # Verificar si es la primera interacción (conversación vacía)
        if (not conversation_context or 
            not isinstance(conversation_context, dict) or 
            not conversation_context.get("history")):
            
            # Mostrar mensaje de bienvenida con opciones
            welcome_response = self.welcome_agent.build_welcome_response(user_profile)
            welcome_response["conversation_id"] = conversation_id
            
            # Inicializar contexto de conversación
            initial_context = {
                "history": [
                    {"role": "assistant", "content": welcome_response["data"]["message"], "type": "welcome"}
                ],
                "message_count": 1,
                "welcome_shown": True
            }
            self.bq_adapter.update_conversation_context(conversation_id, user_id, initial_context)
            
            # Guardar el mensaje de bienvenida en la tabla messages
            self._log_assistant_response(conversation_id, user_id, welcome_response)
            
            return welcome_response

        # Verificar si la conversación ha alcanzado el límite de mensajes
        message_count = conversation_context.get("message_count", 0) if isinstance(conversation_context, dict) else 0
        if message_count >= self.gemini_adapter.config.max_messages_per_conversation:
            # Crear nueva conversación
            import uuid
            new_conversation_id = str(uuid.uuid4())
            conversation_context = {"message_count": 0}
            conversation_id = new_conversation_id
            logger.info(f"Conversación anterior alcanzó límite de {self.gemini_adapter.config.max_messages_per_conversation} mensajes. Nueva conversación: {conversation_id}")

        # Procesar input del usuario (mensaje de texto o datos estructurados)
        if user_data_input:
            # Verificar si es una selección del menú principal
            for item in user_data_input:
                if item.field == "menu_option":
                    if item.value == "perfil":
                        # Mostrar configuración de perfil
                        profile_response = self.welcome_agent.build_profile_setup_response()
                        profile_response["conversation_id"] = conversation_id
                        
                        # Actualizar contexto con la selección del usuario y la respuesta
                        updated_context = self._update_conversation_history(
                            conversation_context, 
                            {"intent": "configurar_perfil", "selected_option": item.value}, 
                            f"Seleccionó: {item.value}"
                        )
                        self.bq_adapter.update_conversation_context(conversation_id, user_id, updated_context)
                        
                        # Guardar la respuesta en la tabla messages
                        self._log_assistant_response(conversation_id, user_id, profile_response)
                        
                        return profile_response
                    elif item.value == "otro":
                        # Mostrar opción para escribir consulta personalizada
                        custom_response = self.welcome_agent.build_custom_query_response()
                        custom_response["conversation_id"] = conversation_id
                        
                        # Actualizar contexto con la selección del usuario y la respuesta
                        updated_context = self._update_conversation_history(
                            conversation_context, 
                            {"intent": "consulta_personalizada", "selected_option": item.value}, 
                            f"Seleccionó: {item.value}"
                        )
                        self.bq_adapter.update_conversation_context(conversation_id, user_id, updated_context)
                        
                        # Guardar la respuesta en la tabla messages
                        self._log_assistant_response(conversation_id, user_id, custom_response)
                        
                        return custom_response
                    else:
                        # Procesar otras opciones del menú - generar consultas específicas para contenido
                        if item.value in ["planeaciones", "meds", "evaluacion", "metodologias", "programas"]:
                            # Generar consulta específica según la selección
                            content_queries = {
                                "planeaciones": "planeaciones didácticas para educación",
                                "meds": "materiales educativos digitales",
                                "evaluacion": "herramientas de evaluación educativa",
                                "metodologias": "metodologías de enseñanza",
                                "programas": "programas analíticos educativos"
                            }
                            message_for_llm = f"Buscar {content_queries.get(item.value, item.value)}"
                        else:
                            message_for_llm = f"El usuario seleccionó: {item.value}"
                        
                        # Actualizar contexto con la selección
                        updated_context = self._update_conversation_history(
                            conversation_context, 
                            {"intent": "menu_selection", "selected_option": item.value}, 
                            f"Seleccionó: {item.value}"
                        )
                        self.bq_adapter.update_conversation_context(conversation_id, user_id, updated_context)
                        break
            else:
                # Actualizar perfil si son datos de perfil
                updated_fields = {item.field: item.value for item in user_data_input}
                user_profile.update(updated_fields)
                self.bq_adapter.update_user_profile(user_id, user_profile)
                
                # Actualizar contexto con los datos del perfil
                # Convertir valores a string de manera segura
                field_strings = []
                for k, v in updated_fields.items():
                    if isinstance(v, list):
                        field_strings.append(f"{k}=[{', '.join(map(str, v))}]")
                    else:
                        field_strings.append(f"{k}={v}")
                
                updated_context = self._update_conversation_history(
                    conversation_context, 
                    {"intent": "profile_update", "updated_fields": updated_fields}, 
                    f"Actualizó perfil: {', '.join(field_strings)}"
                )
                self.bq_adapter.update_conversation_context(conversation_id, user_id, updated_context)
                
                message_for_llm = conversation_context.get("last_user_prompt_for_buttons", "Continuar")
        else:
            message_for_llm = message

        # Si no hay mensaje para procesar, devolver error
        if not message_for_llm:
            return self._generate_error_response("No se recibió un mensaje válido para procesar")

        # Procesar mensaje a través del sistema de agentes
        routing_plan = self.gemini_adapter.get_routing_plan(
            message_for_llm, user_profile, conversation_context
        )

        if not routing_plan:
            return self._generate_error_response("No pude entender tu solicitud")

        response = await self._execute_plan(routing_plan, message_for_llm, user_profile)

        # Actualizar contexto con la interacción completa
        final_plan = response.get("final_plan", routing_plan)
        
        # Enriquecer el plan con información contextual
        enriched_plan = {
            "intent": final_plan.get("intent"),
            "analysis": final_plan.get("analysis"),
            "action_type": final_plan.get("action", {}).get("type"),
            "context_to_remember": final_plan.get("context_to_remember", {})
        }
        
        # Añadir información contextual específica según el tipo de respuesta
        if response.get("response_type") == "text":
            enriched_plan["response_type"] = "text_response"
        elif response.get("response_type") == "content_cards":
            enriched_plan["response_type"] = "search_results"
            
        updated_context = self._update_conversation_history(conversation_context, enriched_plan, message_for_llm)
        self.bq_adapter.update_conversation_context(conversation_id, user_id, updated_context)
        self._log_assistant_response(conversation_id, user_id, response)
        
        # Incluir el conversation_id en la respuesta para que el frontend sepa si cambió
        response["conversation_id"] = conversation_id
        
        return response

    async def _execute_plan(
        self, 
        plan: Dict[str, Any], 
        original_query: str, 
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the routing plan from the hierarchical agent system."""
        action_type = plan.get("action", {}).get("type")
        action_data = plan.get("action", {}).get("data", {})

        if action_type == "ask_for_information":
            plan["context_to_remember"] = {"last_user_prompt_for_buttons": original_query}
            return {"type": "buttons", "data": action_data}

        if action_type == "direct_answer":
            return {"type": "text", "data": {"text": action_data.get("response_text")}}

        if action_type == "content_creation_redirect":
            return self._generate_content_creation_redirect(action_data)

        if action_type == "needs_deep_analysis":
            selected_keys = action_data.get("selected_context_keys", [])
            nem_context = {k: v for k, v in self.gemini_adapter.config.knowledge_base_nem.items() if k in selected_keys}
            sep_context = {k: v for k, v in self.gemini_adapter.config.sep_knowledge_base.items() if k in selected_keys}
            full_selected_context = {**nem_context, **sep_context}

            final_plan = self.gemini_adapter.get_complex_analysis(
                original_query, user_profile, full_selected_context
            )
            if not final_plan:
                return self._generate_error_response("Tuve problemas al analizar tu solicitud en detalle")
            
            final_response = await self._execute_plan(final_plan, original_query, user_profile)
            final_response["final_plan"] = final_plan
            return final_response

        if action_type == "vector_search":
            query = action_data.get("query")
            if not query:
                return self._generate_error_response("Hubo un problema al generar la consulta")

            search_results = self.vector_adapter.search_similar(query=query, num_neighbors=5)
            if not search_results:
                return self._generate_content_creation_redirect({
                    "redirect_type": "both",
                    "redirect_message": "No encontré contenido específico para tu consulta. Te sugiero crear tu propio contenido educativo personalizado."
                })
            
            # Verificar confianza de los resultados (distance < 0.35 equivale a > 65% de confianza)
            high_confidence_results = []
            for result in search_results:
                distance = result.get("distance", 1.0)
                if distance < 0.35:  # Más del 65% de confianza
                    high_confidence_results.append(result)
            
            # Si no hay resultados con alta confianza, redirigir a creación de contenido
            if not high_confidence_results:
                return self._generate_content_creation_redirect({
                    "redirect_type": "both",
                    "redirect_message": "Los recursos disponibles no tienen la precisión suficiente para tu consulta. Te recomiendo crear contenido personalizado que se ajuste exactamente a tus necesidades."
                })
            
            intro_text = action_data.get("intro_text", "Aquí tienes algunos recursos:")
            
            # Crear content_cards con información más detallada
            content_cards = []
            for result in high_confidence_results:
                content_card = {
                    "id": result.get("id", ""),
                    "content_type": result.get("content_type", "med"),
                    "title": result.get("title", "Sin título"),
                    "description": result.get("description", "Sin descripción"),
                    "url": result.get("url", ""),
                    "tags": result.get("tags", [])
                }
                content_cards.append(content_card)
            
            return {
                "type": "content_cards",
                "data": {
                    "intro_text": intro_text, 
                    "content_cards": content_cards,
                    "total_results": len(content_cards)
                }
            }
        
        return self._generate_error_response("No estoy seguro de cómo proceder")

    def _update_conversation_history(
        self, 
        current_context: Dict[str, Any], 
        action_plan: Dict[str, Any], 
        user_message: str
    ) -> Dict[str, Any]:
        """Update conversation history with new interaction."""
        # Asegurar que current_context sea un diccionario
        if not isinstance(current_context, dict):
            current_context = {}
            
        history = current_context.get("history", [])
        
        # Añadir mensaje del usuario
        history.append({
            "role": "user", 
            "content": user_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Añadir respuesta del asistente
        history.append({
            "role": "assistant", 
            "intent": action_plan.get("intent"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Limitar historia para el contexto (mantener solo los últimos N mensajes)
        max_history = self.gemini_adapter.config.max_history_context * 2  # *2 porque cada interacción tiene 2 mensajes
        if len(history) > max_history:
            history = history[-max_history:]
            
        # Contar mensajes totales en la conversación
        message_count = current_context.get("message_count", 0) + 1
        
        # Construir nuevo contexto con información enriquecida
        new_context = {
            "last_intent": action_plan.get("intent"),
            "last_user_message": user_message,
            "history": history,
            "message_count": message_count,
            "welcome_shown": current_context.get("welcome_shown", True),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Añadir información contextual específica según el tipo de interacción
        if action_plan.get("selected_option"):
            new_context["last_selected_option"] = action_plan["selected_option"]
            
        if action_plan.get("updated_fields"):
            new_context["profile_updates"] = action_plan["updated_fields"]
            
        # Mantener información contextual previa
        if current_context.get("conversation_topics"):
            new_context["conversation_topics"] = current_context["conversation_topics"]
            
        if current_context.get("user_preferences"):
            new_context["user_preferences"] = current_context["user_preferences"]
            
        # Añadir contexto adicional si existe
        if action_plan.get("context_to_remember"):
            new_context.update(action_plan["context_to_remember"])
            
        return new_context

    def _log_user_input(self, conv_id: str, user_id: str, msg: Optional[str], data: Optional[List[UserDataInput]]):
        """Log user input to BigQuery."""
        if msg is not None:
            content = msg
        elif data is not None:
            # Crear contenido más legible para datos estructurados
            if len(data) == 1 and data[0].field == "menu_option":
                option_value = data[0].value
                option_labels = {
                    "perfil": "⚙️ Configurar Perfil",
                    "otro": "✍️ Escribir Consulta Personalizada",
                    "planeaciones": "📚 Ayuda con Planeaciones",
                    "meds": "📖 Materiales Educativos (MEDs)",
                    "evaluacion": "🎯 Evaluación y Diagnóstico",
                    "metodologias": "🔧 Metodologías de Enseñanza",
                    "programas": "📋 Programas Analíticos",
                    "general": "❓ Preguntas Generales"
                }
                content = f"👆 Seleccionó: {option_labels.get(option_value, option_value)}"
            else:
                # Para datos de perfil u otros datos estructurados
                content = f"📝 Datos: {', '.join([f'{item.field}={item.value}' for item in data])}"
        else:
            content = "Mensaje vacío"
            
        self.bq_adapter.log_message(conv_id, user_id, str(uuid.uuid4()), "user", content, False)

    def _log_assistant_response(self, conv_id: str, user_id: str, response: Dict[str, Any]):
        """Log assistant response to BigQuery."""
        response_type = response.get('response_type', response.get('type', 'unknown'))
        
        # Crear contenido más legible para el frontend
        if response_type == 'welcome':
            data = response.get('data', {})
            content = f"🤖 {data.get('message', 'Mensaje de bienvenida')}"
        elif response_type == 'buttons':
            data = response.get('data', {})
            content = f"📋 {data.get('message', 'Opciones de configuración')}"
        elif response_type == 'text_input':
            data = response.get('data', {})
            content = f"✍️ {data.get('message', 'Solicitud de consulta personalizada')}"
        elif response_type == 'text':
            data = response.get('data', {})
            content = data.get('text', 'Respuesta de texto')
        elif response_type == 'content_cards':
            data = response.get('data', {})
            content = f"📚 {data.get('intro_text', 'Resultados de búsqueda')}"
        else:
            content = f"RESPONSE_TYPE: {response_type} | DATA: {str(response.get('data', {}))}"
        
        self.bq_adapter.log_message(conv_id, user_id, str(uuid.uuid4()), "assistant", content, True)

    def _generate_error_response(self, text: str) -> Dict[str, Any]:
        """Generate error response."""
        logger.warning(f"Generating error response: {text}")
        return {"type": "text", "data": {"text": text}}

    def _generate_content_creation_redirect(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content creation redirect response."""
        redirect_type = action_data.get("redirect_type", "both")
        redirect_message = action_data.get("redirect_message", "Te sugiero crear contenido educativo personalizado.")
        
        content_cards = []
        
        if redirect_type in ["planeacion", "both"]:
            content_cards.append({
                "id": "planeacion_redirection",
                "title": "Crear Planeación Gratuita",
                "description": "Accede a la herramienta para crear planeaciones didácticas personalizadas",
                "content": "Crea planeaciones completas con objetivos, actividades, evaluación y recursos adaptados a tu contexto educativo.",
                "type": "redirect",
                "url": "https://redmagisterial.com/red-magia/crear-planeacion-gratutia",
                "tags": ["planeación", "didáctica", "gratuita"]
            })
        
        if redirect_type in ["med", "both"]:
            content_cards.append({
                "id": "med_redirection",
                "title": "Crear Material Educativo Digital (MED)",
                "description": "Accede a la herramienta para crear materiales educativos digitales",
                "content": "Desarrolla recursos digitales interactivos, presentaciones, videos y otros materiales educativos innovadores.",
                "type": "redirect",
                "url": "https://redmagisterial.com/login?previous=/red-magia/meds/crear-med",
                "tags": ["MED", "digital", "interactivo"]
            })
        
        return {
            "type": "content_cards",
            "data": {
                "intro_text": redirect_message,
                "content_cards": content_cards,
                "total_results": len(content_cards)
            }
        } 