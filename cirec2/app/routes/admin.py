from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Article, Category, User
from app.services.pdf_processor import PDFProcessor
from app.services.embedding_service import EmbeddingService
from werkzeug.utils import secure_filename
import os
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    stats = {
        'total_articles': Article.query.count(),
        'published_articles': Article.query.filter_by(is_published=True).count(),
        'draft_articles': Article.query.filter_by(is_published=False).count(),
        'total_users': User.query.count(),
        'total_categories': Category.query.count()
    }
    
    # Get recent articles
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    
    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_articles=recent_articles,
                         recent_users=recent_users)

@admin_bp.route('/articles')
@login_required
@admin_required
def articles():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category')
    
    # Base query
    query = Article.query
    
    # Apply filters
    if status_filter == 'published':
        query = query.filter_by(is_published=True)
    elif status_filter == 'draft':
        query = query.filter_by(is_published=False)
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    # Paginate
    articles = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get categories for filter
    categories = Category.query.all()
    
    return render_template('admin/articles.html',
                         articles=articles,
                         categories=categories,
                         status_filter=status_filter,
                         category_filter=category_filter)

@admin_bp.route('/articles/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_article():
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        tags = request.form.get('tags', '').strip()
        is_published = bool(request.form.get('is_published'))
        is_featured = bool(request.form.get('is_featured'))
        
        # Handle file upload
        pdf_file = request.files.get('pdf_file')
        
        # Validation
        errors = []
        if not title:
            errors.append('Title is required.')
        if not description:
            errors.append('Description is required.')
        if not author:
            errors.append('Author is required.')
        if not category:
            errors.append('Category is required.')
        if not pdf_file:
            errors.append('PDF file is required.')
        
        # Validate PDF file
        if pdf_file:
            is_valid, file_errors = PDFProcessor.validate_pdf_file(pdf_file)
            if not is_valid:
                errors.extend(file_errors)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            categories = Category.query.all()
            return render_template('admin/add_article.html', categories=categories)
        
        try:
            # Save PDF file
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdfs')
            save_result = PDFProcessor.save_uploaded_pdf(pdf_file, upload_folder)
            
            if not save_result['success']:
                flash(f'Error saving file: {save_result["error"]}', 'error')
                return redirect(url_for('admin.add_article'))
            
            # Extract text from PDF
            pdf_path = save_result['filepath']
            extraction_result = PDFProcessor.extract_text_from_pdf(pdf_path)
            
            if not extraction_result['success']:
                flash('Error extracting text from PDF. Article saved without content.', 'warning')
                full_text = ''
                preview_content = description[:500]
                page_count = 0
            else:
                full_text = extraction_result['full_text']
                preview_content = PDFProcessor.generate_preview_content(full_text)
                page_count = extraction_result['page_count']
            
            # Generate embeddings
            title_embedding = EmbeddingService.generate_embedding(title + ' ' + description)
            content_embedding = EmbeddingService.generate_embedding(full_text[:2000]) if full_text else None
            
            # Create article
            article = Article(
                title=title,
                description=description,
                author=author,
                category=category,
                tags=tags,
                pdf_filename=save_result['filename'],
                pdf_path=pdf_path,
                pdf_size=save_result['filesize'],
                full_text_content=full_text,
                preview_content=preview_content,
                page_count=page_count,
                title_embedding=title_embedding,
                content_embedding=content_embedding,
                is_published=is_published,
                is_featured=is_featured,
                created_by=current_user.id,
                published_at=datetime.utcnow() if is_published else None
            )
            
            db.session.add(article)
            db.session.commit()
            
            flash('Article added successfully!', 'success')
            return redirect(url_for('admin.articles'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding article: {str(e)}', 'error')
    
    categories = Category.query.all()
    return render_template('admin/add_article.html', categories=categories)

@admin_bp.route('/articles/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        author = request.form.get('author', '').strip()
        category = request.form.get('category', '').strip()
        tags = request.form.get('tags', '').strip()
        is_published = bool(request.form.get('is_published'))
        is_featured = bool(request.form.get('is_featured'))
        
        # Validation
        if not all([title, description, author, category]):
            flash('All fields are required.', 'error')
            categories = Category.query.all()
            return render_template('admin/edit_article.html', article=article, categories=categories)
        
        try:
            # Update article
            article.title = title
            article.description = description
            article.author = author
            article.category = category
            article.tags = tags
            article.is_featured = is_featured
            article.updated_at = datetime.utcnow()
            
            # Handle publication status change
            if is_published and not article.is_published:
                article.published_at = datetime.utcnow()
            elif not is_published and article.is_published:
                article.published_at = None
            
            article.is_published = is_published
            
            # Update embeddings if title or description changed
            title_embedding = EmbeddingService.generate_embedding(title + ' ' + description)
            article.title_embedding = title_embedding
            
            db.session.commit()
            flash('Article updated successfully!', 'success')
            return redirect(url_for('admin.articles'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating article: {str(e)}', 'error')
    
    categories = Category.query.all()
    return render_template('admin/edit_article.html', article=article, categories=categories)

@admin_bp.route('/articles/<int:article_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    
    try:
        # Delete PDF file
        if os.path.exists(article.pdf_path):
            os.remove(article.pdf_path)
        
        # Delete article from database
        db.session.delete(article)
        db.session.commit()
        
        flash('Article deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting article: {str(e)}', 'error')
    
    return redirect(url_for('admin.articles'))

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', '').strip().lower()
    description = request.form.get('description', '').strip()
    
    if not name or not slug:
        flash('Name and slug are required.', 'error')
        return redirect(url_for('admin.categories'))
    
    # Check if slug already exists
    if Category.query.filter_by(slug=slug).first():
        flash('A category with this slug already exists.', 'error')
        return redirect(url_for('admin.categories'))
    
    try:
        category = Category(name=name, slug=slug, description=description)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding category: {str(e)}', 'error')
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)