from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector  # Re-enabled
from app import db
import uuid

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    tags = db.Column(db.Text)  # Comma-separated tags
    
    # PDF and content
    pdf_filename = db.Column(db.String(255), nullable=False)
    pdf_path = db.Column(db.String(500), nullable=False)
    pdf_size = db.Column(db.Integer)  # File size in bytes
    
    # Extracted content
    full_text_content = db.Column(db.Text)
    preview_content = db.Column(db.Text, nullable=False)  # First few paragraphs
    page_count = db.Column(db.Integer)
    
    # ML embeddings for semantic search - Re-enabled
    title_embedding = db.Column(Vector(384))
    content_embedding = db.Column(Vector(384))
    
    # Status and metadata
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Foreign keys
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('articles', lazy=True))
    
    def __repr__(self):
        return f'<Article {self.title}>'
    
    @property
    def tag_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    @tag_list.setter
    def tag_list(self, tags):
        self.tags = ', '.join(tags)
    
    def increment_view_count(self):
        self.view_count = (self.view_count or 0) + 1
        db.session.commit()
    
    def increment_download_count(self):
        self.download_count = (self.download_count or 0) + 1
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'title': self.title,
            'description': self.description,
            'author': self.author,
            'category': self.category,
            'tags': self.tag_list,
            'preview_content': self.preview_content,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    article_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Category {self.name}>'