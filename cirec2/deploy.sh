# Make deploy script executable
# chmod +x deploy.sh

# # Copy CSS content to actual file
# cat > static/css/main.css << 'EOF'
# [Copy the CSS content from the main.css artifact here]
# EOF

# # Copy JS content to actual file  
# cat > static/js/main.js << 'EOF'
# [Copy the JS content from the main.js artifact here]
# EOF

# # Create favicon placeholder
# touch static/images/favicon.ico




#!/bin/bash

# CIREC Blog Deployment Script
echo "🚀 Deploying CIREC Blog System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p static/css static/js static/images uploads/pdfs

# Database setup
echo "Setting up database..."
export FLASK_APP=run.py

# Run migrations
flask db upgrade

# Initialize default data if needed
flask init-categories

# Create admin user if it doesn't exist
flask create-admin

# Show system stats
flask stats

echo "✅ Deployment complete!"
echo "🌐 Application URL: http://localhost:3000/"
echo "👤 Admin login: tayab.dev1@gmail.com / tayab123"
echo ""
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  python run.py"