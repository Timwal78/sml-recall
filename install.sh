#!/usr/bin/env bash
# SML-RECALL Installation Script

echo "━━━ SML-RECALL SETUP ━━━"
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

if [ ! -f config.yaml ]; then
    echo "Copying config.yaml.example to config.yaml..."
    cp config.yaml.example config.yaml
    echo "⚠️ Please edit config.yaml to add your Anthropic API key and RECALL key."
else
    echo "✅ config.yaml already exists."
fi

if [ ! -f MASTER.md ]; then
    echo "Copying free/templates/MASTER.md to root..."
    cp free/templates/MASTER.md MASTER.md
else
    echo "✅ MASTER.md already exists in root."
fi

echo "━━━ SETUP COMPLETE ━━━"
echo "Activate your environment with: source .venv/bin/activate"
