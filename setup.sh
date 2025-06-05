#!/bin/bash
# Healthcare Kiosk Application Setup Script
# 헬스케어 키오스크 애플리케이션 설치 스크립트
# Created by Claude Code

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Language selection
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Healthcare Kiosk Setup / 헬스케어 키오스크 설치${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Select language / 언어를 선택하세요:"
echo "1) English"
echo "2) 한국어"
read -p "Choice / 선택: " lang_choice

# Set messages based on language
if [ "$lang_choice" = "2" ]; then
    MSG_CHECKING_PYTHON="Python 설치 확인 중..."
    MSG_PYTHON_NOT_FOUND="Python이 설치되어 있지 않습니다!"
    MSG_PYTHON_VERSION="Python 버전:"
    MSG_MIN_VERSION_REQUIRED="최소 Python 3.8 이상이 필요합니다"
    MSG_CREATING_VENV="가상환경 생성 중..."
    MSG_ACTIVATING_VENV="가상환경 활성화 중..."
    MSG_INSTALLING_DEPS="의존성 패키지 설치 중 (시간이 걸릴 수 있습니다)..."
    MSG_CREATING_ENV="환경 설정 파일 생성 중..."
    MSG_INIT_DB="데이터베이스 초기화 중..."
    MSG_CREATING_DIRS="필요한 디렉토리 생성 중..."
    MSG_SETUP_COMPLETE="설치가 완료되었습니다!"
    MSG_TO_RUN="애플리케이션 실행 방법:"
    MSG_ACTIVATE_VENV="가상환경 활성화:"
    MSG_RUN_APP="애플리케이션 실행:"
    MSG_ERROR="오류가 발생했습니다!"
    MSG_CHECK_LOGS="로그를 확인하거나 도움을 요청하세요."
else
    MSG_CHECKING_PYTHON="Checking Python installation..."
    MSG_PYTHON_NOT_FOUND="Python is not installed!"
    MSG_PYTHON_VERSION="Python version:"
    MSG_MIN_VERSION_REQUIRED="Minimum Python 3.8 required"
    MSG_CREATING_VENV="Creating virtual environment..."
    MSG_ACTIVATING_VENV="Activating virtual environment..."
    MSG_INSTALLING_DEPS="Installing dependencies (this may take a while)..."
    MSG_CREATING_ENV="Creating environment configuration file..."
    MSG_INIT_DB="Initializing database..."
    MSG_CREATING_DIRS="Creating necessary directories..."
    MSG_SETUP_COMPLETE="Setup completed successfully!"
    MSG_TO_RUN="To run the application:"
    MSG_ACTIVATE_VENV="Activate virtual environment:"
    MSG_RUN_APP="Run application:"
    MSG_ERROR="An error occurred!"
    MSG_CHECK_LOGS="Please check the logs or seek help."
fi

# Function to print colored messages
print_msg() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check Python version
check_python_version() {
    if command -v python3 &> /dev/null; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        major=$(echo $python_version | cut -d. -f1)
        minor=$(echo $python_version | cut -d. -f2)
        
        if [ $major -ge 3 ] && [ $minor -ge 8 ]; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# Main setup process
main() {
    print_msg $BLUE "
╔═══════════════════════════════════════╗
║    Healthcare Kiosk Setup Script      ║
║    헬스케어 키오스크 설치 스크립트         ║
╚═══════════════════════════════════════╝
"

    # Step 1: Check Python installation
    print_msg $YELLOW "1. $MSG_CHECKING_PYTHON"
    if ! check_python_version; then
        print_msg $RED "$MSG_PYTHON_NOT_FOUND"
        print_msg $RED "$MSG_MIN_VERSION_REQUIRED"
        exit 1
    fi
    print_msg $GREEN "✓ $MSG_PYTHON_VERSION $(python3 --version)"

    # Step 2: Create virtual environment
    print_msg $YELLOW "2. $MSG_CREATING_VENV"
    if [ -d "venv" ]; then
        print_msg $YELLOW "   Virtual environment already exists, skipping..."
    else
        python3 -m venv venv
        print_msg $GREEN "✓ Virtual environment created"
    fi

    # Step 3: Activate virtual environment and install dependencies
    print_msg $YELLOW "3. $MSG_ACTIVATING_VENV"
    source venv/bin/activate

    print_msg $YELLOW "4. $MSG_INSTALLING_DEPS"
    pip install --upgrade pip
    pip install -r requirements.txt
    print_msg $GREEN "✓ Dependencies installed"

    # Step 4: Create .env file if it doesn't exist
    print_msg $YELLOW "5. $MSG_CREATING_ENV"
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Application Settings
APP_NAME="Healthcare Kiosk"
APP_VERSION="1.0.0"
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DATABASE_URL=sqlite:///./kiosk.db

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 16)

# Session Management
SESSION_TIMEOUT_SECONDS=120
IDLE_TIMEOUT_SECONDS=120

# Hardware Devices
ENABLE_HARDWARE=false
PRINTER_PORT=/dev/ttyUSB0
CARD_READER_PORT=/dev/ttyUSB1
CASH_ACCEPTOR_PORT=/dev/ttyUSB2

# Language Settings
DEFAULT_LANGUAGE=ko
SUPPORTED_LANGUAGES=["ko", "en", "zh", "vi"]

# TTS Configuration
TTS_ENABLED=true
TTS_SPEED=1.0

# Admin Settings (CHANGE THESE!)
ADMIN_PASSWORD=admin123
ADMIN_NFC_CARD_ID=0123456789

# Monitoring
ENABLE_MONITORING=false
SENTRY_DSN=

# Backup
BACKUP_PATH=./backups
BACKUP_RETENTION_DAYS=30
EOF
        print_msg $GREEN "✓ Environment configuration created"
    else
        print_msg $YELLOW "   .env file already exists, skipping..."
    fi

    # Step 5: Create necessary directories
    print_msg $YELLOW "6. $MSG_CREATING_DIRS"
    mkdir -p static/images
    mkdir -p static/tutorials
    mkdir -p static/videos
    mkdir -p locale
    mkdir -p logs
    mkdir -p backups
    print_msg $GREEN "✓ Directories created"

    # Step 6: Initialize database
    print_msg $YELLOW "7. $MSG_INIT_DB"
    python -c "from app.core.database import init_db; init_db()"
    print_msg $GREEN "✓ Database initialized"

    # Setup complete
    print_msg $GREEN "
╔═══════════════════════════════════════╗
║        $MSG_SETUP_COMPLETE             ║
╚═══════════════════════════════════════╝
"

    print_msg $BLUE "$MSG_TO_RUN"
    print_msg $YELLOW "$MSG_ACTIVATE_VENV"
    print_msg $NC "    source venv/bin/activate"
    print_msg $YELLOW "$MSG_RUN_APP"
    print_msg $NC "    ./run.sh"
}

# Error handler
error_handler() {
    print_msg $RED "$MSG_ERROR"
    print_msg $RED "$MSG_CHECK_LOGS"
    exit 1
}

# Set error handler
trap error_handler ERR

# Run main setup
main