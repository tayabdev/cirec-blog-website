import os
import uuid
import secrets
from datetime import datetime, timedelta
from flask import current_app, url_for, request
from flask_mail import Message
from app import mail

def generate_uuid():
    """Generate a random UUID"""
    return str(uuid.uuid4())

def generate_secure_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def format_datetime(dt, format_string='%B %d, %Y at %I:%M %p'):
    """Format datetime object to string"""
    if not dt:
        return ''
    return dt.strftime(format_string)

def format_date(dt, format_string='%B %d, %Y'):
    """Format date object to string"""
    if not dt:
        return ''
    return dt.strftime(format_string)

def time_ago(dt):
    """Return human-readable time ago string"""
    if not dt:
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def format_file_size(bytes_size):
    """Format file size in human-readable format"""
    if not bytes_size:
        return '0 B'
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

def send_email(to, subject, template, **kwargs):
    """Send email using Flask-Mail"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Set email body (you can render templates here)
        msg.body = template
        msg.html = template
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def create_breadcrumbs(items):
    """Create breadcrumb navigation"""
    breadcrumbs = []
    for item in items:
        if isinstance(item, tuple):
            text, url = item
            breadcrumbs.append({'text': text, 'url': url})
        else:
            breadcrumbs.append({'text': item, 'url': None})
    return breadcrumbs

def paginate_query(query, page, per_page=20):
    """Helper function to paginate SQLAlchemy queries"""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def safe_filename(filename, max_length=100):
    """Create a safe filename"""
    import re
    # Remove unsafe characters
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > max_length - len(ext):
        name = name[:max_length - len(ext)]
    return name + ext

def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def slugify(text, max_length=50):
    """Convert text to URL-friendly slug"""
    import re
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Limit length
    if len(text) > max_length:
        text = text[:max_length].rstrip('-')
    return text

def generate_excerpt(text, max_length=200, suffix='...'):
    """Generate excerpt from text"""
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    # Try to break at sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    last_space = truncated.rfind(' ')
    
    if last_period > max_length * 0.7:
        return text[:last_period + 1]
    elif last_space > max_length * 0.7:
        return truncated[:last_space] + suffix
    else:
        return truncated + suffix

def is_safe_url(target):
    """Check if URL is safe for redirects"""
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def flash_form_errors(form):
    """Flash form validation errors"""
    from flask import flash
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field.title()}: {error}', 'error')

def get_or_404(model, **kwargs):
    """Get model instance or raise 404"""
    from flask import abort
    instance = model.query.filter_by(**kwargs).first()
    if not instance:
        abort(404)
    return instance

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_upload_folder(folder_path):
    """Create upload folder if it doesn't exist"""
    try:
        os.makedirs(folder_path, exist_ok=True)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to create upload folder: {str(e)}")
        return False

def delete_file_safe(file_path):
    """Safely delete file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        current_app.logger.error(f"Failed to delete file {file_path}: {str(e)}")
    return False

def get_file_extension(filename):
    """Get file extension from filename"""
    if not filename:
        return ''
    return os.path.splitext(filename)[1].lower()

def validate_image_file(file):
    """Validate uploaded image file"""
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    max_size = 5 * 1024 * 1024  # 5MB
    
    errors = []
    
    if not file or not file.filename:
        errors.append('No file selected')
        return False, errors
    
    # Check extension
    ext = get_file_extension(file.filename)
    if ext not in allowed_extensions:
        errors.append('Invalid file type. Allowed: JPG, PNG, GIF, WebP')
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if size > max_size:
        errors.append(f'File too large. Maximum size: {format_file_size(max_size)}')
    
    return len(errors) == 0, errors

def create_thumbnail(image_path, thumbnail_path, size=(300, 300)):
    """Create thumbnail from image"""
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85)
            
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to create thumbnail: {str(e)}")
        return False

def get_mimetype(filename):
    """Get MIME type from filename"""
    import mimetypes
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'