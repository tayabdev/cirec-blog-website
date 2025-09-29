from sentence_transformers import SentenceTransformer
import numpy as np
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    _model = None
    
    @classmethod
    def get_model(cls):
        """Lazy loading of the sentence transformer model"""
        if cls._model is None:
            model_name = current_app.config.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            try:
                logger.info(f"Loading embedding model: {model_name}")
                cls._model = SentenceTransformer(model_name)
                logger.info(f"Successfully loaded embedding model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                return None
        return cls._model
    
    @classmethod
    def generate_embedding(cls, text):
        """Generate embedding for a single text"""
        try:
            if not text or not text.strip():
                return None
            
            model = cls.get_model()
            if not model:
                logger.warning("Model not available, skipping embedding generation")
                return None
                
            # Clean and truncate text if too long
            cleaned_text = cls.preprocess_text(text)
            embedding = model.encode(cleaned_text)
            
            # Convert to list for JSON serialization
            return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    @classmethod
    def generate_embeddings_batch(cls, texts):
        """Generate embeddings for multiple texts"""
        try:
            if not texts:
                return []
            
            model = cls.get_model()
            if not model:
                return [None] * len(texts)
                
            cleaned_texts = [cls.preprocess_text(text) for text in texts]
            embeddings = model.encode(cleaned_texts)
            
            # Convert to list of lists
            return [embedding.tolist() for embedding in embeddings]
        
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(texts) if texts else []
    
    @classmethod
    def preprocess_text(cls, text, max_length=512):
        """Preprocess text before embedding generation"""
        if not text:
            return ""
        
        # Remove extra whitespaces
        text = ' '.join(text.split())
        
        # Truncate if too long (most models have token limits)
        if len(text.split()) > max_length:
            text = ' '.join(text.split()[:max_length])
        
        return text
    
    @classmethod
    def calculate_similarity(cls, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings"""
        try:
            if not embedding1 or not embedding2:
                return 0.0
            
            # Convert to numpy arrays
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm_a = np.linalg.norm(emb1)
            norm_b = np.linalg.norm(emb2)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
        
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    @classmethod
    def find_similar_articles(cls, query_embedding, article_embeddings, threshold=0.5, limit=10):
        """Find articles similar to query based on embeddings"""
        try:
            if not query_embedding or not article_embeddings:
                return []
            
            similarities = []
            
            for article_id, article_embedding in article_embeddings:
                if not article_embedding:
                    continue
                
                similarity = cls.calculate_similarity(query_embedding, article_embedding)
                
                if similarity >= threshold:
                    similarities.append({
                        'article_id': article_id,
                        'similarity': similarity
                    })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top results
            return similarities[:limit]
        
        except Exception as e:
            logger.error(f"Error finding similar articles: {e}")
            return []