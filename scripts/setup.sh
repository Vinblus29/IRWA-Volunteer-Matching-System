#!/bin/bash

# Volunteer Matching System Setup Script
echo "🚀 Setting up Volunteer Matching System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment for Python
echo "📦 Setting up Python virtual environment..."
cd backend
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix/Linux/macOS
    source venv/bin/activate
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words'); nltk.download('wordnet')"

# Download spaCy model (optional)
echo "📚 Downloading spaCy model..."
python -m spacy download en_core_web_sm || echo "⚠️  SpaCy model download failed, continuing without it"

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f .env ]; then
    cp ../.env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env file with your OpenAI API key and other credentials"
else
    echo "✅ .env file already exists"
fi

# Go to frontend directory
cd ../frontend

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

echo "✅ Setup completed successfully!"
echo ""
echo "🎉 Next steps:"
echo "1. Edit backend/.env file with your OpenAI API key"
echo "2. Start the backend: cd backend && python -m uvicorn app.main:app --reload"
echo "3. Start the frontend: cd frontend && npm start"
echo ""
echo "📚 Useful URLs:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo "🤖 The system includes intelligent agents for:"
echo "- Skill profiling and analysis"
echo "- Event matching optimization"
echo "- Availability tracking"
echo ""
echo "Happy coding! 🚀" 