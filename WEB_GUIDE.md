# 웹 인터페이스 가이드

## 📱 웹 기반 배리어-프리 키오스크

이제 **HTML, CSS, JavaScript**로 구현된 웹 인터페이스를 통해 키오스크를 사용할 수 있습니다!

## 🚀 실행 방법

### 1. 서버 시작
```bash
cd /Users/smcrony/kiosk_app
python -m app.main
```

### 2. 웹 브라우저 접속
- **일반 모드**: http://localhost:8000
- **키오스크 모드**: http://localhost:8000/kiosk
- **관리자 모드**: http://localhost:8000/admin

## 📁 웹 파일 구조

```
kiosk_app/
├── templates/
│   └── index.html              # 메인 HTML 템플릿
├── static/
│   ├── css/
│   │   ├── main.css           # 메인 스타일시트
│   │   └── accessibility.css  # 접근성 전용 스타일
│   └── js/
│       ├── app.js             # 메인 애플리케이션 로직
│       ├── accessibility.js   # 접근성 관리
│       ├── i18n.js           # 다국어 지원
│       └── api.js            # API 통신
└── app/api/endpoints/
    ├── web.py                 # 웹 라우터
    └── websocket.py           # 실시간 통신
```

## 🎨 주요 기능

### ✨ 접근성 기능
- **글자 크기 조절**: 슬라이더로 12-24pt 조절
- **고대비 모드**: 시각장애인을 위한 고대비 색상
- **음성 안내**: Web Speech API 기반 TTS
- **키보드 네비게이션**: Tab, Enter, ESC 키 지원
- **터치 최적화**: 큰 버튼, 진동 피드백
- **색맹 지원**: 프로토노피아, 듀테라노피아, 트리타노피아

### 🌍 다국어 지원
- **4개 언어**: 한국어, 영어, 중국어, 베트남어
- **실시간 전환**: 페이지 새로고침 없이 언어 변경
- **음성 안내**: 언어별 TTS 지원

### 📱 반응형 디자인
- **모바일 최적화**: 768px 이하 화면 지원
- **터치 친화적**: 최소 44px 터치 타겟
- **다양한 화면**: 태블릿, 데스크톱 지원

### ⚡ 실시간 기능
- **WebSocket 통신**: 실시간 대기열 업데이트
- **세션 관리**: 2분 자동 타임아웃
- **오프라인 지원**: 네트워크 끊김 시 대기열 처리

## 🔧 사용법

### 기본 흐름
1. **홈 화면**: 3개 서비스 버튼 (접수/수납/증명서)
2. **접수 화면**: 
   - 환자정보 입력 → 증상선택 → 진료과선택 → 순번표
3. **음성 안내**: 화면 전환시 자동 음성 안내
4. **도움 요청**: 빨간 "도움요청" 버튼으로 직원 호출

### 접근성 기능 사용
- **글자 크기**: 상단 슬라이더로 조절
- **고대비**: "고대비" 버튼 클릭
- **음성**: "음성안내" 버튼으로 켜기/끄기
- **언어**: 드롭다운에서 언어 선택

### 키보드 단축키
- `Ctrl/Cmd + +`: 글자 크기 증가
- `Ctrl/Cmd + -`: 글자 크기 감소  
- `Ctrl/Cmd + 0`: 글자 크기 초기화
- `Alt + C`: 고대비 모드 토글
- `Alt + V`: 음성 안내 토글
- `Alt + H`: 도움 요청
- `ESC`: 홈으로 돌아가기
- `F1`: 도움말 표시

## 🎯 접근성 특징

### WCAG 2.1 준수
- **Level AA** 기준 충족
- **색상 대비비**: 최소 4.5:1
- **포커스 표시**: 명확한 시각적 피드백
- **스크린 리더**: ARIA 라벨 완전 지원

### 디지털 취약계층 고려
- **고령자**: 큰 버튼, 간단한 UI
- **시각장애인**: 스크린 리더, 고대비 모드
- **청각장애인**: 시각적 피드백 강화
- **외국인**: 4개 언어 지원

### 인지 접근성
- **명확한 단계**: 진행 상황 표시
- **오류 방지**: 실시간 입력 검증
- **시간 연장**: 타임아웃 전 경고

## 🔄 API 연동

### RESTful API
```javascript
// 환자 검색
const patient = await api.searchPatient(phone);

// 접수 생성
const appointment = await api.createWalkInAppointment(patientId, symptoms);

// 대기열 상태 조회
const queueStatus = await api.getQueueStatus(department);
```

### WebSocket 실시간 통신
```javascript
// 대기열 업데이트 수신
wsClient.on('queue_update', (data) => {
    updateQueueDisplay(data);
});

// 공지사항 수신
wsClient.on('announcement', (data) => {
    showAnnouncement(data.message);
});
```

## 🎛️ 설정

### 환경 변수 (.env)
```bash
# UI 설정
UI_FONT_SIZE_DEFAULT=16
UI_FONT_SIZE_MIN=12
UI_FONT_SIZE_MAX=24
UI_CONTRAST_MODE=False

# TTS 설정
TTS_ENABLED=True
TTS_VOICE=ko-KR-Wavenet-A
TTS_SPEED=1.0

# 세션 설정
SESSION_TIMEOUT_SECONDS=120
IDLE_TIMEOUT_SECONDS=120
```

### JavaScript 설정
```javascript
// 접근성 설정
accessibility.settings = {
    fontSize: 16,
    highContrast: false,
    voiceEnabled: true,
    colorblindMode: 'none'
};

// 언어 설정
i18n.setLanguage('ko');
```

## 🎨 스타일 커스터마이징

### CSS 변수 수정
```css
:root {
    --primary-color: #3498db;
    --font-size-base: 16px;
    --min-touch-target: 44px;
    --border-radius: 15px;
}
```

### 접근성 모드
```css
/* 고대비 모드 */
body.high-contrast {
    --background-color: #000000;
    --text-color: #ffffff;
    --primary-color: #ffff00;
}

/* 큰 터치 모드 */
body.large-touch button {
    min-height: 60px;
    padding: 20px;
}
```

## 🐛 디버깅

### 브라우저 개발자 도구
```javascript
// 접근성 리포트
console.log(accessibility.generateAccessibilityReport());

// API 상태 확인
console.log(await api.getSessionStatus());

// WebSocket 연결 상태
console.log(wsClient.ws.readyState);
```

### 로그 확인
```bash
# 서버 로그
tail -f logs/kiosk_*.log

# 브라우저 콘솔에서 네트워크 탭 확인
```

## 📱 모바일 최적화

### PWA (Progressive Web App) 지원
향후 추가 예정:
- 오프라인 모드
- 앱 설치
- 푸시 알림

### 터치 제스처
- **탭**: 버튼 클릭
- **길게 누르기**: 도움말 표시
- **스와이프**: 화면 전환 (향후 추가)

## 🔧 문제 해결

### 일반적인 문제
1. **음성이 안 나와요**: 브라우저 설정에서 음성 허용
2. **화면이 작아요**: 글자 크기 슬라이더 조절
3. **터치가 안 돼요**: 버튼 크기를 "큰 터치" 모드로 변경
4. **언어가 안 바뀌어요**: 페이지 새로고침 후 다시 시도

### 브라우저 호환성
- **권장**: Chrome 90+, Safari 14+, Firefox 88+
- **모바일**: iOS Safari 14+, Chrome Mobile 90+

## 🚀 향후 계획

### Phase 2 기능
- [ ] PWA 지원
- [ ] 오프라인 모드
- [ ] 생체 인증 (지문, 얼굴)
- [ ] AI 음성 어시스턴트
- [ ] AR/VR 지원

이제 웹 브라우저에서도 완전한 배리어-프리 키오스크 경험을 제공합니다! 🎉