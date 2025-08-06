
#!/bin/bash

echo "🎯 Research Analyser Development Setup"
echo "======================================"

# Navigate to the ResearchAnalyser directory
cd "$(dirname "$0")"

# Install dependencies if needed
if [ ! -f "backend/.venv_created" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    touch backend/.venv_created
fi

echo "🚀 Starting Development Servers..."
echo "Backend: http://0.0.0.0:8000"
echo "Frontend: http://0.0.0.0:3000" 
echo "API Docs: http://0.0.0.0:8000/docs"
echo "======================================"

# Run the start script
python3 start.py
