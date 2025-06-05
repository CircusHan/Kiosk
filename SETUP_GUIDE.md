# Healthcare Kiosk Setup Guide / 헬스케어 키오스크 설치 가이드

[English](#english) | [한국어](#korean)

---

<a name="english"></a>
## English Guide

### System Requirements

- **Operating System**: macOS, Linux, or Windows 10+
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space
- **Display**: 1024x768 minimum resolution

### Quick Start

1. **Download and Extract**
   ```bash
   cd /path/to/kiosk_app
   ```

2. **Run Setup Script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Run Application**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

### Detailed Installation Steps

#### Step 1: Install Python (if not installed)

**macOS:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.12
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

**Windows:**
1. Download Python from https://www.python.org/downloads/
2. Run installer and check "Add Python to PATH"
3. Open Command Prompt or PowerShell

#### Step 2: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd kiosk_app

# Or download and extract the ZIP file
```

#### Step 3: Run Automated Setup

```bash
# Make scripts executable (macOS/Linux)
chmod +x setup.sh run.sh

# Run setup
./setup.sh
```

The setup script will:
- Check Python installation
- Create virtual environment
- Install all dependencies
- Create configuration files
- Initialize database
- Create necessary directories

#### Step 4: Configure the Application

Edit the `.env` file to customize settings:

```bash
# Open in text editor
nano .env  # or use any text editor
```

Important settings to change:
- `SECRET_KEY`: Generate a new secret key for production
- `ADMIN_PASSWORD`: Change from default 'admin123'
- `DATABASE_URL`: Change if using PostgreSQL/MySQL
- `ENABLE_HARDWARE`: Set to 'true' if hardware devices are connected

#### Step 5: Run the Application

```bash
./run.sh
```

Select from menu:
1. **Full Application**: Runs both GUI and API server
2. **API Only**: Runs just the backend API server
3. **Development Mode**: Enables hot reload for development
4. **Run Tests**: `pytest -v tests/`
5. **Database Reset**: Clear and reinitialize database

### Troubleshooting

#### Python Not Found
```bash
# Check Python installation
python3 --version

# If not found, install Python 3.8+
```

#### Permission Denied
```bash
# Make scripts executable
chmod +x setup.sh run.sh
```

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in .env
```

#### Module Import Errors
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Manual Installation (Alternative)

If the setup script doesn't work:

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Create Configuration**
   ```bash
   cp .env.example .env  # or create manually
   ```

4. **Initialize Database**
   ```bash
   python -c "from app.core.database import init_db; init_db()"
   ```

5. **Run Application**
   ```bash
   python -m app.main
   ```

### API Documentation

When running, access:
- API Endpoint: `http://localhost:8000`
- API Documentation: `http://localhost:8000/api/docs`
- Health Check: `http://localhost:8000/health`

---

<a name="korean"></a>
## 한국어 가이드

### 시스템 요구사항

- **운영체제**: macOS, Linux, 또는 Windows 10 이상
- **Python**: 3.8 버전 이상
- **메모리**: 최소 4GB RAM (8GB 권장)
- **저장공간**: 최소 2GB 여유 공간
- **디스플레이**: 최소 1024x768 해상도

### 빠른 시작

1. **다운로드 및 압축 해제**
   ```bash
   cd /path/to/kiosk_app
   ```

2. **설치 스크립트 실행**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **애플리케이션 실행**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

### 상세 설치 단계

#### 1단계: Python 설치 (설치되지 않은 경우)

**macOS:**
```bash
# Homebrew 설치 (설치되지 않은 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 설치
brew install python@3.12
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

**Windows:**
1. https://www.python.org/downloads/ 에서 Python 다운로드
2. 설치 프로그램 실행 시 "Add Python to PATH" 체크
3. 명령 프롬프트 또는 PowerShell 열기

#### 2단계: 프로젝트 다운로드

```bash
# git 사용 시
git clone <repository-url>
cd kiosk_app

# 또는 ZIP 파일 다운로드 후 압축 해제
```

#### 3단계: 자동 설치 실행

```bash
# 스크립트 실행 권한 부여 (macOS/Linux)
chmod +x setup.sh run.sh

# 설치 실행
./setup.sh
```

설치 스크립트가 수행하는 작업:
- Python 설치 확인
- 가상환경 생성
- 모든 의존성 패키지 설치
- 설정 파일 생성
- 데이터베이스 초기화
- 필요한 디렉토리 생성

#### 4단계: 애플리케이션 설정

`.env` 파일을 편집하여 설정 변경:

```bash
# 텍스트 편집기로 열기
nano .env  # 또는 다른 텍스트 편집기 사용
```

변경해야 할 중요 설정:
- `SECRET_KEY`: 운영환경용 새 시크릿 키 생성
- `ADMIN_PASSWORD`: 기본값 'admin123'에서 변경
- `DATABASE_URL`: PostgreSQL/MySQL 사용 시 변경
- `ENABLE_HARDWARE`: 하드웨어 장치 연결 시 'true'로 설정

#### 5단계: 애플리케이션 실행

```bash
./run.sh
```

메뉴에서 선택:
1. **전체 애플리케이션**: GUI와 API 서버 모두 실행
2. **API 서버만**: 백엔드 API 서버만 실행
3. **개발 모드**: 개발용 자동 새로고침 활성화
4. **테스트 실행**: 테스트 스위트 실행
5. **데이터베이스 초기화**: 데이터베이스 초기화 및 재생성

### 문제 해결

#### Python을 찾을 수 없음
```bash
# Python 설치 확인
python3 --version

# 없다면 Python 3.8+ 설치
```

#### 권한 거부됨
```bash
# 스크립트 실행 권한 부여
chmod +x setup.sh run.sh
```

#### 포트가 이미 사용 중
```bash
# 8000번 포트 사용 프로세스 찾기
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 프로세스 종료 또는 .env에서 포트 변경
```

#### 모듈 임포트 오류
```bash
# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# 의존성 재설치
pip install -r requirements.txt
```

### 수동 설치 (대안)

설치 스크립트가 작동하지 않는 경우:

1. **가상환경 생성**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # 또는
   venv\Scripts\activate  # Windows
   ```

2. **의존성 설치**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **설정 파일 생성**
   ```bash
   cp .env.example .env  # 또는 수동으로 생성
   ```

4. **데이터베이스 초기화**
   ```bash
   python -c "from app.core.database import init_db; init_db()"
   ```

5. **애플리케이션 실행**
   ```bash
   python -m app.main
   ```

### API 문서

실행 중일 때 접속:
- API 엔드포인트: `http://localhost:8000`
- API 문서: `http://localhost:8000/api/docs`
- 상태 확인: `http://localhost:8000/health`

### 추가 도움말

#### 일반적인 오류 메시지와 해결법

1. **"ModuleNotFoundError: No module named 'app'"**
   - 현재 디렉토리가 프로젝트 루트인지 확인
   - 가상환경이 활성화되었는지 확인

2. **"sqlite3.OperationalError: unable to open database file"**
   - 디렉토리 쓰기 권한 확인
   - 데이터베이스 파일 경로 확인

3. **"ImportError: cannot import name 'xxx' from 'PySide6'"**
   - PySide6 재설치: `pip install --force-reinstall PySide6`

#### 성능 최적화 팁

1. **운영 환경 설정**
   ```bash
   # .env 파일에서
   DEBUG=false
   WORKERS=4  # CPU 코어 수에 맞게 조정
   ```

2. **데이터베이스 최적화**
   - SQLite 대신 PostgreSQL 사용 고려
   - 정기적인 데이터베이스 백업

3. **로그 관리**
   - 로그 레벨을 INFO 또는 WARNING으로 설정
   - 로그 파일 정기 정리

### 지원 및 문의

문제가 지속되면:
1. `logs/` 디렉토리의 로그 파일 확인
2. GitHub Issues에 문제 보고
3. 시스템 정보와 오류 메시지 포함

---

## License / 라이선스

This project is licensed under the MIT License.
이 프로젝트는 MIT 라이선스 하에 배포됩니다.