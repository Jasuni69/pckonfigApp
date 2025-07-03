from passlib.context import CryptContext
import re


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
   
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    
    return pwd_context.hash(password)

def validate_password_strength(password: str) -> dict:
    """
    Validate password strength according to security best practices.
    Returns dict with validation result and error messages.
    """
    errors = []
    
    # Check minimum length
    if len(password) < 8:
        errors.append("Lösenordet måste vara minst 8 tecken långt")
    
    # Check for at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        errors.append("Lösenordet måste innehålla minst en stor bokstav")
    
    # Check for at least one lowercase letter
    if not re.search(r"[a-z]", password):
        errors.append("Lösenordet måste innehålla minst en liten bokstav")
    
    # Check for at least one digit
    if not re.search(r"\d", password):
        errors.append("Lösenordet måste innehålla minst en siffra")
    
    # Check for at least one special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Lösenordet måste innehålla minst ett specialtecken")
    
    # Check for common weak patterns
    common_patterns = ["123456", "password", "qwerty", "abc123"]
    if any(pattern in password.lower() for pattern in common_patterns):
        errors.append("Lösenordet innehåller vanliga osäkra mönster")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }
