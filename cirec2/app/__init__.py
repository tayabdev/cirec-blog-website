from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
# from flask_wtf.csrf import CSRFProtect  # Temporarily commented out
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
# csrf = CSRFProtect()  # Temporarily commented out

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    # csrf.init_app(app)  # Temporarily commented out
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.articles import articles_bp
    from app.routes.search import search_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(articles_bp, url_prefix='/articles')
    app.register_blueprint(search_bp, url_prefix='/search')
    
    return app