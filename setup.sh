#!/bin/bash
# Setup Script für Website Compliance Crawler
# Erstellt Virtual Environment und installiert Dependencies

set -e  # Exit bei Fehler

echo "🚀 Setup Website Compliance Crawler..."
echo ""

# 1. Virtual Environment erstellen
if [ -d "venv" ]; then
    echo "✓ Virtual Environment existiert bereits"
else
    echo "📦 Erstelle Virtual Environment..."
    python3 -m venv venv
    echo "✓ Virtual Environment erstellt"
fi

echo ""

# 2. Virtual Environment aktivieren
echo "🔧 Aktiviere Virtual Environment..."
source venv/bin/activate

echo ""

# 3. Dependencies installieren
echo "📥 Installiere Dependencies..."
pip install -q --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup erfolgreich!"
echo ""
echo "Zum Aktivieren des Virtual Environments:"
echo "  source venv/bin/activate"
echo ""
echo "Zum Testen:"
echo "  python test_parser.py"
echo ""
