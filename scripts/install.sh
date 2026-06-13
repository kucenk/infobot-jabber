#!/bin/bash
# install.sh - Installation script for Armbian

set -e

echo "🚀 InfoBot Jabber Setup untuk Armbian"
echo "======================================"

# Check Python version
python3 --version

# Create bot user (optional)
# sudo useradd -m -s /bin/bash infobot

# Clone or extract
cd /home/infobot
git clone https://github.com/kucenk/infobot-jabber.git
cd infobot-jabber

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
mkdir -p logs config data

# Copy config
cp config/config.example.yaml config/config.yaml

# Edit config
echo "⚙️  Edit config/config.yaml dengan kredensial Anda"
nano config/config.yaml

# Test run
echo "🧪 Testing bot..."
python3 main.py &
sleep 5
kill %1

# Setup systemd
sudo cp systemd/infobot.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable infobot
sudo systemctl start infobot

echo "✅ Setup selesai!"
echo ""
echo "Gunakan:"
echo "  sudo systemctl status infobot"
echo "  sudo journalctl -u infobot -f"
