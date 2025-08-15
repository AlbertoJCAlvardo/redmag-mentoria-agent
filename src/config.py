"""
Configuration module for MentorIA Chatbot API.

Manages all application configuration and environment variables.
"""

import os
import json
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for all project settings."""

    def __init__(self):
        """Initialize configuration with environment variables."""
        # --- Project Directory Setup ---
        # Define the base directory of the application (the 'src' folder)
        # This makes file paths independent of the current working directory.
        # Path(__file__) is the path to this config.py file.
        # .resolve() makes it an absolute path.
        # .parent gets the directory containing it ('src').
        BASE_DIR = Path(__file__).resolve().parent

        # Google Cloud Configuration
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-east1")
        self.service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        self.gcs_bucket_name = os.getenv("GCS_BUCKET_NAME")

        # BigQuery Configuration
        self.bigquery_users_table = os.getenv("BIGQUERY_USERS_TABLE", "redmag-chatbot.redmag_chatbot_dataset_prod.users")
        self.bigquery_messages_table = os.getenv("BIGQUERY_MESSAGES_TABLE", "redmag-chatbot.redmag_chatbot_dataset_prod.messages")
        self.bigquery_context_table = os.getenv("BIGQUERY_CONTEXT_TABLE", "redmag-chatbot.redmag_chatbot_dataset_prod.conversation_context")

        # Vertex AI Vector Search Configuration
        self.index_id = os.getenv("VECTOR_INDEX_ID")
        self.endpoint_id = os.getenv("VECTOR_ENDPOINT_ID")
        self.deployed_index_id = os.getenv("DEPLOYED_INDEX_ID")

        # Embedding Model Configuration
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

        # Firecrawl Scraper Configuration
        self.firecrawl_api_keys = [os.getenv("FIRECRAWL_API_KEYS")]

        # Gemini AI Configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        # API Authentication (for external CMS APIs)
        self.api_username = os.getenv("API_USERNAME")
        self.api_password = os.getenv("API_PASSWORD")

        self.batch_size = 100

        # Chat Configuration
        self.max_messages_per_conversation = int(os.getenv("MAX_MESSAGES_PER_CONVERSATION", "20"))
        self.max_history_context = int(os.getenv("MAX_HISTORY_CONTEXT", "8"))

        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # --- Static Knowledge Base Loading ---
        # Construct absolute paths to the knowledge base files inside 'src/static'
        # Try multiple possible paths for different deployment scenarios
        possible_static_paths = [
            BASE_DIR / "static",  # Local development
            Path("/app/src/static"),  # Docker container
            Path("/app/static"),  # Alternative Docker path
        ]
        
        knowledge_base_nem_path = None
        sep_knowledge_base_path = None
        
        # Find the correct static directory
        for static_path in possible_static_paths:
            nem_file = static_path / "knowledge_base_nem.json"
            sep_file = static_path / "sep_knowledge_base.json"
            if nem_file.exists() and sep_file.exists():
                knowledge_base_nem_path = nem_file
                sep_knowledge_base_path = sep_file
                break
        
        if not knowledge_base_nem_path or not sep_knowledge_base_path:
            # If not found, try to load with fallback to empty data
            print(f"Warning: Knowledge base files not found. Tried paths: {[str(p) for p in possible_static_paths]}")
            self.knowledge_base_nem = {}
            self.sep_knowledge_base = {}
        else:
            try:
                with open(knowledge_base_nem_path, "r", encoding="utf-8") as f:
                    self.knowledge_base_nem = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Error decoding JSON from {knowledge_base_nem_path}")
                self.knowledge_base_nem = {}

            try:
                with open(sep_knowledge_base_path, "r", encoding="utf-8") as f:
                    self.sep_knowledge_base = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Error decoding JSON from {sep_knowledge_base_path}")
                self.sep_knowledge_base = {}


    def validate(self) -> bool:
        """Validate that required configuration values are present."""
        required_fields = ["project_id", "index_id", "bigquery_users_table"]
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        if missing_fields:
            raise ValueError(f"Missing required configuration: {missing_fields}")
        return True

    def get_index_path(self) -> str:
        """Get the full path for the vector index."""
        return f"projects/{self.project_id}/locations/us/indexes/{self.index_id}"

    def get_endpoint_path(self) -> Optional[str]:
        """Get the full path for the vector endpoint if available."""
        if self.endpoint_id:
            return f"projects/{self.project_id}/locations/{self.location}/indexEndpoints/{self.endpoint_id}"
        return None

    def setup_authentication(self) -> None:
        """Setup Google Cloud authentication using service account."""
        if not self.service_account_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not configured")

        service_account_file = Path(self.service_account_path)
        if not service_account_file.exists():
            raise FileNotFoundError(f"Service account file not found: {self.service_account_path}")

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(service_account_file.absolute())


# Global configuration instance
config = Config()
