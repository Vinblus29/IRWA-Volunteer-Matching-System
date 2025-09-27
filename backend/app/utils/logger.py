import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from ..config import settings

def setup_logging():
    """Setup application logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Define log format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # File handler for errors
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    root_logger.addHandler(error_handler)
    
    # Agent-specific logger
    agent_logger = logging.getLogger("agent")
    agent_handler = logging.handlers.RotatingFileHandler(
        log_dir / "agents.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    agent_handler.setLevel(logging.DEBUG)
    agent_handler.setFormatter(log_format)
    agent_logger.addHandler(agent_handler)
    
    # Database logger
    db_logger = logging.getLogger("database")
    db_handler = logging.handlers.RotatingFileHandler(
        log_dir / "database.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    db_handler.setLevel(logging.DEBUG)
    db_handler.setFormatter(log_format)
    db_logger.addHandler(db_handler)
    
    # Security logger
    security_logger = logging.getLogger("security")
    security_handler = logging.handlers.RotatingFileHandler(
        log_dir / "security.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10  # Keep more security logs
    )
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(log_format)
    security_logger.addHandler(security_handler)
    
    # Disable some noisy loggers in production
    if settings.environment == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logging.info("Logging system initialized")

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
    
    def log_failed_login(self, email: str, ip_address: str = None):
        """Log failed login attempt"""
        self.logger.warning(
            f"Failed login attempt for email: {email} from IP: {ip_address or 'unknown'}"
        )
    
    def log_successful_login(self, email: str, ip_address: str = None):
        """Log successful login"""
        self.logger.info(
            f"Successful login for email: {email} from IP: {ip_address or 'unknown'}"
        )
    
    def log_password_change(self, user_id: str, ip_address: str = None):
        """Log password change"""
        self.logger.info(
            f"Password changed for user: {user_id} from IP: {ip_address or 'unknown'}"
        )
    
    def log_suspicious_activity(self, user_id: str, activity: str, ip_address: str = None):
        """Log suspicious activity"""
        self.logger.warning(
            f"Suspicious activity for user {user_id}: {activity} from IP: {ip_address or 'unknown'}"
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str):
        """Log data access"""
        self.logger.info(
            f"User {user_id} performed {action} on {resource}"
        )
    
    def log_unauthorized_access(self, user_id: str, resource: str, ip_address: str = None):
        """Log unauthorized access attempt"""
        self.logger.warning(
            f"Unauthorized access attempt by user {user_id} to {resource} from IP: {ip_address or 'unknown'}"
        )

# Create global security logger instance
security_logger = SecurityLogger() 