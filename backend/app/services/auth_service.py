"""
Authentication service for user management
"""

from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate
from email_validator import validate_email, EmailNotValidError
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.logger import app_logger
from datetime import timedelta
from app.config import settings


class AuthService:
    """Service for authentication operations"""
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """
        Create a new user
        
        Args:
            db: Database session
            user_data: User creation data
        
        Returns:
            Created user object
        """
        try:
            # Normalize and validate email using email_validator in a robust way
            try:
                # Validate syntax only; avoid network/DNS deliverability checks which
                # can fail in local/dev environments or for reserved domains like example.com
                validated = validate_email(user_data.email, check_deliverability=False)
            except EmailNotValidError as ev_err:
                raise ValueError("Invalid email address") from ev_err

            # email_validator may return different shapes across versions.
            # Prefer common attributes in order of likelihood.
            normalized_email = None
            if hasattr(validated, "email"):
                normalized_email = validated.email
            elif hasattr(validated, "normalized"):
                normalized_email = validated.normalized
            elif isinstance(validated, tuple) and len(validated) > 0:
                normalized_email = validated[0]
            else:
                normalized_email = str(validated)

            # Ensure consistent casing
            normalized_email = normalized_email.strip()

            # Check if user already exists
            existing_user = db.query(User).filter(User.email == normalized_email).first()
            if existing_user:
                raise ValueError("Email already registered")

            # Create new user
            hashed_pwd = hash_password(user_data.password)

            new_user = User(
                name=user_data.name,
                email=normalized_email,
                organization=user_data.organization,
                hashed_password=hashed_pwd
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            app_logger.info(f"Created new user: {new_user.email}")
            return new_user

        except Exception as e:
            db.rollback()
            app_logger.error(f"Error creating user: {str(e)}")
            raise
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            db: Database session
            email: User email
            password: Plain password
        
        Returns:
            User object if authenticated, None otherwise
        """
        try:
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                return None
            
            if not verify_password(password, user.hashed_password):
                return None
            
            if not user.is_active:
                return None
            
            app_logger.info(f"User authenticated: {email}")
            return user
        
        except Exception as e:
            app_logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    def generate_token(self, user: User) -> str:
        """
        Generate JWT token for user
        
        Args:
            user: User object
        
        Returns:
            JWT token string
        """
        token_data = {
            "user_id": user.id,
            "email": user.email
        }
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(token_data, expires_delta=access_token_expires)
        
        return access_token


# Global instance
auth_service = AuthService()
