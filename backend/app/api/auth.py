from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from ..models.user import UserCreate, UserLogin, User, Token, UserUpdate
from ..services.auth_service import auth_service
from ..utils.validators import validate_email, validate_password
from ..utils.security import sanitize_input
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=Dict[str, Any])
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Validate input
        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        if not validate_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with letters and numbers"
            )
        
        # Sanitize input
        user_dict = user_data.dict()
        for key, value in user_dict.items():
            if isinstance(value, str):
                user_dict[key] = sanitize_input(value)
        
        # Create user
        user = await auth_service.create_user(user_dict)
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={
                "sub": user.username,
                "user_id": str(user.id),
                "role": user.role
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": auth_service.access_token_expire_minutes * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return access token"""
    try:
        # Sanitize input
        email = sanitize_input(user_credentials.email)
        password = user_credentials.password
        
        # Authenticate user
        user = await auth_service.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = auth_service.create_access_token(
            data={
                "sub": user.username,
                "user_id": str(user.id),
                "role": user.role
            }
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=User)
async def get_current_user_info(current_user = Depends(auth_service.get_current_active_user)):
    """Get current user information"""
    return User(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        phone=current_user.phone,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login
    )

@router.put("/me", response_model=User)
async def update_current_user(
    update_data: UserUpdate,
    current_user = Depends(auth_service.get_current_active_user)
):
    """Update current user information"""
    try:
        # Sanitize input
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if isinstance(value, str):
                update_dict[key] = sanitize_input(value)
        
        # Validate email if provided
        if "email" in update_dict and not validate_email(update_dict["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Update user
        updated_user = await auth_service.update_user(str(current_user.id), update_dict)
        
        return User(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            full_name=updated_user.full_name,
            phone=updated_user.phone,
            role=updated_user.role,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            last_login=updated_user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Update failed"
        )

@router.post("/change-password")
async def change_password(
    password_data: Dict[str, str],
    current_user = Depends(auth_service.get_current_active_user)
):
    """Change user password"""
    try:
        current_password = password_data.get("current_password")
        new_password = password_data.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password and new password are required"
            )
        
        if not validate_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters with letters and numbers"
            )
        
        # Change password
        success = await auth_service.change_password(
            str(current_user.id), 
            current_password, 
            new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post("/forgot-password")
async def forgot_password(email_data: Dict[str, str]):
    """Request password reset"""
    try:
        email = sanitize_input(email_data.get("email", ""))
        
        if not validate_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Generate reset token
        reset_token = await auth_service.reset_password(email)
        
        # In production, you would send this token via email
        # For demo purposes, we return it (DON'T DO THIS IN PRODUCTION)
        return {
            "message": "Password reset instructions sent to email",
            "reset_token": reset_token  # Remove this in production
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.post("/reset-password")
async def reset_password(reset_data: Dict[str, str]):
    """Reset password with token"""
    try:
        token = reset_data.get("token")
        new_password = reset_data.get("new_password")
        
        if not token or not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token and new password are required"
            )
        
        if not validate_password(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters with letters and numbers"
            )
        
        # Reset password
        success = await auth_service.confirm_password_reset(token, new_password)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.post("/logout")
async def logout(current_user = Depends(auth_service.get_current_active_user)):
    """Logout user (in a real app, you might blacklist the token)"""
    # In a production app, you might want to:
    # 1. Add the token to a blacklist
    # 2. Store logout time
    # 3. Clean up any session data
    
    return {"message": "Successfully logged out"}

@router.get("/validate-token")
async def validate_token(current_user = Depends(auth_service.get_current_active_user)):
    """Validate if the current token is still valid"""
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "role": current_user.role,
        "expires_in": auth_service.access_token_expire_minutes * 60
    } 