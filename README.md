# 배리어-프리 보건소 키오스크

디지털 취약계층(고령자·장애인·외국인)을 포함한 누구나 쉽게 이용할 수 있는 Python 기반 보건소 키오스크 시스템

## 주요 기능

### 1. 접근성 지원
- 글자 크기 조절 (±)
- 고대비 및 색맹 모드
- 터치 진동 및 음성 TTS 지원
- 다국어 UI (한국어, 영어, 중국어, 베트남어)
- 화면 높이 및 버튼 배치 조절
- 비상 도움 요청 버튼

### 2. 주요 서비스
- **접수**: 예약 확인, 증상 선택, 순번표 발급
- **수납**: 진료비 결제 (현금/카드/QR)
- **증명서 발급**: 진단서, 진료확인서, 접종증명서

### 3. 부가 기능
- 처방약 목록 및 복약 방법 안내
- 백신 접종 일정 확인
- 근처 의료시설 지도 안내
- 체온/혈압/체중 측정 기기 연동

## 기술 스택

- **언어**: Python 3.12+
- **백엔드**: FastAPI + Uvicorn
- **프론트엔드**: PySide6
- **데이터베이스**: SQLite (SQLModel/SQLAlchemy)
- **상태관리**: transitions (FSM)
- **다국어**: Babel
- **스케줄링**: APScheduler
- **테스트**: pytest, Playwright

## 설치 및 실행

### 1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 입력
```

### 4. 데이터베이스 초기화
```bash
python -m app.core.database init
```

### 5. 애플리케이션 실행
```bash
# 개발 서버
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 (GUI 포함)
python -m app.main
```

### 6. 테스트 실행
```bash
pytest -v tests/
```

## 프로젝트 구조

```
kiosk_app/
├── app/
│   ├── main.py               # FastAPI 엔트리포인트
│   ├── state_machine.py      # 화면 전환 FSM
│   ├── i18n.py              # 다국어 헬퍼
│   ├── core/                # 핵심 모듈
│   ├── services/            # 비즈니스 로직
│   ├── hardware/            # 하드웨어 인터페이스
│   ├── ui/                  # GUI 컴포넌트
│   └── utils/               # 유틸리티
├── static/                  # 정적 파일
├── locale/                  # 번역 파일
├── tests/                   # 테스트
└── Dockerfile              # 컨테이너 설정
```

## 보안

- 전 구간 SSL/TLS 암호화
- 민감 정보 AES 암호화
- 유휴 시간 자동 초기화 (2분)
- 세션 종료 시 메모리 및 로그 마스킹

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.