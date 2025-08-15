"""
Authentication middleware for MentorIA Chatbot API.

Provides token-based authentication for API endpoints.
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.config import config

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Middleware for token-based authentication."""
    
    @staticmethod
    async def verify_token(request: Request) -> Optional[str]:
        """
        Verify the authentication token.
        
        Args:
            request: FastAPI request object
            
        Returns:
            User ID if token is valid, None if no auth required
            
        Raises:
            HTTPException: If token is invalid or missing
        """
        # Skip authentication if not required
        if not config.require_auth:
            return None
            
        # Skip authentication for health check and root endpoints
        if request.url.path in ["/health", "/"]:
            return None
            
        # Get token from header
        credentials: HTTPAuthorizationCredentials = await security(request)
        
        if not credentials:
            logger.warning("No authorization header provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        
        # Verify token
        if not config.api_token or token != config.api_token:
            logger.warning(f"Invalid token provided: {token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Token verified successfully")
        return "authenticated_user"


async def auth_dependency(request: Request) -> Optional[str]:
    """
    Dependency for FastAPI to verify authentication.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User ID if authenticated, None if no auth required
    """
    return await AuthMiddleware.verify_token(request) 