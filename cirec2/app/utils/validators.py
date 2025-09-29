import re
from email_validator import validate_email as email_validator, EmailNotValidError

def validate_email(email):
    """Validate email address format"""
    try:
        # Use email-validator library for comprehensive validation
        validated_email = email_validator(email)
        return True
    except EmailNotValidError:
        return False

def validate_password(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters long
    - Contains at least one letter
    - Contains at least one number
    """
    if not password or len(password) < 8:
        return False
    
    # Check for at least one letter
    if not re.search(r'[a-zA-Z]', password):
        return False
    
    # Check for at least one number
    if not re.search(r'\d', password):
        return False
    
    return True

def validate_name(name):
    """Validate name (first name, last name)"""
    if not name or len(name.strip()) < 2:
        return False
    
    # Only allow letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", name.strip()):
        return False
    
    return True

def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False
    
    return True

def validate_url(url):
    """Validate URL format"""
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    if not filename:
        return ''
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\-_\. ]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Trim and limit length
    filename = filename.strip('_')[:100]
    
    return filename

def validate_article_data(data):
    """Validate article form data"""
    errors = []
    
    # Required fields
    required_fields = ['title', 'description', 'author', 'category']
    for field in required_fields:
        if not data.get(field, '').strip():
            errors.append(f'{field.title()} is required.')
    
    # Title length
    title = data.get('title', '').strip()
    if title and (len(title) < 5 or len(title) > 255):
        errors.append('Title must be between 5 and 255 characters.')
    
    # Description length
    description = data.get('description', '').strip()
    if description and (len(description) < 10 or len(description) > 1000):
        errors.append('Description must be between 10 and 1000 characters.')
    
    # Author name
    author = data.get('author', '').strip()
    if author and not validate_name(author):
        errors.append('Author name contains invalid characters.')
    
    return errors

def validate_search_query(query):
    """Validate search query"""
    if not query or not query.strip():
        return False
    
    # Check minimum length
    if len(query.strip()) < 2:
        return False
    
    # Check maximum length
    if len(query.strip()) > 200:
        return False
    
    # Check for malicious patterns (basic SQL injection prevention)
    malicious_patterns = [
        r';\s*(drop|delete|truncate|alter)\s',
        r'union\s+select',
        r'<script',
        r'javascript:',
        r'eval\s*\(',
    ]
    
    query_lower = query.lower()
    for pattern in malicious_patterns:
        if re.search(pattern, query_lower):
            return False
    
    return True

def clean_html_tags(text):
    """Remove HTML tags from text"""
    if not text:
        return ''
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    import html
    clean_text = html.unescape(clean_text)
    
    return clean_text.strip()

def truncate_text(text, max_length=100, suffix='...'):
    """Truncate text to specified length"""
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    # Try to break at word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length // 2:  # Only break at word if not too short
        truncated = truncated[:last_space]
    
    return truncated + suffix