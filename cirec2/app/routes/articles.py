from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file, abort
from flask_login import login_required, current_user
from app.models import Article, Category
from app import db
import os
import uuid

articles_bp = Blueprint('articles', __name__)

@articles_bp.route('/')
def list_articles():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category')
    sort_by = request.args.get('sort', 'latest')  # latest, popular, featured
    
    # Base query for published articles
    query = Article.query.filter_by(is_published=True)
    
    # Apply category filter
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    # Apply sorting
    if sort_by == 'popular':
        query = query.order_by(Article.view_count.desc())
    elif sort_by == 'featured':
        query = query.filter_by(is_featured=True).order_by(Article.created_at.desc())
    else:  # latest
        query = query.order_by(Article.created_at.desc())
    
    # Paginate results
    articles = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Get all categories for filter dropdown
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_template('articles/list.html',
                         articles=articles,
                         categories=categories,
                         current_category=category_filter,
                         current_sort=sort_by)

@articles_bp.route('/debug/<article_uuid>')
def debug_article(article_uuid):
    """Debug route to check article existence"""
    try:
        article = Article.query.filter_by(uuid=article_uuid).first()
        if article:
            return f"""
            <h3>Article Found!</h3>
            <p>Title: {article.title}</p>
            <p>Published: {article.is_published}</p>
            <p>UUID: {article.uuid}</p>
            <p>Created: {article.created_at}</p>
            <a href="/articles/{article.uuid}">View Article</a>
            """
        else:
            all_articles = Article.query.all()
            return f"""
            <h3>Article Not Found</h3>
            <p>Looking for UUID: {article_uuid}</p>
            <h4>All Articles:</h4>
            {''.join([f'<p>{a.title} - {a.uuid} - Published: {a.is_published}</p>' for a in all_articles])}
            """
    except Exception as e:
        return f"Error: {str(e)}"

@articles_bp.route('/<uuid:article_uuid>')
def view_article(article_uuid):
    # Convert string to UUID if needed
    if isinstance(article_uuid, str):
        try:
            article_uuid = uuid.UUID(article_uuid)
        except ValueError:
            abort(404)
    
    article = Article.query.filter_by(uuid=article_uuid, is_published=True).first_or_404()
    
    # Increment view count
    article.increment_view_count()
    
    # Check if user can access full content
    can_access_full = False
    if current_user.is_authenticated:
        can_access_full = current_user.is_subscribed() or current_user.is_admin
    
    # Get related articles (same category, excluding current)
    related_articles = Article.query.filter(
        Article.category == article.category,
        Article.id != article.id,
        Article.is_published == True
    ).order_by(Article.view_count.desc()).limit(4).all()
    
    return render_template('articles/detail.html',
                         article=article,
                         can_access_full=can_access_full,
                         related_articles=related_articles)

@articles_bp.route('/<uuid:article_uuid>/preview')
def preview_article(article_uuid):
    """Show article preview for non-subscribed users"""
    article = Article.query.filter_by(uuid=article_uuid, is_published=True).first_or_404()
    
    # Only show preview content
    return render_template('articles/preview.html', article=article)

@articles_bp.route('/<uuid:article_uuid>/download')
@login_required
def download_pdf(article_uuid):
    """Download PDF file - requires login"""
    article = Article.query.filter_by(uuid=article_uuid, is_published=True).first_or_404()
    
    # Check if user can download
    if not (current_user.is_subscribed() or current_user.is_admin):
        flash('You need a subscription to download articles.', 'error')
        return redirect(url_for('articles.view_article', article_uuid=article_uuid))
    
    # Check if file exists
    if not os.path.exists(article.pdf_path):
        flash('PDF file not found.', 'error')
        return redirect(url_for('articles.view_article', article_uuid=article_uuid))
    
    # Increment download count
    article.increment_download_count()
    
    # Send file
    try:
        return send_file(
            article.pdf_path,
            as_attachment=True,
            download_name=f"{article.title}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        flash('Error downloading file. Please try again.', 'error')
        return redirect(url_for('articles.view_article', article_uuid=article_uuid))

@articles_bp.route('/category/<category_name>')
def category_articles(category_name):
    """Show articles in a specific category"""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'latest')
    
    # Get category
    category = Category.query.filter_by(slug=category_name, is_active=True).first_or_404()
    
    # Base query for published articles in this category
    query = Article.query.filter_by(is_published=True, category=category.name)
    
    # Apply sorting
    if sort_by == 'popular':
        query = query.order_by(Article.view_count.desc())
    elif sort_by == 'featured':
        query = query.filter_by(is_featured=True).order_by(Article.created_at.desc())
    else:  # latest
        query = query.order_by(Article.created_at.desc())
    
    # Paginate results
    articles = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('articles/category.html',
                         articles=articles,
                         category=category,
                         current_sort=sort_by)

@articles_bp.route('/api/<uuid:article_uuid>/like', methods=['POST'])
@login_required
def like_article(article_uuid):
    """API endpoint to like/unlike an article"""
    article = Article.query.filter_by(uuid=article_uuid).first_or_404()
    
    # For now, just increment view count as a proxy for likes
    # You can implement a proper likes system with a separate table
    article.increment_view_count()
    
    return jsonify({
        'success': True,
        'view_count': article.view_count
    })

@articles_bp.route('/api/popular')
def api_popular_articles():
    """API endpoint for popular articles"""
    limit = request.args.get('limit', 5, type=int)
    
    articles = Article.query.filter_by(is_published=True)\
        .order_by(Article.view_count.desc())\
        .limit(limit).all()
    
    return jsonify([article.to_dict() for article in articles])

@articles_bp.route('/api/featured')
def api_featured_articles():
    """API endpoint for featured articles"""
    limit = request.args.get('limit', 6, type=int)
    
    articles = Article.query.filter_by(is_published=True, is_featured=True)\
        .order_by(Article.created_at.desc())\
        .limit(limit).all()
    
    return jsonify([article.to_dict() for article in articles])

@articles_bp.route('/api/recent')
def api_recent_articles():
    """API endpoint for recent articles"""
    limit = request.args.get('limit', 10, type=int)
    
    articles = Article.query.filter_by(is_published=True)\
        .order_by(Article.created_at.desc())\
        .limit(limit).all()
    
    return jsonify([article.to_dict() for article in articles])