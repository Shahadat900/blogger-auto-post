#!/data/data/com.termux/files/usr/bin/bash

echo "============================================"
echo "  Islamic Guide - Termux Setup"
echo "============================================"
echo ""

echo "[1/5] Updating packages..."
pkg update -y && pkg upgrade -y

echo "[2/5] Installing Python and Git..."
pkg install -y python git cronie

echo "[3/5] Installing pip packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[4/5] Cloning repository..."
if [ ! -d "blogger-auto-post" ]; then
    git clone https://github.com/Shahadat900/blogger-auto-post.git
fi

cd blogger-auto-post

echo "[5/5] Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env with your keys:"
    echo "  nano .env"
    echo ""
    echo "You need to set:"
    echo "  - GEMINI_API_KEY"
    echo "  - BLOGGER_CLIENT_ID"
    echo "  - BLOGGER_CLIENT_SECRET"
    echo "  - BLOGGER_REFRESH_TOKEN"
    echo "  - BLOGGER_BLOG_ID"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To add cron job:"
echo "  crontab -e"
echo ""
echo "Then add this line for 2 posts/day:"
echo "  0 8,20 * * * cd ~/blogger-auto-post && python scripts/main.py >> logs.txt 2>&1"
echo ""
echo "Or run manually:"
echo "  cd ~/blogger-auto-post && python scripts/main.py"
