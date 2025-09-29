from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import or_, func
from app.models import Article, Category
from app.services.embedding_service import EmbeddingService
from app import db
import re

search_bp = Blueprint('search', __name__)

@search_bp.route('/')
def search():
    query = request.args.get('q', '').strip()
    category_filter = request.args.get('category')
    search_type = request.args.get('type', 'hybrid')  # text, semantic, hybrid
    page = request.args.get('page', 1, type=int)
    
    articles = None
    categories = Category.query.filter_by(is_active=True).all()
    
    if query:
        if search_type == 'semantic':
            articles = perform_semantic_search(query, category_filter, page)
        elif search_type == 'text':
            articles = perform_text_search(query, category_filter, page)
        else:  # hybrid
            articles = perform_hybrid_search(query, category_filter, page)
    
    return render_template('search/results.html',
                         query=query,
                         articles=articles,
                         categories=categories,
                         current_category=category_filter,
                         search_type=search_type)

def perform_text_search(query, category_filter=None, page=1):
    """Perform text-based search using PostgreSQL full-text search"""
    # Clean and prepare search query
    search_terms = re.findall(r'\w+', query.lower())
    if not search_terms:
        return None
    
    # Base query for published articles
    base_query = Article.query.filter_by(is_published=True)
    
    # Apply category filter
    if category_filter:
        base_query = base_query.filter_by(category=category_filter)
    
    # Create search conditions
    search_conditions = []
    for term in search_terms:
        term_pattern = f'%{term}%'
        search_conditions.append(
            or_(
                Article.title.ilike(term_pattern),
                Article.description.ilike(term_pattern),
                Article.tags.ilike(term_pattern),
                Article.full_text_content.ilike(term_pattern),
                Article.author.ilike(term_pattern)
            )
        )
    
    # Combine all search conditions
    if search_conditions:
        search_query = base_query.filter(or_(*search_conditions))
    else:
        search_query = base_query
    
    # Order by relevance (approximate)
    search_query = search_query.order_by(
        Article.is_featured.desc(),
        Article.view_count.desc(),
        Article.created_at.desc()
    )
    
    # Paginate results
    return search_query.paginate(
        page=page, per_page=12, error_out=False
    )

def perform_semantic_search(query, category_filter=None, page=1):
    """Perform semantic search using embeddings"""
    try:
        # Generate embedding for search query
        query_embedding = EmbeddingService.generate_embedding(query)
        if not query_embedding:
            return perform_text_search(query, category_filter, page)
        
        # Base query for published articles
        base_query = Article.query.filter_by(is_published=True)
        
        # Apply category filter
        if category_filter:
            base_query = base_query.filter_by(category=category_filter)
        
        # Filter articles that have embeddings
        base_query = base_query.filter(Article.title_embedding.isnot(None))
        
        # Get articles and calculate similarity
        articles_with_similarity = []
        articles = base_query.all()
        
        for article in articles:
            # Calculate similarity with title embedding
            title_similarity = 0
            if article.title_embedding:
                title_similarity = EmbeddingService.calculate_similarity(
                    query_embedding, article.title_embedding
                )
            
            # Calculate similarity with content embedding
            content_similarity = 0
            if article.content_embedding:
                content_similarity = EmbeddingService.calculate_similarity(
                    query_embedding, article.content_embedding
                )
            
            # Combined similarity score (weighted)
            combined_similarity = (title_similarity * 0.7) + (content_similarity * 0.3)
            
            if combined_similarity > 0.3:  # Threshold for relevance
                articles_with_similarity.append({
                    'article': article,
                    'similarity': combined_similarity
                })
        
        # Sort by similarity
        articles_with_similarity.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Paginate manually
        per_page = 12
        start = (page - 1) * per_page
        end = start + per_page
        
        paginated_articles = articles_with_similarity[start:end]
        total = len(articles_with_similarity)
        
        # Create a mock pagination object
        class MockPagination:
            def __init__(self, items, page, per_page, total):
                self.items = [item['article'] for item in items]
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = (total + per_page - 1) // per_page
                self.prev_num = page - 1 if page > 1 else None
                self.next_num = page + 1 if page < self.pages else None
                self.has_prev = page > 1
                self.has_next = page < self.pages
        
        return MockPagination(paginated_articles, page, per_page, total)
    
    except Exception as e:
        # Fallback to text search if semantic search fails
        return perform_text_search(query, category_filter, page)

def perform_hybrid_search(query, category_filter=None, page=1):
    """Perform hybrid search combining text and semantic search"""
    try:
        # Get results from both search methods
        text_results = perform_text_search(query, category_filter, 1)
        semantic_results = perform_semantic_search(query, category_filter, 1)
        
        if not text_results and not semantic_results:
            return None
        
        # Combine and deduplicate results
        combined_articles = {}
        
        # Add text search results with score
        if text_results:
            for i, article in enumerate(text_results.items):
                score = 1.0 - (i * 0.1)  # Decreasing score based on position
                combined_articles[article.id] = {
                    'article': article,
                    'text_score': score,
                    'semantic_score': 0
                }
        
        # Add semantic search results with score
        if semantic_results:
            for i, article in enumerate(semantic_results.items):
                score = 1.0 - (i * 0.1)
                if article.id in combined_articles:
                    combined_articles[article.id]['semantic_score'] = score
                else:
                    combined_articles[article.id] = {
                        'article': article,
                        'text_score': 0,
                        'semantic_score': score
                    }
        
        # Calculate combined scores and sort
        for article_data in combined_articles.values():
            article_data['combined_score'] = (
                article_data['text_score'] * 0.6 + 
                article_data['semantic_score'] * 0.4
            )
        
        sorted_articles = sorted(
            combined_articles.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )
        
        # Paginate results
        per_page = 12
        start = (page - 1) * per_page
        end = start + per_page
        
        paginated_articles = sorted_articles[start:end]
        total = len(sorted_articles)
        
        # Create mock pagination object
        class MockPagination:
            def __init__(self, items, page, per_page, total):
                self.items = [item['article'] for item in items]
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = (total + per_page - 1) // per_page
                self.prev_num = page - 1 if page > 1 else None
                self.next_num = page + 1 if page < self.pages else None
                self.has_prev = page > 1
                self.has_next = page < self.pages
        
        return MockPagination(paginated_articles, page, per_page, total)
    
    except Exception as e:
        # Fallback to text search
        return perform_text_search(query, category_filter, page)

@search_bp.route('/api/suggestions')
def api_search_suggestions():
    """API endpoint for search suggestions"""
    query = request.args.get('q', '').strip().lower()
    limit = request.args.get('limit', 5, type=int)
    
    if len(query) < 2:
        return jsonify([])
    
    # Search in titles and tags
    suggestions = []
    
    # Title suggestions
    title_matches = Article.query.filter(
        Article.is_published == True,
        Article.title.ilike(f'%{query}%')
    ).limit(limit).all()
    
    for article in title_matches:
        suggestions.append({
            'type': 'article',
            'text': article.title,
            'url': f'/articles/{article.uuid}'
        })
    
    # Category suggestions
    if len(suggestions) < limit:
        category_matches = Category.query.filter(
            Category.is_active == True,
            Category.name.ilike(f'%{query}%')
        ).limit(limit - len(suggestions)).all()
        
        for category in category_matches:
            suggestions.append({
                'type': 'category',
                'text': category.name,
                'url': f'/articles/category/{category.slug}'
            })
    
    return jsonify(suggestions)

@search_bp.route('/api/autocomplete')
def api_autocomplete():
    """API endpoint for search autocomplete"""
    query = request.args.get('q', '').strip().lower()
    
    if len(query) < 2:
        return jsonify([])
    
    # Get unique search terms from articles
    terms = set()
    
    # Extract terms from titles
    articles = Article.query.filter(
        Article.is_published == True,
        Article.title.ilike(f'%{query}%')
    ).limit(10).all()
    
    for article in articles:
        words = re.findall(r'\w+', article.title.lower())
        for word in words:
            if word.startswith(query) and len(word) > 2:
                terms.add(word)
    
    # Extract terms from tags
    tag_articles = Article.query.filter(
        Article.is_published == True,
        Article.tags.ilike(f'%{query}%')
    ).limit(10).all()
    
    for article in tag_articles:
        if article.tags:
            tag_words = re.findall(r'\w+', article.tags.lower())
            for word in tag_words:
                if word.startswith(query) and len(word) > 2:
                    terms.add(word)
    
    return jsonify(sorted(list(terms))[:10])

@search_bp.route('/api/advanced')
def api_advanced_search():
    """API endpoint for advanced search with filters"""
    query = request.args.get('q', '').strip()
    author = request.args.get('author', '').strip()
    category = request.args.get('category', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    sort_by = request.args.get('sort', 'relevance')
    page = request.args.get('page', 1, type=int)
    
    # Base query
    search_query = Article.query.filter_by(is_published=True)
    
    # Apply filters
    if query:
        search_conditions = []
        search_terms = re.findall(r'\w+', query.lower())
        for term in search_terms:
            term_pattern = f'%{term}%'
            search_conditions.append(
                or_(
                    Article.title.ilike(term_pattern),
                    Article.description.ilike(term_pattern),
                    Article.full_text_content.ilike(term_pattern)
                )
            )
        if search_conditions:
            search_query = search_query.filter(or_(*search_conditions))
    
    if author:
        search_query = search_query.filter(Article.author.ilike(f'%{author}%'))
    
    if category:
        search_query = search_query.filter_by(category=category)
    
    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            search_query = search_query.filter(Article.created_at >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            search_query = search_query.filter(Article.created_at <= date_to_obj)
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'date_desc':
        search_query = search_query.order_by(Article.created_at.desc())
    elif sort_by == 'date_asc':
        search_query = search_query.order_by(Article.created_at.asc())
    elif sort_by == 'popular':
        search_query = search_query.order_by(Article.view_count.desc())
    elif sort_by == 'title':
        search_query = search_query.order_by(Article.title.asc())
    else:  # relevance
        search_query = search_query.order_by(
            Article.is_featured.desc(),
            Article.view_count.desc(),
            Article.created_at.desc()
        )
    
    # Paginate
    articles = search_query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Return JSON response
    return jsonify({
        'articles': [article.to_dict() for article in articles.items],
        'pagination': {
            'page': articles.page,
            'pages': articles.pages,
            'per_page': articles.per_page,
            'total': articles.total,
            'has_prev': articles.has_prev,
            'has_next': articles.has_next
        }
    })