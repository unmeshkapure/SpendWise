from pydantic import EmailStr, ValidationError
import re
from typing import Dict, Any, Optional, Union
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class ValidationException(Exception):
    """Custom exception for validation errors"""
    pass

def validate_email(email: str) -> bool:
    """
    Validate email format using regex pattern
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email is valid, raises ValidationException otherwise
        
    Raises:
        ValidationException: If email format is invalid
    """
    if not email:
        raise ValidationException("Email is required")
    
    # RFC 5322 compliant email regex (simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationException(f"Invalid email format: {email}")
    
    # Additional checks
    if len(email) > 254:  # RFC 5321 limit
        raise ValidationException("Email address is too long (max 254 characters)")
    
    local, domain = email.rsplit('@', 1)
    if len(local) > 64:  # RFC 5321 limit for local part
        raise ValidationException("Email local part is too long (max 64 characters)")
    
    return True

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if phone number is valid, raises ValidationException otherwise
    """
    if not phone:
        raise ValidationException("Phone number is required")
    
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Indian phone number
    if phone.startswith('+91') or phone.startswith('91'):
        # Indian numbers: 10 digits after country code
        if len(clean_phone) != 12:  # 2 for country code + 10 for number
            raise ValidationException("Invalid Indian phone number format")
        if not clean_phone[2:].isdigit() or not (clean_phone[2:].startswith('6') or 
                                               clean_phone[2:].startswith('7') or 
                                               clean_phone[2:].startswith('8') or 
                                               clean_phone[2:].startswith('9')):
            raise ValidationException("Invalid Indian phone number (should start with 6,7,8,9)")
    elif phone.startswith('+'):
        # International format
        if len(clean_phone) < 7 or len(clean_phone) > 15:
            raise ValidationException("International phone number should be 7-15 digits")
    else:
        # Assume Indian format without country code
        if len(clean_phone) != 10:
            raise ValidationException("Indian phone number should be 10 digits")
        if not clean_phone.startswith('6') and not clean_phone.startswith('7') and \
           not clean_phone.startswith('8') and not clean_phone.startswith('9'):
            raise ValidationException("Invalid Indian phone number (should start with 6,7,8,9)")
    
    return True

def validate_username(username: str) -> bool:
    """
    Validate username format and constraints
    
    Args:
        username (str): Username to validate
        
    Returns:
        bool: True if username is valid, raises ValidationException otherwise
    """
    if not username:
        raise ValidationException("Username is required")
    
    if len(username) < 3:
        raise ValidationException("Username must be at least 3 characters long")
    
    if len(username) > 30:
        raise ValidationException("Username must be no more than 30 characters long")
    
    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValidationException("Username can only contain alphanumeric characters, underscores, and hyphens")
    
    # Check for consecutive special characters
    if re.search(r'[-_]{2,}', username):
        raise ValidationException("Username cannot contain consecutive special characters")
    
    # Check if starts with special character
    if username[0] in ['-', '_']:
        raise ValidationException("Username cannot start with a special character")
    
    # Check if ends with special character
    if username[-1] in ['-', '_']:
        raise ValidationException("Username cannot end with a special character")
    
    return True

def validate_password(password: str) -> bool:
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
        
    Returns:
        bool: True if password is valid, raises ValidationException otherwise
    """
    if not password:
        raise ValidationException("Password is required")
    
    if len(password) < 8:
        raise ValidationException("Password must be at least 8 characters long")
    
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise ValidationException("Password must contain at least one uppercase letter")
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise ValidationException("Password must contain at least one lowercase letter")
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        raise ValidationException("Password must contain at least one digit")
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationException("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
    
    # Check for common patterns that are not secure
    common_patterns = [
        r'(.)\1{2,}',  # Three or more consecutive identical characters
        r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
        r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
    ]
    
    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            raise ValidationException("Password contains common patterns that are not secure")
    
    return True

def validate_amount(amount: Union[float, int]) -> bool:
    """
    Validate monetary amount
    
    Args:
        amount (Union[float, int]): Amount to validate
        
    Returns:
        bool: True if amount is valid, raises ValidationException otherwise
    """
    if amount is None:
        raise ValidationException("Amount is required")
    
    if not isinstance(amount, (int, float)):
        raise ValidationException("Amount must be a number")
    
    if amount < 0:
        raise ValidationException("Amount must be non-negative")
    
    if amount > 999999999.99:  # Max 99 crore
        raise ValidationException("Amount is too large (max 99,99,99,999.99)")
    
    # Check for reasonable precision (2 decimal places)
    if isinstance(amount, float) and len(str(amount).split('.')[-1]) > 2:
        raise ValidationException("Amount should have maximum 2 decimal places")
    
    return True

def validate_date(date_str: str) -> bool:
    """
    Validate date string format (ISO format: YYYY-MM-DD)
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        bool: True if date is valid, raises ValidationException otherwise
    """
    if not date_str:
        raise ValidationException("Date is required")
    
    try:
        # Parse ISO format date
        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        # Check if it's a reasonable date (not too far in past or future)
        current_year = datetime.now().year
        if parsed_date.year < 1900 or parsed_date.year > current_year + 10:
            raise ValidationException(f"Date year must be between 1900 and {current_year + 10}")
        
        return True
    except ValueError:
        raise ValidationException(f"Invalid date format: {date_str}. Expected ISO format (YYYY-MM-DD)")

def validate_future_date(date_str: str) -> bool:
    """
    Validate that date is in the future
    
    Args:
        date_str (str): Date string to validate
        
    Returns:
        bool: True if date is in the future, raises ValidationException otherwise
    """
    if not validate_date(date_str):
        return False
    
    parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    current_date = datetime.now()
    
    if parsed_date <= current_date:
        raise ValidationException("Date must be in the future")
    
    return True

def validate_transaction_data(data: Dict[str, Any]) -> bool:
    """
    Validate transaction data
    
    Args:
        data (Dict[str, Any]): Transaction data to validate
        
    Returns:
        bool: True if data is valid, raises ValidationException otherwise
    """
    if not isinstance(data, dict):
        raise ValidationException("Transaction data must be a dictionary")
    
    # Validate amount
    amount = data.get('amount')
    if amount is None:
        raise ValidationException("Amount is required")
    validate_amount(amount)
    
    # Validate category
    category = data.get('category', '').strip()
    if not category:
        raise ValidationException("Category is required")
    
    if len(category) > 50:
        raise ValidationException("Category name is too long (max 50 characters)")
    
    # Validate type
    transaction_type = data.get('type', '').strip().lower()
    if transaction_type not in ['income', 'expense']:
        raise ValidationException("Type must be either 'income' or 'expense'")
    
    # Validate description (optional)
    description = data.get('description', '')
    if description and len(description) > 500:
        raise ValidationException("Description is too long (max 500 characters)")
    
    # Validate date (optional, defaults to now)
    date_val = data.get('date')
    if date_val:
        if isinstance(date_val, (datetime, date)):
            pass
        elif isinstance(date_val, str):
            validate_date(date_val)
        else:
            raise ValidationException("Date must be a string or datetime object")
    
    return True

def validate_savings_goal_data(data: Dict[str, Any]) -> bool:
    """
    Validate savings goal data
    
    Args:
        data (Dict[str, Any]): Savings goal data to validate
        
    Returns:
        bool: True if data is valid, raises ValidationException otherwise
    """
    if not isinstance(data, dict):
        raise ValidationException("Savings goal data must be a dictionary")
    
    # Validate title
    title = data.get('title', '').strip()
    if not title:
        raise ValidationException("Title is required")
    
    if len(title) < 3:
        raise ValidationException("Title must be at least 3 characters long")
    
    if len(title) > 100:
        raise ValidationException("Title is too long (max 100 characters)")
    
    # Validate target amount
    target_amount = data.get('target_amount')
    if target_amount is None:
        raise ValidationException("Target amount is required")
    validate_amount(target_amount)
    
    # Validate target date
    target_date = data.get('target_date')
    if not target_date:
        raise ValidationException("Target date is required")
    validate_future_date(target_date)
    
    # Validate description (optional)
    description = data.get('description', '')
    if description and len(description) > 500:
        raise ValidationException("Description is too long (max 500 characters)")
    
    return True

def validate_user_data(data: Dict[str, Any]) -> bool:
    """
    Validate user registration data
    
    Args:
        data (Dict[str, Any]): User data to validate
        
    Returns:
        bool: True if data is valid, raises ValidationException otherwise
    """
    if not isinstance(data, dict):
        raise ValidationException("User data must be a dictionary")
    
    # Validate email
    email = data.get('email', '').strip()
    if not email:
        raise ValidationException("Email is required")
    validate_email(email)
    
    # Validate username
    username = data.get('username', '').strip()
    if not username:
        raise ValidationException("Username is required")
    validate_username(username)
    
    # Validate password
    password = data.get('password', '')
    if not password:
        raise ValidationException("Password is required")
    validate_password(password)
    
    # Validate full name (optional)
    full_name = data.get('full_name', '').strip()
    if full_name:
        if len(full_name) < 2:
            raise ValidationException("Full name must be at least 2 characters long")
        if len(full_name) > 100:
            raise ValidationException("Full name is too long (max 100 characters)")
        if not re.match(r'^[a-zA-Z\s\-\']+$', full_name):
            raise ValidationException("Full name can only contain letters, spaces, hyphens, and apostrophes")
    
    return True

def validate_pagination_params(page: int = 1, limit: int = 10) -> bool:
    """
    Validate pagination parameters
    
    Args:
        page (int): Page number (default 1)
        limit (int): Items per page (default 10)
        
    Returns:
        bool: True if parameters are valid, raises ValidationException otherwise
    """
    if not isinstance(page, int) or page < 1:
        raise ValidationException("Page number must be a positive integer")
    
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        raise ValidationException("Limit must be a positive integer between 1 and 100")
    
    return True

def validate_category(category: str) -> bool:
    """
    Validate transaction category
    
    Args:
        category (str): Category to validate
        
    Returns:
        bool: True if category is valid, raises ValidationException otherwise
    """
    if not category:
        raise ValidationException("Category is required")
    
    if len(category.strip()) == 0:
        raise ValidationException("Category cannot be empty")
    
    if len(category) > 50:
        raise ValidationException("Category name is too long (max 50 characters)")
    
    # Check for valid characters
    if not re.match(r'^[a-zA-Z\s\-\_]+$', category.strip()):
        raise ValidationException("Category can only contain letters, spaces, hyphens, and underscores")
    
    return True

def validate_transaction_type(transaction_type: str) -> bool:
    """
    Validate transaction type
    
    Args:
        transaction_type (str): Type to validate
        
    Returns:
        bool: True if type is valid, raises ValidationException otherwise
    """
    if not transaction_type:
        raise ValidationException("Transaction type is required")
    
    normalized_type = transaction_type.strip().lower()
    if normalized_type not in ['income', 'expense']:
        raise ValidationException("Transaction type must be either 'income' or 'expense'")
    
    return True

def validate_positive_number(value: Union[int, float], field_name: str = "Value") -> bool:
    """
    Validate that a number is positive
    
    Args:
        value (Union[int, float]): Number to validate
        field_name (str): Name of the field for error message
        
    Returns:
        bool: True if number is positive, raises ValidationException otherwise
    """
    if value is None:
        raise ValidationException(f"{field_name} is required")
    
    if not isinstance(value, (int, float)):
        raise ValidationException(f"{field_name} must be a number")
    
    if value <= 0:
        raise ValidationException(f"{field_name} must be positive")
    
    return True

def validate_string_length(value: str, min_length: int, max_length: int, field_name: str = "Field") -> bool:
    """
    Validate string length
    
    Args:
        value (str): String to validate
        min_length (int): Minimum length
        max_length (int): Maximum length
        field_name (str): Name of the field for error message
        
    Returns:
        bool: True if string length is valid, raises ValidationException otherwise
    """
    if value is None:
        raise ValidationException(f"{field_name} is required")
    
    if not isinstance(value, str):
        raise ValidationException(f"{field_name} must be a string")
    
    if len(value) < min_length:
        raise ValidationException(f"{field_name} must be at least {min_length} characters long")
    
    if len(value) > max_length:
        raise ValidationException(f"{field_name} must be no more than {max_length} characters long")
    
    return True

def validate_percentage(value: Union[int, float]) -> bool:
    """
    Validate percentage value
    
    Args:
        value (Union[int, float]): Percentage to validate
        
    Returns:
        bool: True if percentage is valid, raises ValidationException otherwise
    """
    if value is None:
        raise ValidationException("Percentage is required")
    
    if not isinstance(value, (int, float)):
        raise ValidationException("Percentage must be a number")
    
    if value < 0 or value > 100:
        raise ValidationException("Percentage must be between 0 and 100")
    
    return True

def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is valid, raises ValidationException otherwise
    """
    if not url:
        raise ValidationException("URL is required")
    
    # Simple URL regex
    pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    
    if not re.match(pattern, url):
        raise ValidationException(f"Invalid URL format: {url}")
    
    if len(url) > 2048:  # RFC 7230 limit
        raise ValidationException("URL is too long (max 2048 characters)")
    
    return True

def validate_json(json_str: str) -> bool:
    """
    Validate JSON string
    
    Args:
        json_str (str): JSON string to validate
        
    Returns:
        bool: True if JSON is valid, raises ValidationException otherwise
    """
    import json
    
    if not json_str:
        raise ValidationException("JSON string is required")
    
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError as e:
        raise ValidationException(f"Invalid JSON format: {str(e)}")

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and other injection attacks
    
    Args:
        text (str): Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = text.replace('<', '&lt;').replace('>', '&gt;')
    sanitized = sanitized.replace('"', '&quot;').replace("'", '&#x27;')
    sanitized = sanitized.replace('/', '&#x2F;')
    
    # Remove script tags (case insensitive)
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)
    
    return sanitized

def validate_input_length(text: str, max_length: int = 1000, field_name: str = "Input") -> bool:
    """
    Validate input length to prevent buffer overflow
    
    Args:
        text (str): Input text to validate
        max_length (int): Maximum allowed length
        field_name (str): Name of the field for error message
        
    Returns:
        bool: True if input length is valid, raises ValidationException otherwise
    """
    if text is None:
        raise ValidationException(f"{field_name} is required")
    
    if not isinstance(text, str):
        raise ValidationException(f"{field_name} must be a string")
    
    if len(text) > max_length:
        raise ValidationException(f"{field_name} exceeds maximum length of {max_length} characters")
    
    return True

def validate_uuid(uuid_str: str) -> bool:
    """
    Validate UUID format
    
    Args:
        uuid_str (str): UUID string to validate
        
    Returns:
        bool: True if UUID is valid, raises ValidationException otherwise
    """
    import uuid
    
    if not uuid_str:
        raise ValidationException("UUID is required")
    
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        raise ValidationException(f"Invalid UUID format: {uuid_str}")

def validate_enum(value: str, valid_values: list, field_name: str = "Value") -> bool:
    """
    Validate that value is in allowed enum values
    
    Args:
        value (str): Value to validate
        valid_values (list): List of valid values
        field_name (str): Name of the field for error message
        
    Returns:
        bool: True if value is valid, raises ValidationException otherwise
    """
    if value is None:
        raise ValidationException(f"{field_name} is required")
    
    if value not in valid_values:
        raise ValidationException(f"{field_name} must be one of: {', '.join(valid_values)}")
    
    return True

def validate_credit_card_number(card_number: str) -> bool:
    """
    Validate credit card number using Luhn algorithm
    
    Args:
        card_number (str): Credit card number to validate
        
    Returns:
        bool: True if card number is valid, raises ValidationException otherwise
    """
    if not card_number:
        raise ValidationException("Credit card number is required")
    
    # Remove spaces and hyphens
    clean_number = re.sub(r'[\s-]', '', card_number)
    
    # Check if it's all digits
    if not clean_number.isdigit():
        raise ValidationException("Credit card number must contain only digits")
    
    # Check length (13-19 digits)
    if len(clean_number) < 13 or len(clean_number) > 19:
        raise ValidationException("Credit card number must be 13-19 digits long")
    
    # Luhn algorithm
    def luhn_check(card_num):
        digits = [int(d) for d in card_num]
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        return sum(digits) % 10 == 0
    
    if not luhn_check(clean_number):
        raise ValidationException("Invalid credit card number")
    
    return True

def validate_pin(pin: str) -> bool:
    """
    Validate PIN code (for Indian addresses)
    
    Args:
        pin (str): PIN code to validate
        
    Returns:
        bool: True if PIN is valid, raises ValidationException otherwise
    """
    if not pin:
        raise ValidationException("PIN code is required")
    
    # Remove spaces
    clean_pin = re.sub(r'\s', '', pin)
    
    # Check if it's exactly 6 digits
    if not re.match(r'^\d{6}$', clean_pin):
        raise ValidationException("PIN code must be exactly 6 digits")
    
    # Check if it's a valid Indian PIN (first digit 1-8)
    if clean_pin[0] not in '12345678':
        raise ValidationException("Invalid Indian PIN code")
    
    return True

# Validation utility class for batch validation
class BatchValidator:
    """Utility class for batch validation of multiple fields"""
    
    def __init__(self):
        self.errors = []
    
    def add_error(self, field: str, message: str):
        """Add validation error"""
        self.errors.append(f"{field}: {message}")
    
    def validate_email(self, email: str, field_name: str = "email"):
        """Validate email and add error if invalid"""
        try:
            validate_email(email)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_username(self, username: str, field_name: str = "username"):
        """Validate username and add error if invalid"""
        try:
            validate_username(username)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_password(self, password: str, field_name: str = "password"):
        """Validate password and add error if invalid"""
        try:
            validate_password(password)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_amount(self, amount: Union[float, int], field_name: str = "amount"):
        """Validate amount and add error if invalid"""
        try:
            validate_amount(amount)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_date(self, date_str: str, field_name: str = "date"):
        """Validate date and add error if invalid"""
        try:
            validate_date(date_str)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_string_length(self, value: str, min_length: int, max_length: int, field_name: str = "field"):
        """Validate string length and add error if invalid"""
        try:
            validate_string_length(value, min_length, max_length, field_name)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def has_errors(self) -> bool:
        """Check if there are validation errors"""
        return len(self.errors) > 0
    
    def get_errors(self) -> list:
        """Get list of validation errors"""
        return self.errors.copy()
    
    def clear_errors(self):
        """Clear all validation errors"""
        self.errors.clear()
    
    def validate_all(self, data: Dict[str, Any]) -> bool:
        """Validate all fields in data dictionary"""
        # This is a template - implement based on your specific needs
        # Example implementation for user registration:
        self.validate_email(data.get('email', ''), 'email')
        self.validate_username(data.get('username', ''), 'username')
        self.validate_password(data.get('password', ''), 'password')
        
        full_name = data.get('full_name', '')
        if full_name:
            self.validate_string_length(full_name, 2, 100, 'full_name')
        
        return not self.has_errors()

# Example usage function
def validate_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user registration data using batch validation
    
    Args:
        data (Dict[str, Any]): Registration data
        
    Returns:
        Dict[str, Any]: Validation result with errors if any
    """
    validator = BatchValidator()
    
    # Validate required fields
    validator.validate_email(data.get('email', ''), 'email')
    validator.validate_username(data.get('username', ''), 'username')
    validator.validate_password(data.get('password', ''), 'password')
    
    # Validate optional fields
    full_name = data.get('full_name', '')
    if full_name:
        validator.validate_string_length(full_name, 2, 100, 'full_name')
    
    return {
        'valid': not validator.has_errors(),
        'errors': validator.get_errors()
    }

# Logging validation events
def log_validation_event(field_name: str, value: Any, is_valid: bool, error_message: str = None):
    """Log validation events for monitoring"""
    if is_valid:
        logger.info(f"Validation passed for field '{field_name}'")
    else:
        logger.warning(f"Validation failed for field '{field_name}': {error_message}")

# Performance validation (for API rate limiting)
def validate_rate_limit(request_count: int, limit: int, window_seconds: int) -> bool:
    """
    Validate rate limit (simplified implementation)
    
    Returns:
        bool: True if value is valid, raises ValidationException otherwise
    """
    if value is None:
        raise ValidationException(f"{field_name} is required")
    
    if value not in valid_values:
        raise ValidationException(f"{field_name} must be one of: {', '.join(valid_values)}")
    
    return True

def validate_credit_card_number(card_number: str) -> bool:
    """
    Validate credit card number using Luhn algorithm
    
    Args:
        card_number (str): Credit card number to validate
        
    Returns:
        bool: True if card number is valid, raises ValidationException otherwise
    """
    if not card_number:
        raise ValidationException("Credit card number is required")
    
    # Remove spaces and hyphens
    clean_number = re.sub(r'[\s-]', '', card_number)
    
    # Check if it's all digits
    if not clean_number.isdigit():
        raise ValidationException("Credit card number must contain only digits")
    
    # Check length (13-19 digits)
    if len(clean_number) < 13 or len(clean_number) > 19:
        raise ValidationException("Credit card number must be 13-19 digits long")
    
    # Luhn algorithm
    def luhn_check(card_num):
        digits = [int(d) for d in card_num]
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        return sum(digits) % 10 == 0
    
    if not luhn_check(clean_number):
        raise ValidationException("Invalid credit card number")
    
    return True

def validate_pin(pin: str) -> bool:
    """
    Validate PIN code (for Indian addresses)
    
    Args:
        pin (str): PIN code to validate
        
    Returns:
        bool: True if PIN is valid, raises ValidationException otherwise
    """
    if not pin:
        raise ValidationException("PIN code is required")
    
    # Remove spaces
    clean_pin = re.sub(r'\s', '', pin)
    
    # Check if it's exactly 6 digits
    if not re.match(r'^\d{6}$', clean_pin):
        raise ValidationException("PIN code must be exactly 6 digits")
    
    # Check if it's a valid Indian PIN (first digit 1-8)
    if clean_pin[0] not in '12345678':
        raise ValidationException("Invalid Indian PIN code")
    
    return True

# Validation utility class for batch validation
class BatchValidator:
    """Utility class for batch validation of multiple fields"""
    
    def __init__(self):
        self.errors = []
    
    def add_error(self, field: str, message: str):
        """Add validation error"""
        self.errors.append(f"{field}: {message}")
    
    def validate_email(self, email: str, field_name: str = "email"):
        """Validate email and add error if invalid"""
        try:
            validate_email(email)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_username(self, username: str, field_name: str = "username"):
        """Validate username and add error if invalid"""
        try:
            validate_username(username)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_password(self, password: str, field_name: str = "password"):
        """Validate password and add error if invalid"""
        try:
            validate_password(password)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_amount(self, amount: Union[float, int], field_name: str = "amount"):
        """Validate amount and add error if invalid"""
        try:
            validate_amount(amount)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_date(self, date_str: str, field_name: str = "date"):
        """Validate date and add error if invalid"""
        try:
            validate_date(date_str)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_string_length(self, value: str, min_length: int, max_length: int, field_name: str = "field"):
        """Validate string length and add error if invalid"""
        try:
            validate_string_length(value, min_length, max_length, field_name)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def has_errors(self) -> bool:
        """Check if there are validation errors"""
        return len(self.errors) > 0
    
    def get_errors(self) -> list:
        """Get list of validation errors"""
        return self.errors.copy()
    
    def clear_errors(self):
        """Clear all validation errors"""
        self.errors.clear()
    
    def validate_all(self, data: Dict[str, Any]) -> bool:
        """Validate all fields in data dictionary"""
        # This is a template - implement based on your specific needs
        # Example implementation for user registration:
        self.validate_email(data.get('email', ''), 'email')
        self.validate_username(data.get('username', ''), 'username')
        self.validate_password(data.get('password', ''), 'password')
        
        full_name = data.get('full_name', '')
        if full_name:
            self.validate_string_length(full_name, 2, 100, 'full_name')
        
        return not self.has_errors()

# Example usage function
def validate_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user registration data using batch validation
    
    Args:
        data (Dict[str, Any]): Registration data
        
    Returns:
        Dict[str, Any]: Validation result with errors if any
    """
    validator = BatchValidator()
    
    # Validate required fields
    validator.validate_email(data.get('email', ''), 'email')
    validator.validate_username(data.get('username', ''), 'username')
    validator.validate_password(data.get('password', ''), 'password')
    
    # Validate optional fields
    full_name = data.get('full_name', '')
    if full_name:
        validator.validate_string_length(full_name, 2, 100, 'full_name')
    
    return {
        'valid': not validator.has_errors(),
        'errors': validator.get_errors()
    }

# Logging validation events
def log_validation_event(field_name: str, value: Any, is_valid: bool, error_message: str = None):
    """Log validation events for monitoring"""
    if is_valid:
        logger.info(f"Validation passed for field '{field_name}'")
    else:
        logger.warning(f"Validation failed for field '{field_name}': {error_message}")

# Performance validation (for API rate limiting)
def validate_rate_limit(request_count: int, limit: int, window_seconds: int) -> bool:
    """
    Validate rate limit (simplified implementation)
    
    Args:
        request_count (int): Number of requests in current window
        limit (int): Maximum allowed requests
        window_seconds (int): Time window in seconds
        
    Returns:
        bool: True if within rate limit
    """
    if request_count > limit:
        logger.warning(f"Rate limit exceeded: {request_count}/{limit} requests in {window_seconds}s")
        return False
    return True

def validate_credit_card_number(card_number: str) -> bool:
    """
    Validate credit card number using Luhn algorithm
    
    Args:
        card_number (str): Credit card number to validate
        
    Returns:
        bool: True if card number is valid, raises ValidationException otherwise
    """
    if not card_number:
        raise ValidationException("Credit card number is required")
    
    # Remove spaces and hyphens
    clean_number = re.sub(r'[\s-]', '', card_number)
    
    # Check if it's all digits
    if not clean_number.isdigit():
        raise ValidationException("Credit card number must contain only digits")
    
    # Check length (13-19 digits)
    if len(clean_number) < 13 or len(clean_number) > 19:
        raise ValidationException("Credit card number must be 13-19 digits long")
    
    # Luhn algorithm
    def luhn_check(card_num):
        digits = [int(d) for d in card_num]
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
        return sum(digits) % 10 == 0
    
    if not luhn_check(clean_number):
        raise ValidationException("Invalid credit card number")
    
    return True

def validate_pin(pin: str) -> bool:
    """
    Validate PIN code (for Indian addresses)
    
    Args:
        pin (str): PIN code to validate
        
    Returns:
        bool: True if PIN is valid, raises ValidationException otherwise
    """
    if not pin:
        raise ValidationException("PIN code is required")
    
    # Remove spaces
    clean_pin = re.sub(r'\s', '', pin)
    
    # Check if it's exactly 6 digits
    if not re.match(r'^\d{6}$', clean_pin):
        raise ValidationException("PIN code must be exactly 6 digits")
    
    # Check if it's a valid Indian PIN (first digit 1-8)
    if clean_pin[0] not in '12345678':
        raise ValidationException("Invalid Indian PIN code")
    
    return True

# Validation utility class for batch validation
class BatchValidator:
    """Utility class for batch validation of multiple fields"""
    
    def __init__(self):
        self.errors = []
    
    def add_error(self, field: str, message: str):
        """Add validation error"""
        self.errors.append(f"{field}: {message}")
    
    def validate_email(self, email: str, field_name: str = "email"):
        """Validate email and add error if invalid"""
        try:
            validate_email(email)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_username(self, username: str, field_name: str = "username"):
        """Validate username and add error if invalid"""
        try:
            validate_username(username)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_password(self, password: str, field_name: str = "password"):
        """Validate password and add error if invalid"""
        try:
            validate_password(password)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_amount(self, amount: Union[float, int], field_name: str = "amount"):
        """Validate amount and add error if invalid"""
        try:
            validate_amount(amount)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_date(self, date_str: str, field_name: str = "date"):
        """Validate date and add error if invalid"""
        try:
            validate_date(date_str)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def validate_string_length(self, value: str, min_length: int, max_length: int, field_name: str = "field"):
        """Validate string length and add error if invalid"""
        try:
            validate_string_length(value, min_length, max_length, field_name)
        except ValidationException as e:
            self.add_error(field_name, str(e))
    
    def has_errors(self) -> bool:
        """Check if there are validation errors"""
        return len(self.errors) > 0
    
    def get_errors(self) -> list:
        """Get list of validation errors"""
        return self.errors.copy()
    
    def clear_errors(self):
        """Clear all validation errors"""
        self.errors.clear()
    
    def validate_all(self, data: Dict[str, Any]) -> bool:
        """Validate all fields in data dictionary"""
        # This is a template - implement based on your specific needs
        # Example implementation for user registration:
        self.validate_email(data.get('email', ''), 'email')
        self.validate_username(data.get('username', ''), 'username')
        self.validate_password(data.get('password', ''), 'password')
        
        full_name = data.get('full_name', '')
        if full_name:
            self.validate_string_length(full_name, 2, 100, 'full_name')
        
        return not self.has_errors()

# Example usage function
def validate_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user registration data using batch validation
    
    Args:
        data (Dict[str, Any]): Registration data
        
    Returns:
        Dict[str, Any]: Validation result with errors if any
    """
    validator = BatchValidator()
    
    # Validate required fields
    validator.validate_email(data.get('email', ''), 'email')
    validator.validate_username(data.get('username', ''), 'username')
    validator.validate_password(data.get('password', ''), 'password')
    
    # Validate optional fields
    full_name = data.get('full_name', '')
    if full_name:
        validator.validate_string_length(full_name, 2, 100, 'full_name')
    
    return {
        'valid': not validator.has_errors(),
        'errors': validator.get_errors()
    }

