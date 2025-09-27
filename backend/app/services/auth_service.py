import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status, Depends
from ..config import settings
from ..database import get_database
from ..models.user import UserInDB, TokenData

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer()

class AuthService:
    """Service for authentication and authorization"""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.db = get_database()
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            role: str = payload.get("role")
            
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            token_data = TokenData(username=username, user_id=user_id, role=role)
            return token_data
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user with email and password"""
        try:
            user = await self.db.users.find_one({"email": email})
            if not user:
                return None
            
            user_obj = UserInDB(**user)
            if not self.verify_password(password, user_obj.hashed_password):
                return None
            
            # Update last login
            await self.db.users.update_one(
                {"_id": user_obj.id},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            return user_obj
            
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
        """Get the current authenticated user"""
        token = credentials.credentials
        token_data = self.verify_token(token)
        
        user = await self.db.users.find_one({"_id": token_data.user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_obj = UserInDB(**user)
        if not user_obj.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user_obj
    
    async def get_current_active_user(self, current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
        """Get the current active user"""
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    
    def require_role(self, required_role: str):
        """Decorator to require specific role"""
        async def role_checker(current_user: UserInDB = Depends(self.get_current_active_user)) -> UserInDB:
            if current_user.role != required_role and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {required_role}"
                )
            return current_user
        return role_checker
    
    def require_any_role(self, allowed_roles: list):
        """Decorator to require any of the specified roles"""
        async def role_checker(current_user: UserInDB = Depends(self.get_current_active_user)) -> UserInDB:
            if current_user.role not in allowed_roles and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            return current_user
        return role_checker
    
    async def create_user(self, user_data: Dict[str, Any]) -> UserInDB:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await self.db.users.find_one({
                "$or": [
                    {"email": user_data["email"]},
                    {"username": user_data["username"]}
                ]
            })
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email or username already exists"
                )
            
            # Hash password
            user_data["hashed_password"] = self.hash_password(user_data.pop("password"))
            user_data["created_at"] = datetime.utcnow()
            user_data["updated_at"] = datetime.utcnow()
            
            # Insert user
            result = await self.db.users.insert_one(user_data)
            
            # Return created user
            user = await self.db.users.find_one({"_id": result.inserted_id})
            return UserInDB(**user)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user"
            )
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> UserInDB:
        """Update user information"""
        try:
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            if not update_data:
                # No updates to make
                user = await self.db.users.find_one({"_id": user_id})
                return UserInDB(**user)
            
            # Handle password update
            if "password" in update_data:
                update_data["hashed_password"] = self.hash_password(update_data.pop("password"))
            
            update_data["updated_at"] = datetime.utcnow()
            
            # Update user
            result = await self.db.users.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Return updated user
            user = await self.db.users.find_one({"_id": user_id})
            return UserInDB(**user)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating user"
            )
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user (soft delete - mark as inactive)"""
        try:
            result = await self.db.users.update_one(
                {"_id": user_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.matched_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # Get user
            user = await self.db.users.find_one({"_id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user_obj = UserInDB(**user)
            
            # Verify current password
            if not self.verify_password(current_password, user_obj.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # Update password
            new_hashed_password = self.hash_password(new_password)
            await self.db.users.update_one(
                {"_id": user_id},
                {"$set": {
                    "hashed_password": new_hashed_password,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {e}")
            return False
    
    async def reset_password(self, email: str) -> str:
        """Generate password reset token"""
        try:
            user = await self.db.users.find_one({"email": email})
            if not user:
                # Don't reveal if email exists or not
                return "If the email exists, a reset link will be sent"
            
            # Generate reset token (expires in 1 hour)
            reset_data = {
                "sub": user["email"],
                "user_id": str(user["_id"]),
                "type": "password_reset"
            }
            
            reset_token = self.create_access_token(
                reset_data, 
                expires_delta=timedelta(hours=1)
            )
            
            # Store reset token (in production, you might store this in Redis)
            await self.db.password_resets.insert_one({
                "user_id": user["_id"],
                "token": reset_token,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=1),
                "used": False
            })
            
            return reset_token
            
        except Exception as e:
            logger.error(f"Error generating password reset for {email}: {e}")
            return "Error generating reset token"
    
    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """Confirm password reset with token"""
        try:
            # Verify token
            token_data = self.verify_token(token)
            
            # Check if it's a password reset token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reset token"
                )
            
            # Check if token exists and is not used
            reset_record = await self.db.password_resets.find_one({
                "token": token,
                "used": False,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not reset_record:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token"
                )
            
            # Update password
            new_hashed_password = self.hash_password(new_password)
            await self.db.users.update_one(
                {"_id": reset_record["user_id"]},
                {"$set": {
                    "hashed_password": new_hashed_password,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            # Mark token as used
            await self.db.password_resets.update_one(
                {"_id": reset_record["_id"]},
                {"$set": {"used": True}}
            )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error confirming password reset: {e}")
            return False
    
    async def validate_user_permissions(self, user: UserInDB, resource_type: str, 
                                      resource_id: str = None, action: str = "read") -> bool:
        """Validate user permissions for a resource"""
        try:
            # Admin can do everything
            if user.role == "admin":
                return True
            
            # Role-based permissions
            permissions = {
                "volunteer": {
                    "volunteers": ["read", "update_own"],
                    "events": ["read"],
                    "matches": ["read_own", "update_own"]
                },
                "organization": {
                    "volunteers": ["read"],
                    "events": ["read", "create", "update_own", "delete_own"],
                    "matches": ["read_own", "create", "update_own"]
                }
            }
            
            user_permissions = permissions.get(user.role, {})
            resource_permissions = user_permissions.get(resource_type, [])
            
            # Check if action is allowed
            if action in resource_permissions:
                return True
            
            # Check ownership-based permissions
            if f"{action}_own" in resource_permissions and resource_id:
                return await self._check_resource_ownership(user, resource_type, resource_id)
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating permissions: {e}")
            return False
    
    async def _check_resource_ownership(self, user: UserInDB, resource_type: str, resource_id: str) -> bool:
        """Check if user owns the resource"""
        try:
            if resource_type == "volunteers":
                resource = await self.db.volunteers.find_one({"_id": resource_id})
                return resource and str(resource.get("user_id")) == str(user.id)
            
            elif resource_type == "events":
                resource = await self.db.events.find_one({"_id": resource_id})
                return resource and str(resource.get("organization_id")) == str(user.id)
            
            elif resource_type == "matches":
                resource = await self.db.matches.find_one({"_id": resource_id})
                if not resource:
                    return False
                
                # User can access match if they are the volunteer or event owner
                if str(resource.get("volunteer_id")) == str(user.id):
                    return True
                
                # Check if user owns the event
                event = await self.db.events.find_one({"_id": resource.get("event_id")})
                return event and str(event.get("organization_id")) == str(user.id)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking resource ownership: {e}")
            return False

# Create a global instance
auth_service = AuthService() 