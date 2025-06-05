# Troubleshooting Guide / 문제 해결 가이드

## Common Issues and Solutions / 일반적인 문제와 해결법

### 1. Python Installation Issues / Python 설치 문제

#### Problem: Python not found / Python을 찾을 수 없음
```
bash: python3: command not found
```

**Solution / 해결법:**

**macOS:**
```bash
# Install Homebrew first
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then install Python
brew install python@3.12

# Verify installation
python3 --version
```

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Restart terminal

**Linux:**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```

### 2. Virtual Environment Issues / 가상환경 문제

#### Problem: venv module not found / venv 모듈을 찾을 수 없음
```
Error: No module named venv
```

**Solution / 해결법:**
```bash
# Ubuntu/Debian
sudo apt install python3.12-venv

# macOS (reinstall Python)
brew reinstall python@3.12

# Windows (reinstall Python with all components)
```

### 3. Permission Errors / 권한 오류

#### Problem: Permission denied / 권한이 거부됨
```
bash: ./setup.sh: Permission denied
```

**Solution / 해결법:**
```bash
chmod +x setup.sh run.sh
```

### 4. Port Already in Use / 포트가 이미 사용 중

#### Problem: Address already in use / 주소가 이미 사용 중
```
[Errno 48] Address already in use
```

**Solution / 해결법:**

**Find process using port 8000 / 8000번 포트를 사용하는 프로세스 찾기:**
```bash
# macOS/Linux
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

**Kill the process / 프로세스 종료:**
```bash
# macOS/Linux (replace PID with actual process ID)
kill -9 PID

# Windows
taskkill /PID PID /F
```

**Or change port in .env / 또는 .env에서 포트 변경:**
```
PORT=8001
```

### 5. Database Errors / 데이터베이스 오류

#### Problem: Unable to open database file / 데이터베이스 파일을 열 수 없음
```
sqlite3.OperationalError: unable to open database file
```

**Solution / 해결법:**
```bash
# Check directory permissions
ls -la

# Create directory if missing
mkdir -p data

# Reset database
rm -f kiosk.db
python -c "from app.core.database import init_db; init_db()"
```

### 6. Module Import Errors / 모듈 임포트 오류

#### Problem: ModuleNotFoundError / 모듈을 찾을 수 없음
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution / 해결법:**
```bash
# Activate virtual environment first!
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 7. GUI Display Issues / GUI 디스플레이 문제

#### Problem: No display or black screen / 화면이 표시되지 않음
```
qt.qpa.xcb: could not connect to display
```

**Solution / 해결법:**

**Linux with SSH:**
```bash
# Enable X11 forwarding
ssh -X user@host

# Or set display
export DISPLAY=:0
```

**macOS:**
```bash
# Install XQuartz if needed
brew install --cask xquartz
# Logout and login again
```

### 8. TTS (Text-to-Speech) Not Working / 음성 안내가 작동하지 않음

#### Problem: No audio output / 오디오 출력 없음

**Solution / 해결법:**
```bash
# Install system TTS
# macOS (already included)
# Linux
sudo apt install espeak

# Disable TTS in .env if causing issues
TTS_ENABLED=false
```

### 9. Memory Issues / 메모리 문제

#### Problem: Out of memory / 메모리 부족
```
MemoryError
```

**Solution / 해결법:**
- Close other applications / 다른 애플리케이션 종료
- Reduce workers in .env / .env에서 worker 수 감소:
  ```
  WORKERS=2
  ```
- Use API-only mode / API 전용 모드 사용:
  ```bash
  ./run.sh
  # Select option 2
  ```

### 10. SSL/Certificate Errors / SSL/인증서 오류

#### Problem: SSL certificate verify failed / SSL 인증서 검증 실패

**Solution / 해결법:**
```bash
# Update certificates
# macOS
brew install ca-certificates

# Linux
sudo apt-get update && sudo apt-get install ca-certificates

# Python
pip install --upgrade certifi
```

## Quick Diagnostic Commands / 빠른 진단 명령어

### Check System / 시스템 확인
```bash
# Python version
python3 --version

# Pip version
pip --version

# Current directory
pwd

# List files
ls -la

# Check disk space
df -h

# Check memory
free -h  # Linux
top      # macOS/Linux
```

### Test Installation / 설치 테스트
```bash
# Test Python
python3 -c "print('Python works!')"

# Test virtual environment
source venv/bin/activate
python -c "import sys; print(sys.prefix)"

# Test imports
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import PySide6; print('PySide6 installed')"
```

### Reset Everything / 모두 초기화
```bash
# Complete reset (WARNING: removes all data)
rm -rf venv kiosk.db logs/* backups/*
./setup.sh
```

## Log Files / 로그 파일

Check logs for detailed error information / 자세한 오류 정보는 로그 확인:

```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# View all logs
cat logs/app.log | less
```

## Getting Help / 도움 받기

If problems persist / 문제가 지속되면:

1. **Collect Information / 정보 수집:**
   ```bash
   python3 --version > debug_info.txt
   pip list >> debug_info.txt
   echo "=== Error Log ===" >> debug_info.txt
   tail -n 50 logs/app.log >> debug_info.txt
   ```

2. **Include in report / 보고서에 포함:**
   - Operating system / 운영체제
   - Python version / Python 버전
   - Error messages / 오류 메시지
   - Steps to reproduce / 재현 단계

3. **Contact / 연락처:**
   - GitHub Issues
   - Email support
   - Community forum

## Prevention Tips / 예방 팁

1. **Regular Updates / 정기 업데이트:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Backup Data / 데이터 백업:**
   ```bash
   cp kiosk.db backups/kiosk_$(date +%Y%m%d).db
   ```

3. **Monitor Logs / 로그 모니터링:**
   - Check logs daily / 매일 로그 확인
   - Set up log rotation / 로그 순환 설정

4. **Test Before Deploy / 배포 전 테스트:**
   ```bash
   ./run.sh
   # Select option 4 (Run Tests)
   ```