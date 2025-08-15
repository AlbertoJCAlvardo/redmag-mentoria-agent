"""
BigQuery adapter for MentorIA Chatbot API.

Provides data access layer for BigQuery operations.
"""

import logging
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

from src.config import config

logger = logging.getLogger(__name__)


class BigQueryAdapter:
    """Adapter for BigQuery database operations."""

    def __init__(self):
        """Initialize BigQuery client."""
        try:
            self.client = bigquery.Client(project=config.project_id)
            self.users_table_id = config.bigquery_users_table
            self.messages_table_id = config.bigquery_messages_table
            self.context_table_id = config.bigquery_context_table
            logger.info("BigQueryAdapter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}", exc_info=True)
            # No raise exception to allow application to continue without BigQuery
            self.client = None

    def _is_available(self) -> bool:
        """Check if BigQuery is available."""
        return self.client is not None

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile data from BigQuery.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User profile data dictionary or None if not found
        """
        if not self._is_available():
            logger.warning("BigQuery not available, returning empty profile")
            return {}
            
        query = f"""
            SELECT profile_data
            FROM `{self.users_table_id}`
            WHERE user_id = @user_id
            LIMIT 1
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
        )
        try:
            query_job = self.client.query(query, job_config=job_config)
            rows = list(query_job)
            if rows:
                profile_data = rows[0].profile_data
                
                # BigQuery puede devolver JSON como string, necesitamos deserializarlo
                if isinstance(profile_data, str):
                    try:
                        profile_data = json.loads(profile_data)
                        logger.info(f"Deserialized profile data for user_id: {user_id}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to deserialize profile data for user_id {user_id}: {e}")
                        return {}
                
                # Verificar que sea un diccionario
                if isinstance(profile_data, dict):
                    return profile_data
                else:
                    logger.warning(f"Profile data is not a dict for user_id {user_id}: {type(profile_data)}")
                    return {}
                    
            return {}
        except Exception as e:
            logger.error(f"Failed to get user profile for user_id {user_id}: {e}", exc_info=True)
            return {}

    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Update or create user profile in BigQuery.
        
        Args:
            user_id: Unique user identifier
            profile_data: User profile data dictionary
            
        Returns:
            True if operation was successful, False otherwise
        """
        if not self._is_available():
            logger.warning("BigQuery not available, skipping profile update")
            return True
            
        query = f"""
            MERGE `{self.users_table_id}` T
            USING (SELECT @user_id AS user_id) S
            ON T.user_id = S.user_id
            WHEN MATCHED THEN
                UPDATE SET profile_data = @profile_data, last_created = @now
            WHEN NOT MATCHED THEN
                INSERT (user_id, created_at, last_created, profile_data)
                VALUES (@user_id, @now, @now, @profile_data)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("profile_data", "JSON", json.dumps(profile_data)),
                bigquery.ScalarQueryParameter("now", "DATETIME", datetime.now(timezone.utc)),
            ]
        )
        try:
            self.client.query(query, job_config=job_config).result()
            logger.info(f"Successfully updated profile for user_id: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update user profile for user_id {user_id}: {e}", exc_info=True)
            return False

    def get_conversation_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation context from BigQuery.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Conversation context data dictionary or None if not found
        """
        if not self._is_available():
            logger.warning("BigQuery not available, returning empty context")
            return {}
            
        query = f"""
            SELECT context_data
            FROM `{self.context_table_id}`
            WHERE conversation_id = @conversation_id AND is_active = TRUE
            LIMIT 1
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id)]
        )
        try:
            rows = list(self.client.query(query, job_config=job_config))
            if rows:
                context_data = rows[0].context_data
                
                # BigQuery puede devolver JSON como string, necesitamos deserializarlo
                if isinstance(context_data, str):
                    try:
                        context_data = json.loads(context_data)
                        logger.info(f"Deserialized context data for conversation_id: {conversation_id}")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to deserialize context data for conversation_id {conversation_id}: {e}")
                        return {}
                
                # Verificar que sea un diccionario
                if isinstance(context_data, dict):
                    return context_data
                else:
                    logger.warning(f"Context data is not a dict for conversation_id {conversation_id}: {type(context_data)}")
                    return {}
                    
            return {}
        except Exception as e:
            logger.error(f"Failed to get context for conversation_id {conversation_id}: {e}", exc_info=True)
            return {}

    def update_conversation_context(self, conversation_id: str, user_id: str, context_data: Dict[str, Any]) -> bool:
        """
        Update or create conversation context in BigQuery.
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: User identifier
            context_data: Conversation context data dictionary
            
        Returns:
            True if operation was successful, False otherwise
        """
        if not self._is_available():
            logger.warning("BigQuery not available, skipping context update")
            return True
            
        query = f"""
            MERGE `{self.context_table_id}` T
            USING (SELECT @conversation_id AS conversation_id) S
            ON T.conversation_id = S.conversation_id
            WHEN MATCHED THEN
                UPDATE SET context_data = @context_data, last_updated = @now
            WHEN NOT MATCHED THEN
                INSERT (conversation_id, user_id, created_at, last_updated, context_data, is_active)
                VALUES (@conversation_id, @user_id, @now, @now, @context_data, TRUE)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                bigquery.ScalarQueryParameter("context_data", "JSON", json.dumps(context_data)),
                bigquery.ScalarQueryParameter("now", "TIMESTAMP", datetime.now(timezone.utc)),
            ]
        )
        try:
            self.client.query(query, job_config=job_config).result()
            logger.info(f"Successfully updated context for conversation_id: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update context for conversation_id {conversation_id}: {e}", exc_info=True)
            return False

    def log_message(self, conversation_id: str, user_id: str, message_id: str, role: str, content: str, agent_response: bool) -> bool:
        """
        Log message to BigQuery.
        
        Args:
            conversation_id: Conversation identifier
            user_id: User identifier
            message_id: Unique message identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            agent_response: True if message is from agent
            
        Returns:
            True if logging was successful, False otherwise
        """
        if not self._is_available():
            logger.warning("BigQuery not available, skipping message logging")
            return True
            
        row_to_insert = {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": content,
            "agent_response": str(agent_response),
            "flow": "chat"
        }
        try:
            errors = self.client.insert_rows_json(self.messages_table_id, [row_to_insert])
            if not errors:
                logger.debug(f"Successfully logged message {message_id}")
                return True
            else:
                logger.error(f"Errors occurred while inserting message {message_id}: {errors}")
                return False
        except Exception as e:
            logger.error(f"Failed to log message {message_id}: {e}", exc_info=True)
            return False

    def get_conversation_messages(self, conversation_id: str, page: int = 1, size: int = 8) -> Dict[str, Any]:
        """
        Get paginated messages for a conversation.
        
        Args:
            conversation_id: Conversation identifier
            page: Page number (1-based)
            size: Number of messages per page
            
        Returns:
            Dictionary with messages, pagination info, and metadata
        """
        if not self._is_available():
            logger.warning("BigQuery not available, returning empty message list")
            return {
                "messages": [],
                "total": 0,
                "page": page,
                "size": size,
                "has_next": False,
                "has_previous": False
            }
        
        try:
            # Calculate offset
            offset = (page - 1) * size
            
            # Get total count
            count_query = f"""
                SELECT COUNT(*) as total
                FROM `{self.messages_table_id}`
                WHERE conversation_id = @conversation_id
            """
            
            count_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                ]
            )
            
            count_result = self.client.query(count_query, count_job_config).result()
            total_count = next(count_result).total
            
            # Get paginated messages
            messages_query = f"""
                SELECT 
                    message_id as id,
                    user_id,
                    conversation_id,
                    content as message,
                    CASE 
                        WHEN agent_response = 'true' THEN 'bot'
                        ELSE 'user'
                    END as message_type,
                    timestamp,
                    flow as metadata
                FROM `{self.messages_table_id}`
                WHERE conversation_id = @conversation_id
                ORDER BY timestamp DESC
                LIMIT @size
                OFFSET @offset
            """
            
            messages_job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    bigquery.ScalarQueryParameter("size", "INT64", size),
                    bigquery.ScalarQueryParameter("offset", "INT64", offset),
                ]
            )
            
            messages_result = self.client.query(messages_query, messages_job_config).result()
            
            messages = []
            for row in messages_result:
                message = {
                    "id": row.id,
                    "user_id": row.user_id,
                    "conversation_id": row.conversation_id,
                    "message": row.message,
                    "message_type": row.message_type,
                    "timestamp": row.timestamp,
                    "metadata": {"flow": row.metadata} if row.metadata else None
                }
                messages.append(message)
            
            # Calculate pagination info
            has_next = (offset + size) < total_count
            has_previous = page > 1
            
            return {
                "messages": messages,
                "total": total_count,
                "page": page,
                "size": size,
                "has_next": has_next,
                "has_previous": has_previous
            }
            
        except Exception as e:
            logger.error(f"Failed to get messages for conversation_id {conversation_id}: {e}", exc_info=True)
            return {
                "messages": [],
                "total": 0,
                "page": page,
                "size": size,
                "has_next": False,
                "has_previous": False
            }

    def get_latest_conversation_id(self, user_id: str) -> Optional[str]:
        """
        Get the latest conversation ID for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Latest conversation ID or None if not found
        """
        if not self._is_available():
            logger.warning("BigQuery not available, returning None for latest conversation")
            return None
        
        try:
            query = f"""
                SELECT conversation_id
                FROM `{self.messages_table_id}`
                WHERE user_id = @user_id
                ORDER BY timestamp DESC
                LIMIT 1
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
                ]
            )
            
            result = self.client.query(query, job_config).result()
            
            for row in result:
                return row.conversation_id
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest conversation for user_id {user_id}: {e}", exc_info=True)
            return None

    def get_conversation_info(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation information.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Conversation information dictionary or None if not found
        """
        if not self._is_available():
            logger.warning("BigQuery not available, returning None for conversation info")
            return None
        
        try:
            query = f"""
                SELECT 
                    conversation_id,
                    user_id,
                    created_at,
                    last_updated as last_message_at,
                    is_active
                FROM `{self.context_table_id}`
                WHERE conversation_id = @conversation_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                ]
            )
            
            result = self.client.query(query, job_config).result()
            
            for row in result:
                # Get message count
                count_query = f"""
                    SELECT COUNT(*) as message_count
                    FROM `{self.messages_table_id}`
                    WHERE conversation_id = @conversation_id
                """
                
                count_job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("conversation_id", "STRING", conversation_id),
                    ]
                )
                
                count_result = self.client.query(count_query, count_job_config).result()
                message_count = next(count_result).message_count
                
                return {
                    "conversation_id": row.conversation_id,
                    "user_id": row.user_id,
                    "created_at": row.created_at,
                    "last_message_at": row.last_message_at,
                    "message_count": message_count,
                    "is_active": row.is_active
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get conversation info for conversation_id {conversation_id}: {e}", exc_info=True)
            return None 