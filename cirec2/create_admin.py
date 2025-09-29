#!/usr/bin/env python3
"""
Script to create admin user for CIREC blog
"""

from app import create_app, db
from app.models import User, Category

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='tayab.dev1@gmail.com').first()
        
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin = User(
            email='tayab.dev1@gmail.com',
            first_name='Tayab',
            last_name='Khan',
            is_admin=True,
            is_verified=True,
            subscription_type='premium'
        )
        admin.set_password('tayab123')  # Change this password!
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print(f"Email: tayab.dev1@gmail.com")
        print(f"Password: tayab123")
        print("⚠️  Please change this password after first login!")

def create_default_categories():
    app = create_app()
    
    with app.app_context():
        categories = [
            {'name': 'Technology', 'slug': 'technology', 'description': 'Latest technology trends and innovations'},
            {'name': 'Science', 'slug': 'science', 'description': 'Scientific research and discoveries'},
            {'name': 'Business', 'slug': 'business', 'description': 'Business insights and market analysis'},
            {'name': 'Health', 'slug': 'health', 'description': 'Health and wellness research'},
            {'name': 'Education', 'slug': 'education', 'description': 'Educational resources and research'},
            {'name': 'Environment', 'slug': 'environment', 'description': 'Environmental studies and sustainability'},
        ]
        
        for cat_data in categories:
            existing = Category.query.filter_by(slug=cat_data['slug']).first()
            if not existing:
                category = Category(**cat_data)
                db.session.add(category)
        
        db.session.commit()
        print("✅ Default categories created successfully!")

if __name__ == '__main__':
    create_admin_user()
    create_default_categories()