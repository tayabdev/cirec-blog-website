from celery import Celery
from app.services.pdf_processor import PDFProcessor
from app.services.embedding_service import EmbeddingService
from app.models import Article
from app import db
import logging

logger = logging.getLogger(__name__)

# Initialize Celery (for production use)
# For development, we'll use direct execution
USE_CELERY = False

if USE_CELERY:
    celery = Celery('cirec_blog')
    celery.config_from_object('app.config')

def process_article_async(article_id):
    """Process article PDF and generate embeddings"""
    if USE_CELERY:
        return _process_article_task.delay(article_id)
    else:
        return _process_article_task(article_id)

def _process_article_task(article_id):
    """Background task to process article PDF and generate embeddings"""
    try:
        # Get article from database
        from app import create_app
        app = create_app()
        
        with app.app_context():
            article = Article.query.get(article_id)
            if not article:
                logger.error(f"Article {article_id} not found")
                return False
            
            logger.info(f"Processing article: {article.title}")
            
            # Extract text from PDF if not already done
            if not article.full_text_content:
                extraction_result = PDFProcessor.extract_text_from_pdf(article.pdf_path)
                
                if extraction_result['success']:
                    article.full_text_content = extraction_result['full_text']
                    article.page_count = extraction_result['page_count']
                    
                    # Update preview content
                    article.preview_content = PDFProcessor.generate_preview_content(
                        extraction_result['full_text']
                    )
                else:
                    logger.error(f"Failed to extract text from {article.pdf_path}")
            
            # Generate embeddings if not already done
            if not article.title_embedding:
                title_text = f"{article.title} {article.description}"
                article.title_embedding = EmbeddingService.generate_embedding(title_text)
                logger.info(f"Generated title embedding for article {article_id}")
            
            if not article.content_embedding and article.full_text_content:
                # Use first 2000 characters for content embedding
                content_sample = article.full_text_content[:2000]
                article.content_embedding = EmbeddingService.generate_embedding(content_sample)
                logger.info(f"Generated content embedding for article {article_id}")
            
            # Save changes
            db.session.commit()
            logger.info(f"Successfully processed article {article_id}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error processing article {article_id}: {str(e)}")
        db.session.rollback()
        return False

def reprocess_all_embeddings():
    """Reprocess embeddings for all articles (maintenance task)"""
    from app import create_app
    app = create_app()
    
    with app.app_context():
        articles = Article.query.filter_by(is_published=True).all()
        
        success_count = 0
        total_count = len(articles)
        
        for article in articles:
            try:
                # Regenerate embeddings
                title_text = f"{article.title} {article.description}"
                article.title_embedding = EmbeddingService.generate_embedding(title_text)
                
                if article.full_text_content:
                    content_sample = article.full_text_content[:2000]
                    article.content_embedding = EmbeddingService.generate_embedding(content_sample)
                
                db.session.commit()
                success_count += 1
                logger.info(f"Reprocessed embeddings for article {article.id}")
                
            except Exception as e:
                logger.error(f"Failed to reprocess article {article.id}: {str(e)}")
                db.session.rollback()
        
        logger.info(f"Reprocessing complete: {success_count}/{total_count} articles processed")
        return success_count, total_count

# Celery task decorators (if using Celery)
if USE_CELERY:
    _process_article_task = celery.task(_process_article_task)