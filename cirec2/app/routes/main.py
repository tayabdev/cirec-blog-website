from flask import Blueprint, render_template, request, jsonify, g
from app.models import Article, Category
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.before_app_request
def load_categories():
    """Load categories for navigation"""
    g.categories = Category.query.filter_by(is_active=True).all()

@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category')
    
    # Base query for published articles
    query = Article.query.filter_by(is_published=True)
    
    # Apply category filter if provided
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    # Get featured articles for homepage
    featured_articles = Article.query.filter_by(
        is_published=True, 
        is_featured=True
    ).order_by(Article.created_at.desc()).limit(6).all()
    
    # Get latest articles with pagination
    articles = query.order_by(Article.created_at.desc()).paginate(
        page=page, 
        per_page=12, 
        error_out=False
    )
    
    # Get all categories for filter
    categories = Category.query.filter_by(is_active=True).all()
    
    # Stats for hero section
    stats = {
        'total_articles': Article.query.filter_by(is_published=True).count(),
        'total_categories': Category.query.filter_by(is_active=True).count(),
        'featured_count': Article.query.filter_by(is_published=True, is_featured=True).count()
    }
    
    return render_template('index.html',
                         articles=articles,
                         featured_articles=featured_articles,
                         categories=categories,
                         current_category=category_filter,
                         stats=stats)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/api/stats')
def api_stats():
    """API endpoint for site statistics"""
    stats = {
        'total_articles': Article.query.filter_by(is_published=True).count(),
        'total_categories': Category.query.filter_by(is_active=True).count(),
        'featured_count': Article.query.filter_by(is_published=True, is_featured=True).count()
    }
    return jsonify(stats)