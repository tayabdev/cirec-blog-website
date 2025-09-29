from sqlalchemy import or_, func, text
from app.models import Article
from app.services.embedding_service import EmbeddingService
from app import db
import re
import logging

logger = logging.getLogger(__name__)

class SearchService:
    
    @staticmethod
    def perform_text_search(query, category_filter=None, page=1, per_page=12):
        """Perform full-text search using PostgreSQL capabilities"""
        try:
            # Clean and prepare search query
            search_terms = re.findall(r'\w+', query.lower())
            if not search_terms:
                return Article.query.filter_by(is_published=True).paginate(
                    page=page, per_page=per_page, error_out=False
                )
            
            # Base query for published articles
            base_query = Article.query.filter_by(is_published=True)
            
            # Apply category filter
            if category_filter:
                base_query = base_query.filter_by(category=category_filter)
            
            # Create search conditions with weighting
            search_conditions = []
            for term in search_terms:
                term_pattern = f'%{term}%'
                search_conditions.append(
                    or_(
                        # Title matches are weighted higher
                        func.lower(Article.title).like(term_pattern),
                        func.lower(Article.description).like(term_pattern),
                        func.lower(Article.tags).like(term_pattern),
                        func.lower(Article.full_text_content).like(term_pattern),
                        func.lower(Article.author).like(term_pattern)
                    )
                )
            
            # Combine all search conditions
            if search_conditions:
                search_query = base_query.filter(or_(*search_conditions))
            else:
                search_query = base_query
            
            # Order by relevance (approximate scoring)
            search_query = search_query.order_by(
                Article.is_featured.desc(),
                Article.view_count.desc(),
                Article.created_at.desc()
            )
            
            return search_query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
        except Exception as e:
            logger.error(f"Text search error: {e}")
            return Article.query.filter_by(is_published=True).paginate(
                page=page, per_page=per_page, error_out=False
            )
    
    @staticmethod
    def perform_semantic_search(query, category_filter=None, page=1, per_page=12):
        """Perform semantic search using AI embeddings"""
        try:
            # Generate embedding for search query
            query_embedding = EmbeddingService.generate_embedding(query)
            if not query_embedding:
                logger.warning("Could not generate embedding, falling back to text search")
                return SearchService.perform_text_search(query, category_filter, page, per_page)
            
            # Base query for published articles with embeddings
            base_query = Article.query.filter_by(is_published=True)
            
            # Apply category filter
            if category_filter:
                base_query = base_query.filter_by(category=category_filter)
            
            # Filter articles that have embeddings
            base_query = base_query.filter(
                or_(
                    Article.title_embedding.isnot(None),
                    Article.content_embedding.isnot(None)
                )
            )
            
            articles = base_query.all()
            
            # Calculate similarities
            articles_with_similarity = []
            for article in articles:
                max_similarity = 0
                
                # Check title embedding similarity
                if article.title_embedding:
                    title_sim = EmbeddingService.calculate_similarity(
                        query_embedding, article.title_embedding
                    )
                    max_similarity = max(max_similarity, title_sim * 1.2)  # Weight title higher
                
                # Check content embedding similarity
                if article.content_embedding:
                    content_sim = EmbeddingService.calculate_similarity(
                        query_embedding, article.content_embedding
                    )
                    max_similarity = max(max_similarity, content_sim)
                
                # Only include articles above similarity threshold
                if max_similarity > 0.3:
                    articles_with_similarity.append({
                        'article': article,
                        'similarity': max_similarity
                    })
            
            # Sort by similarity score
            articles_with_similarity.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Manual pagination
            total = len(articles_with_similarity)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_articles = articles_with_similarity[start:end]
            
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
                
                def iter_pages(self):
                    for num in range(1, self.pages + 1):
                        yield num
            
            return MockPagination(paginated_articles, page, per_page, total)
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return SearchService.perform_text_search(query, category_filter, page, per_page)
    
    @staticmethod
    def perform_hybrid_search(query, category_filter=None, page=1, per_page=12):
        """Combine text and semantic search results"""
        try:
            # Get results from both methods
            text_results = SearchService.perform_text_search(query, category_filter, 1, per_page * 2)
            semantic_results = SearchService.perform_semantic_search(query, category_filter, 1, per_page * 2)
            
            # Combine results with scoring
            combined_articles = {}
            
            # Add text search results
            for i, article in enumerate(text_results.items):
                score = 1.0 - (i * 0.05)  # Decreasing score
                combined_articles[article.id] = {
                    'article': article,
                    'text_score': score,
                    'semantic_score': 0,
                    'combined_score': score * 0.6
                }
            
            # Add semantic search results
            for i, article in enumerate(semantic_results.items):
                score = 1.0 - (i * 0.05)
                if article.id in combined_articles:
                    combined_articles[article.id]['semantic_score'] = score
                    combined_articles[article.id]['combined_score'] = (
                        combined_articles[article.id]['text_score'] * 0.6 + score * 0.4
                    )
                else:
                    combined_articles[article.id] = {
                        'article': article,
                        'text_score': 0,
                        'semantic_score': score,
                        'combined_score': score * 0.4
                    }
            
            # Sort by combined score
            sorted_articles = sorted(
                combined_articles.values(),
                key=lambda x: x['combined_score'],
                reverse=True
            )
            
            # Paginate
            total = len(sorted_articles)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_articles = sorted_articles[start:end]
            
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
                
                def iter_pages(self):
                    for num in range(1, self.pages + 1):
                        yield num
            
            return MockPagination(paginated_articles, page, per_page, total)
            
        except Exception as e:
            logger.error(f"Hybrid search error: {e}")
            return SearchService.perform_text_search(query, category_filter, page, per_page)