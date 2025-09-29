from .main import main_bp
from .auth import auth_bp
from .admin import admin_bp
from .articles import articles_bp
from .search import search_bp

__all__ = ['main_bp', 'auth_bp', 'admin_bp', 'articles_bp', 'search_bp']