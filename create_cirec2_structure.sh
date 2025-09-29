#!/bin/bash

mkdir -p cirec2/app/models
mkdir -p cirec2/app/routes
mkdir -p cirec2/app/services
mkdir -p cirec2/app/utils
mkdir -p cirec2/app/templates/auth
mkdir -p cirec2/app/templates/articles
mkdir -p cirec2/app/templates/admin
mkdir -p cirec2/app/templates/components
mkdir -p cirec2/static/css
mkdir -p cirec2/static/js
mkdir -p cirec2/static/images
mkdir -p cirec2/uploads/pdfs
mkdir -p cirec2/migrations
mkdir -p cirec2/tests

touch cirec2/app/__init__.py
touch cirec2/app/config.py
touch cirec2/app/models/__init__.py
touch cirec2/app/models/user.py
touch cirec2/app/models/article.py
touch cirec2/app/models/subscription.py
touch cirec2/app/routes/__init__.py
touch cirec2/app/routes/auth.py
touch cirec2/app/routes/admin.py
touch cirec2/app/routes/articles.py
touch cirec2/app/routes/search.py
touch cirec2/app/services/__init__.py
touch cirec2/app/services/pdf_processor.py
touch cirec2/app/services/embedding_service.py
touch cirec2/app/services/search_service.py
touch cirec2/app/services/email_service.py
touch cirec2/app/utils/__init__.py
touch cirec2/app/utils/decorators.py
touch cirec2/app/utils/validators.py
touch cirec2/app/utils/helpers.py
touch cirec2/app/templates/base.html
touch cirec2/app/templates/index.html
touch cirec2/app/templates/auth/login.html
touch cirec2/app/templates/auth/register.html
touch cirec2/app/templates/auth/forgot_password.html
touch cirec2/app/templates/articles/list.html
touch cirec2/app/templates/articles/detail.html
touch cirec2/app/templates/articles/preview.html
touch cirec2/app/templates/admin/dashboard.html
touch cirec2/app/templates/admin/add_article.html
touch cirec2/app/templates/admin/manage_articles.html
touch cirec2/app/templates/components/navbar.html
touch cirec2/app/templates/components/footer.html
touch cirec2/app/templates/components/search_bar.html
touch cirec2/static/css/main.css
touch cirec2/static/css/auth.css
touch cirec2/static/css/articles.css
touch cirec2/static/css/admin.css
touch cirec2/static/js/main.js
touch cirec2/static/js/search.js
touch cirec2/static/js/admin.js
touch cirec2/tests/__init__.py
touch cirec2/tests/test_auth.py
touch cirec2/tests/test_articles.py
touch cirec2/tests/test_search.py
touch cirec2/requirements.txt
touch cirec2/.env
touch cirec2/.gitignore
touch cirec2/run.py
touch cirec2/README.md