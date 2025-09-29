import os
from app import create_app, db
from app.models import User, Article, Category
from flask_migrate import upgrade

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Article': Article, 
        'Category': Category
    }

@app.cli.command()
def deploy():
    """Run deployment tasks."""
    upgrade()

@app.cli.command()
def create_admin():
    """Create admin user"""
    admin = User.query.filter_by(email='tayab.dev1@gmail.com').first()
    
    if admin:
        print('Admin user already exists!')
        return
    
    admin = User(
        email='tayab.dev1@gmail.com',
        first_name='Tayab',
        last_name='Khan',
        is_admin=True,
        is_verified=True,
        subscription_type='premium'
    )
    admin.set_password('tayab123')
    
    db.session.add(admin)
    db.session.commit()
    
    print('✅ Admin user created!')
    print('Email: tayab.dev1@gmail.com')
    print('Password: tayab123')
    print('⚠️ Please change password after first login!')

@app.cli.command()
def init_categories():
    """Create default categories"""
    categories = [
        {'name': 'Technology', 'slug': 'technology'},
        {'name': 'Science', 'slug': 'science'},
        {'name': 'Business', 'slug': 'business'},
        {'name': 'Health', 'slug': 'health'},
        {'name': 'Education', 'slug': 'education'},
        {'name': 'Environment', 'slug': 'environment'},
    ]
    
    for cat_data in categories:
        existing = Category.query.filter_by(slug=cat_data['slug']).first()
        if not existing:
            category = Category(**cat_data)
            db.session.add(category)
    
    db.session.commit()
    print('✅ Categories created!')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)