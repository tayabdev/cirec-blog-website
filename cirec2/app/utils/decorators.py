from functools import wraps
from flask import redirect, url_for, flash, request, jsonify
from flask_login import current_user
import time

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def subscription_required(f):
    """Decorator to require valid subscription"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this content.', 'error')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_subscribed() and not current_user.is_admin:
            flash('You need a subscription to access this content.', 'warning')
            return redirect(url_for('auth.profile'))
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit(max_requests=60, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        # Simple in-memory rate limiting (use Redis in production)
        requests = {}
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            now = time.time()
            client_ip = request.remote_addr
            
            # Clean old entries
            requests[client_ip] = [req_time for req_time in requests.get(client_ip, []) 
                                 if now - req_time < window]
            
            # Check rate limit
            if len(requests.get(client_ip, [])) >= max_requests:
                if request.is_json:
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                else:
                    flash('Too many requests. Please try again later.', 'error')
                    return redirect(url_for('main.index'))
            
            # Add current request
            if client_ip not in requests:
                requests[client_ip] = []
            requests[client_ip].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json(required_fields=None):
    """Decorator to validate JSON input"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or not data[field]:
                        missing_fields.append(field)
                
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'fields': missing_fields
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_response(duration=300):
    """Decorator to cache response (simple implementation)"""
    def decorator(f):
        cache = {}
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple cache key based on function name and args
            cache_key = f"{f.__name__}_{hash(str(args) + str(sorted(request.args.items())))}"
            now = time.time()
            
            # Check if cached response exists and is still valid
            if cache_key in cache:
                cached_response, timestamp = cache[cache_key]
                if now - timestamp < duration:
                    return cached_response
            
            # Generate new response
            response = f(*args, **kwargs)
            
            # Cache the response
            cache[cache_key] = (response, now)
            
            # Clean old entries (simple cleanup)
            if len(cache) > 100:  # Limit cache size
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                del cache[oldest_key]
            
            return response
        return decorated_function
    return decorator

def log_activity(action_type):
    """Decorator to log user activity"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function first
            result = f(*args, **kwargs)
            
            # Log activity (implement based on your logging needs)
            if current_user.is_authenticated:
                from flask import current_app
                current_app.logger.info(
                    f"User {current_user.id} performed action: {action_type} "
                    f"at {time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            
            return result
        return decorated_function
    return decorator