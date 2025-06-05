#!/bin/bash
# Healthcare Kiosk Application Run Script
# 헬스케어 키오스크 애플리케이션 실행 스크립트
# Created by Claude Code

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_msg() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_msg $RED "Virtual environment not found! / 가상환경을 찾을 수 없습니다!"
    print_msg $YELLOW "Please run setup.sh first / 먼저 setup.sh를 실행하세요"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Display menu
print_msg $BLUE "
╔═══════════════════════════════════════════════╗
║     Healthcare Kiosk Application              ║
║     헬스케어 키오스크 애플리케이션                  ║
╚═══════════════════════════════════════════════╝
"

print_msg $YELLOW "Select run mode / 실행 모드를 선택하세요:"
echo "1) Full Application (GUI + API) / 전체 애플리케이션 (GUI + API)"
echo "2) API Server Only / API 서버만"
echo "3) Development Mode / 개발 모드"
echo "4) Run Tests / 테스트 실행"
echo "5) Database Reset / 데이터베이스 초기화"
echo "6) Exit / 종료"
echo ""
read -p "Choice / 선택 [1-6]: " choice

case $choice in
    1)
        print_msg $GREEN "Starting full application... / 전체 애플리케이션 시작 중..."
        print_msg $YELLOW "Press Ctrl+C to stop / 중지하려면 Ctrl+C를 누르세요"
        python -m app.main
        ;;
    2)
        print_msg $GREEN "Starting API server... / API 서버 시작 중..."
        print_msg $YELLOW "Access API at: http://localhost:8000"
        print_msg $YELLOW "API Docs at: http://localhost:8000/api/docs"
        print_msg $YELLOW "Press Ctrl+C to stop / 중지하려면 Ctrl+C를 누르세요"
        python -m app.main --api-only
        ;;
    3)
        print_msg $GREEN "Starting in development mode... / 개발 모드로 시작 중..."
        print_msg $YELLOW "Hot reload enabled / 자동 새로고침 활성화"
        # Set development environment variables
        export DEBUG=true
        export LOG_LEVEL=DEBUG
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    4)
        print_msg $GREEN "Running tests... / 테스트 실행 중..."
        pytest -v tests/
        ;;
    5)
        print_msg $YELLOW "⚠️  WARNING: This will reset the database! / 경고: 데이터베이스가 초기화됩니다!"
        read -p "Continue? [y/N] / 계속하시겠습니까? [y/N]: " confirm
        if [[ $confirm == [yY] ]]; then
            print_msg $YELLOW "Resetting database... / 데이터베이스 초기화 중..."
            rm -f kiosk.db
            python -c "from app.core.database import init_db; init_db()"
            print_msg $GREEN "✓ Database reset complete / 데이터베이스 초기화 완료"
        else
            print_msg $YELLOW "Cancelled / 취소됨"
        fi
        ;;
    6)
        print_msg $BLUE "Goodbye! / 안녕히 가세요!"
        exit 0
        ;;
    *)
        print_msg $RED "Invalid choice! / 잘못된 선택입니다!"
        exit 1
        ;;
esac