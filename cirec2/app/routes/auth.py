# Option 1: Auto-upgrade new users to premium
# Update app/routes/auth.py registration:

# from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
# from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.urls import url_parse
# from app import db
# from app.models import User
# from app.utils.validators import validate_email, validate_password
# import re
# from datetime import datetime

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
    
#     if request.method == 'POST':
#         email = request.form.get('email', '').strip().lower()
#         password = request.form.get('password', '')
#         remember_me = bool(request.form.get('remember_me'))
        
#         # Validation
#         if not email or not password:
#             flash('Please fill in all fields.', 'error')
#             return render_template('auth/login.html')
        
#         if not validate_email(email):
#             flash('Please enter a valid email address.', 'error')
#             return render_template('auth/login.html')
        
#         # Find user
#         user = User.query.filter_by(email=email).first()
        
#         if user and user.check_password(password):
#             if not user.is_active:
#                 flash('Your account has been deactivated. Please contact support.', 'error')
#                 return render_template('auth/login.html')
            
#             # Update last login
#             user.last_login = datetime.utcnow()
#             db.session.commit()
            
#             login_user(user, remember=remember_me)
            
#             # Redirect to next page or dashboard
#             next_page = request.args.get('next')
#             if not next_page or url_parse(next_page).netloc != '':
#                 next_page = url_for('main.index')
            
#             flash(f'Welcome back, {user.first_name}!', 'success')
#             return redirect(next_page)
        
#         else:
#             flash('Invalid email or password.', 'error')
    
#     return render_template('auth/login.html')

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
    
#     if request.method == 'POST':
#         # Get form data
#         email = request.form.get('email', '').strip().lower()
#         password = request.form.get('password', '')
#         confirm_password = request.form.get('confirm_password', '')
#         first_name = request.form.get('first_name', '').strip()
#         last_name = request.form.get('last_name', '').strip()
        
#         # Validation
#         errors = []
        
#         if not all([email, password, confirm_password, first_name, last_name]):
#             errors.append('Please fill in all fields.')
        
#         if not validate_email(email):
#             errors.append('Please enter a valid email address.')
        
#         if not validate_password(password):
#             errors.append('Password must be at least 8 characters long and contain letters and numbers.')
        
#         if password != confirm_password:
#             errors.append('Passwords do not match.')
        
#         if len(first_name) < 2 or len(last_name) < 2:
#             errors.append('First name and last name must be at least 2 characters long.')
        
#         # Check if email already exists
#         if User.query.filter_by(email=email).first():
#             errors.append('An account with this email already exists.')
        
#         if errors:
#             for error in errors:
#                 flash(error, 'error')
#             return render_template('auth/register.html')
        
#         # Create new user
#         try:
#             user = User(
#                 email=email,
#                 first_name=first_name,
#                 last_name=last_name,
#                 is_verified=True,  # Auto-verify for now
#                 subscription_type='premium'  # Give new users premium access
#             )
#             user.set_password(password)
            
#             db.session.add(user)
#             db.session.commit()
            
#             flash('Registration successful! You can now log in.', 'success')
#             return redirect(url_for('auth.login'))
        
#         except Exception as e:
#             db.session.rollback()
#             flash('An error occurred during registration. Please try again.', 'error')
    
#     return render_template('auth/register.html')

# @auth_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out successfully.', 'info')
#     return redirect(url_for('main.index'))

# @auth_bp.route('/profile')
# @login_required
# def profile():
#     return render_template('auth/profile.html')

# @auth_bp.route('/profile/update', methods=['POST'])
# @login_required
# def update_profile():
#     first_name = request.form.get('first_name', '').strip()
#     last_name = request.form.get('last_name', '').strip()
    
#     if not first_name or not last_name:
#         flash('First name and last name are required.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     try:
#         current_user.first_name = first_name
#         current_user.last_name = last_name
#         current_user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         flash('Profile updated successfully!', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash('An error occurred while updating your profile.', 'error')
    
#     return redirect(url_for('auth.profile'))

# @auth_bp.route('/change-password', methods=['POST'])
# @login_required
# def change_password():
#     current_password = request.form.get('current_password', '')
#     new_password = request.form.get('new_password', '')
#     confirm_password = request.form.get('confirm_password', '')
    
#     # Validation
#     if not all([current_password, new_password, confirm_password]):
#         flash('Please fill in all password fields.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     if not current_user.check_password(current_password):
#         flash('Current password is incorrect.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     if not validate_password(new_password):
#         flash('New password must be at least 8 characters long and contain letters and numbers.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     if new_password != confirm_password:
#         flash('New passwords do not match.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     try:
#         current_user.set_password(new_password)
#         current_user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         flash('Password changed successfully!', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash('An error occurred while changing your password.', 'error')
    
#     return redirect(url_for('auth.profile'))

# @auth_bp.route('/api/check-email', methods=['POST'])
# def api_check_email():
#     """API endpoint to check if email is available"""
#     email = request.json.get('email', '').strip().lower()
    
#     if not validate_email(email):
#         return jsonify({'available': False, 'message': 'Invalid email format'})
    
#     user_exists = User.query.filter_by(email=email).first() is not None
    
#     return jsonify({
#         'available': not user_exists,
#         'message': 'Email already registered' if user_exists else 'Email available'
#     })



# from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
# from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.urls import url_parse
# from app import db
# from app.models import User
# from app.utils.validators import validate_email, validate_password
# import re
# from datetime import datetime

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
    
#     if request.method == 'POST':
#         email = request.form.get('email', '').strip().lower()
#         password = request.form.get('password', '')
#         remember_me = bool(request.form.get('remember_me'))
        
#         # Validation
#         if not email or not password:
#             flash('Please fill in all fields.', 'error')
#             return render_template('auth/login.html')
        
#         if not validate_email(email):
#             flash('Please enter a valid email address.', 'error')
#             return render_template('auth/login.html')
        
#         # Find user
#         user = User.query.filter_by(email=email).first()
        
#         if user and user.check_password(password):
#             if not user.is_active:
#                 flash('Your account has been deactivated. Please contact support.', 'error')
#                 return render_template('auth/login.html')
            
#             # Update last login
#             user.last_login = datetime.utcnow()
#             db.session.commit()
            
#             login_user(user, remember=remember_me)
            
#             # Redirect to next page or dashboard
#             next_page = request.args.get('next')
#             if not next_page or url_parse(next_page).netloc != '':
#                 next_page = url_for('main.index')
            
#             flash(f'Welcome back, {user.first_name}!', 'success')
#             return redirect(next_page)
        
#         else:
#             flash('Invalid email or password.', 'error')
    
#     return render_template('auth/login.html')

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
    
#     if request.method == 'POST':
#         # Get form data
#         email = request.form.get('email', '').strip().lower()
#         password = request.form.get('password', '')
#         confirm_password = request.form.get('confirm_password', '')
#         first_name = request.form.get('first_name', '').strip()
#         last_name = request.form.get('last_name', '').strip()
        
#         # Validation
#         errors = []
        
#         if not all([email, password, confirm_password, first_name, last_name]):
#             errors.append('Please fill in all fields.')
        
#         if not validate_email(email):
#             errors.append('Please enter a valid email address.')
        
#         if not validate_password(password):
#             errors.append('Password must be at least 8 characters long and contain letters and numbers.')
        
#         if password != confirm_password:
#             errors.append('Passwords do not match.')
        
#         if len(first_name) < 2 or len(last_name) < 2:
#             errors.append('First name and last name must be at least 2 characters long.')
        
#         # Check if email already exists
#         if User.query.filter_by(email=email).first():
#             errors.append('An account with this email already exists.')
        
#         if errors:
#             for error in errors:
#                 flash(error, 'error')
#             return render_template('auth/register.html')
        
#         # Create new user
#         try:
#             user = User(
#                 email=email,
#                 first_name=first_name,
#                 last_name=last_name,
#                 is_verified=True  # Auto-verify for now, implement email verification later
#             )
#             user.set_password(password)
            
#             db.session.add(user)
#             db.session.commit()
            
#             flash('Registration successful! You can now log in.', 'success')
#             return redirect(url_for('auth.login'))
        
#         except Exception as e:
#             db.session.rollback()
#             flash('An error occurred during registration. Please try again.', 'error')
    
#     return render_template('auth/register.html')

# @auth_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out successfully.', 'info')
#     return redirect(url_for('main.index'))

# @auth_bp.route('/profile')
# @login_required
# def profile():
#     return render_template('auth/profile.html')

# @auth_bp.route('/profile/update', methods=['POST'])
# @login_required
# def update_profile():
#     first_name = request.form.get('first_name', '').strip()
#     last_name = request.form.get('last_name', '').strip()
    
#     if not first_name or not last_name:
#         flash('First name and last name are required.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     try:
#         current_user.first_name = first_name
#         current_user.last_name = last_name
#         current_user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         flash('Profile updated successfully!', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash('An error occurred while updating your profile.', 'error')
    
#     return redirect(url_for('auth.profile'))

# @auth_bp.route('/change-password', methods=['POST'])
# @login_required
# def change_password():
#     current_password = request.form.get('current_password', '')
#     new_password = request.form.get('new_password', '')
#     confirm_password = request.form.get('confirm_password', '')
    
#     # Validation
#     if not all([current_password, new_password, confirm_password]):
#         flash('Please fill in all password fields.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     if not current_user.check_password(current_password):
#         flash('Current password is incorrect.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     if not validate_password(new_password):
#         flash('New password must be at least 8 characters long and contain letters and numbers.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     if new_password != confirm_password:
#         flash('New passwords do not match.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     try:
#         current_user.set_password(new_password)
#         current_user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         flash('Password changed successfully!', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash('An error occurred while changing your password.', 'error')
    
#     return redirect(url_for('auth.profile'))

# @auth_bp.route('/api/check-email', methods=['POST'])
# def api_check_email():
#     """API endpoint to check if email is available"""
#     email = request.json.get('email', '').strip().lower()
    
#     if not validate_email(email):
#         return jsonify({'available': False, 'message': 'Invalid email format'})
    
#     user_exists = User.query.filter_by(email=email).first() is not None
    
#     return jsonify({
#         'available': not user_exists,
#         'message': 'Email already registered' if user_exists else 'Email available'
#     })



# Option 1: Auto-upgrade new users to premium
# Update app/routes/auth.py registration:

# from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
# from flask_login import login_user, logout_user, login_required, current_user
# from werkzeug.urls import url_parse
# from app import db
# from app.models import User
# from app.utils.validators import validate_email, validate_password
# import re
# from datetime import datetime

# auth_bp = Blueprint('auth', __name__)

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
    
#     if request.method == 'POST':
#         email = request.form.get('email', '').strip().lower()
#         password = request.form.get('password', '')
#         remember_me = bool(request.form.get('remember_me'))
        
#         # Validation
#         if not email or not password:
#             flash('Please fill in all fields.', 'error')
#             return render_template('auth/login.html')
        
#         if not validate_email(email):
#             flash('Please enter a valid email address.', 'error')
#             return render_template('auth/login.html')
        
#         # Find user
#         user = User.query.filter_by(email=email).first()
        
#         if user and user.check_password(password):
#             if not user.is_active:
#                 flash('Your account has been deactivated. Please contact support.', 'error')
#                 return render_template('auth/login.html')
            
#             # Update last login
#             user.last_login = datetime.utcnow()
#             db.session.commit()
            
#             login_user(user, remember=remember_me)
            
#             # Redirect to next page or dashboard
#             next_page = request.args.get('next')
#             if not next_page or url_parse(next_page).netloc != '':
#                 next_page = url_for('main.index')
            
#             flash(f'Welcome back, {user.first_name}!', 'success')
#             return redirect(next_page)
        
#         else:
#             flash('Invalid email or password.', 'error')
    
#     return render_template('auth/login.html')

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
    
#     if request.method == 'POST':
#         # Get form data
#         email = request.form.get('email', '').strip().lower()
#         password = request.form.get('password', '')
#         confirm_password = request.form.get('confirm_password', '')
#         first_name = request.form.get('first_name', '').strip()
#         last_name = request.form.get('last_name', '').strip()
        
#         # Validation
#         errors = []
        
#         if not all([email, password, confirm_password, first_name, last_name]):
#             errors.append('Please fill in all fields.')
        
#         if not validate_email(email):
#             errors.append('Please enter a valid email address.')
        
#         if not validate_password(password):
#             errors.append('Password must be at least 8 characters long and contain letters and numbers.')
        
#         if password != confirm_password:
#             errors.append('Passwords do not match.')
        
#         if len(first_name) < 2 or len(last_name) < 2:
#             errors.append('First name and last name must be at least 2 characters long.')
        
#         # Check if email already exists
#         if User.query.filter_by(email=email).first():
#             errors.append('An account with this email already exists.')
        
#         if errors:
#             for error in errors:
#                 flash(error, 'error')
#             return render_template('auth/register.html')
        
#         # Create new user
#         try:
#             user = User(
#                 email=email,
#                 first_name=first_name,
#                 last_name=last_name,
#                 is_verified=True,  # Auto-verify for now
#                 subscription_type='premium'  # Give new users premium access
#             )
#             user.set_password(password)
            
#             db.session.add(user)
#             db.session.commit()
            
#             flash('Registration successful! You can now log in.', 'success')
#             return redirect(url_for('auth.login'))
        
#         except Exception as e:
#             db.session.rollback()
#             flash('An error occurred during registration. Please try again.', 'error')
    
#     return render_template('auth/register.html')

# @auth_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out successfully.', 'info')
#     return redirect(url_for('main.index'))

# @auth_bp.route('/profile')
# @login_required
# def profile():
#     return render_template('auth/profile.html')

# @auth_bp.route('/profile/update', methods=['POST'])
# @login_required
# def update_profile():
#     first_name = request.form.get('first_name', '').strip()
#     last_name = request.form.get('last_name', '').strip()
    
#     if not first_name or not last_name:
#         flash('First name and last name are required.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     try:
#         current_user.first_name = first_name
#         current_user.last_name = last_name
#         current_user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         flash('Profile updated successfully!', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash('An error occurred while updating your profile.', 'error')
    
#     return redirect(url_for('auth.profile'))

# @auth_bp.route('/change-password', methods=['POST'])
# @login_required
# def change_password():
#     current_password = request.form.get('current_password', '')
#     new_password = request.form.get('new_password', '')
#     confirm_password = request.form.get('confirm_password', '')
    
#     # Validation
#     if not all([current_password, new_password, confirm_password]):
#         flash('Please fill in all password fields.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     if not current_user.check_password(current_password):
#         flash('Current password is incorrect.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     if not validate_password(new_password):
#         flash('New password must be at least 8 characters long and contain letters and numbers.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     if new_password != confirm_password:
#         flash('New passwords do not match.', 'error')
#         return redirect(url_for('auth.profile'))
    
#     try:
#         current_user.set_password(new_password)
#         current_user.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         flash('Password changed successfully!', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash('An error occurred while changing your password.', 'error')
    
#     return redirect(url_for('auth.profile'))

# @auth_bp.route('/api/check-email', methods=['POST'])
# def api_check_email():
#     """API endpoint to check if email is available"""
#     email = request.json.get('email', '').strip().lower()
    
#     if not validate_email(email):
#         return jsonify({'available': False, 'message': 'Invalid email format'})
    
#     user_exists = User.query.filter_by(email=email).first() is not None
    
#     return jsonify({
#         'available': not user_exists,
#         'message': 'Email already registered' if user_exists else 'Email available'
#     })






# Option 2: Update existing user's subscription
# For the user you just created, upgrade them in the Flask shell:
# bashflask shell
# pythonfrom app.models import User
# from app import db

# # Find the user (replace with actual email)
# user = User.query.filter_by(email='[email of new user]').first()
# if user:
#     user.subscription_type = 'premium'
#     db.session.commit()
#     print(f"Updated {user.email} to premium")
# else:
#     print("User not found")




# Option 3: Change the access logic
# Or modify the access logic in app/routes/articles.py to allow all verified users:


# from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file, abort
# from flask_login import login_required, current_user
# from app.models import Article, Category
# from app import db
# import os
# import uuid

# articles_bp = Blueprint('articles', __name__)

# @articles_bp.route('/')
# def list_articles():
#     page = request.args.get('page', 1, type=int)
#     category_filter = request.args.get('category')
#     sort_by = request.args.get('sort', 'latest')  # latest, popular, featured
    
#     # Base query for published articles
#     query = Article.query.filter_by(is_published=True)
    
#     # Apply category filter
#     if category_filter:
#         query = query.filter_by(category=category_filter)
    
#     # Apply sorting
#     if sort_by == 'popular':
#         query = query.order_by(Article.view_count.desc())
#     elif sort_by == 'featured':
#         query = query.filter_by(is_featured=True).order_by(Article.created_at.desc())
#     else:  # latest
#         query = query.order_by(Article.created_at.desc())
    
#     # Paginate results
#     articles = query.paginate(
#         page=page, per_page=12, error_out=False
#     )
    
#     # Get all categories for filter dropdown
#     categories = Category.query.filter_by(is_active=True).all()
    
#     return render_template('articles/list.html',
#                          articles=articles,
#                          categories=categories,
#                          current_category=category_filter,
#                          current_sort=sort_by)

# @articles_bp.route('/debug/<article_uuid>')
# def debug_article(article_uuid):
#     """Debug route to check article existence"""
#     try:
#         article = Article.query.filter_by(uuid=article_uuid).first()
#         if article:
#             return f"""
#             <h3>Article Found!</h3>
#             <p>Title: {article.title}</p>
#             <p>Published: {article.is_published}</p>
#             <p>UUID: {article.uuid}</p>
#             <p>Created: {article.created_at}</p>
#             <a href="/articles/{article.uuid}">View Article</a>
#             """
#         else:
#             all_articles = Article.query.all()
#             return f"""
#             <h3>Article Not Found</h3>
#             <p>Looking for UUID: {article_uuid}</p>
#             <h4>All Articles:</h4>
#             {''.join([f'<p>{a.title} - {a.uuid} - Published: {a.is_published}</p>' for a in all_articles])}
#             """
#     except Exception as e:
#         return f"Error: {str(e)}"

# @articles_bp.route('/<uuid:article_uuid>')
# def view_article(article_uuid):
#     # Convert string to UUID if needed
#     if isinstance(article_uuid, str):
#         try:
#             article_uuid = uuid.UUID(article_uuid)
#         except ValueError:
#             abort(404)
    
#     article = Article.query.filter_by(uuid=article_uuid, is_published=True).first_or_404()
    
#     # Increment view count
#     article.increment_view_count()
    
#     # Check if user can access full content
#     can_access_full = False
#     if current_user.is_authenticated:
#         can_access_full = current_user.is_verified or current_user.is_admin  # Allow all verified users
    
#     # Get related articles (same category, excluding current)
#     related_articles = Article.query.filter(
#         Article.category == article.category,
#         Article.id != article.id,
#         Article.is_published == True
#     ).order_by(Article.view_count.desc()).limit(4).all()
    
#     return render_template('articles/detail.html',
#                          article=article,
#                          can_access_full=can_access_full,
#                          related_articles=related_articles)

# @articles_bp.route('/<uuid:article_uuid>/preview')
# def preview_article(article_uuid):
#     """Show article preview for non-subscribed users"""
#     article = Article.query.filter_by(uuid=article_uuid, is_published=True).first_or_404()
    
#     # Only show preview content
#     return render_template('articles/preview.html', article=article)

# @articles_bp.route('/<uuid:article_uuid>/download')
# @login_required
# def download_pdf(article_uuid):
#     """Download PDF file - requires login"""
#     article = Article.query.filter_by(uuid=article_uuid, is_published=True).first_or_404()
    
#     # Check if user can download
#     if not (current_user.is_subscribed() or current_user.is_admin):
#         flash('You need a subscription to download articles.', 'error')
#         return redirect(url_for('articles.view_article', article_uuid=article_uuid))
    
#     # Check if file exists
#     if not os.path.exists(article.pdf_path):
#         flash('PDF file not found.', 'error')
#         return redirect(url_for('articles.view_article', article_uuid=article_uuid))
    
#     # Increment download count
#     article.increment_download_count()
    
#     # Send file
#     try:
#         return send_file(
#             article.pdf_path,
#             as_attachment=True,
#             download_name=f"{article.title}.pdf",
#             mimetype='application/pdf'
#         )
#     except Exception as e:
#         flash('Error downloading file. Please try again.', 'error')
#         return redirect(url_for('articles.view_article', article_uuid=article_uuid))

# @articles_bp.route('/category/<category_name>')
# def category_articles(category_name):
#     """Show articles in a specific category"""
#     page = request.args.get('page', 1, type=int)
#     sort_by = request.args.get('sort', 'latest')
    
#     # Get category
#     category = Category.query.filter_by(slug=category_name, is_active=True).first_or_404()
    
#     # Base query for published articles in this category
#     query = Article.query.filter_by(is_published=True, category=category.name)
    
#     # Apply sorting
#     if sort_by == 'popular':
#         query = query.order_by(Article.view_count.desc())
#     elif sort_by == 'featured':
#         query = query.filter_by(is_featured=True).order_by(Article.created_at.desc())
#     else:  # latest
#         query = query.order_by(Article.created_at.desc())
    
#     # Paginate results
#     articles = query.paginate(
#         page=page, per_page=12, error_out=False
#     )
    
#     return render_template('articles/category.html',
#                          articles=articles,
#                          category=category,
#                          current_sort=sort_by)

# @articles_bp.route('/api/<uuid:article_uuid>/like', methods=['POST'])
# @login_required
# def like_article(article_uuid):
#     """API endpoint to like/unlike an article"""
#     article = Article.query.filter_by(uuid=article_uuid).first_or_404()
    
#     # For now, just increment view count as a proxy for likes
#     # You can implement a proper likes system with a separate table
#     article.increment_view_count()
    
#     return jsonify({
#         'success': True,
#         'view_count': article.view_count
#     })

# @articles_bp.route('/api/popular')
# def api_popular_articles():
#     """API endpoint for popular articles"""
#     limit = request.args.get('limit', 5, type=int)
    
#     articles = Article.query.filter_by(is_published=True)\
#         .order_by(Article.view_count.desc())\
#         .limit(limit).all()
    
#     return jsonify([article.to_dict() for article in articles])

# @articles_bp.route('/api/featured')
# def api_featured_articles():
#     """API endpoint for featured articles"""
#     limit = request.args.get('limit', 6, type=int)
    
#     articles = Article.query.filter_by(is_published=True, is_featured=True)\
#         .order_by(Article.created_at.desc())\
#         .limit(limit).all()
    
#     return jsonify([article.to_dict() for article in articles])

# @articles_bp.route('/api/recent')
# def api_recent_articles():
#     """API endpoint for recent articles"""
#     limit = request.args.get('limit', 10, type=int)
    
#     articles = Article.query.filter_by(is_published=True)\
#         .order_by(Article.created_at.desc())\
#         .limit(limit).all()
    
#     return jsonify([article.to_dict() for article in articles])