/**
 * 배리어-프리 보건소 키오스크 - 메인 애플리케이션
 */

class KioskApp {
    constructor() {
        this.currentScreen = 'home';
        this.currentStep = 'patient-input';
        this.sessionData = {};
        this.idleTimer = null;
        this.warningTimer = null;
        this.sessionTimeout = 120; // 2분
        this.warningTime = 30; // 30초 전 경고
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.startSession();
        this.setupIdleTimer();
        this.initializeAccessibility();
        
        // 초기 음성 안내
        this.speak('보건소 키오스크에 오신 것을 환영합니다. 서비스를 선택해주세요.');
    }
    
    setupEventListeners() {
        // 서비스 버튼 이벤트
        document.getElementById('reception-btn').addEventListener('click', () => {
            this.showScreen('reception');
            this.speak('진료 접수 화면입니다.');
        });
        
        document.getElementById('payment-btn').addEventListener('click', () => {
            this.showScreen('payment');
            this.speak('진료비 수납 화면입니다.');
        });
        
        document.getElementById('certificate-btn').addEventListener('click', () => {
            this.showScreen('certificate');
            this.speak('증명서 발급 화면입니다.');
        });
        
        // 진료과 선택 이벤트
        document.querySelectorAll('.department-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const dept = e.currentTarget.dataset.dept;
                this.selectDepartment(dept);
            });
        });
        
        // 폼 이벤트
        document.querySelectorAll('input').forEach(input => {
            input.addEventListener('focus', () => this.resetIdleTimer());
            input.addEventListener('input', () => this.resetIdleTimer());
        });
        
        // 터치 이벤트
        document.addEventListener('touchstart', () => this.resetIdleTimer());
        document.addEventListener('click', () => this.resetIdleTimer());
        
        // 키보드 접근성
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
            this.resetIdleTimer();
        });
        
        // 증상 선택 이벤트
        document.querySelectorAll('.symptom-item input').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const symptom = e.target.value;
                const label = e.target.closest('.symptom-item');
                
                if (e.target.checked) {
                    label.classList.add('selected');
                    this.speak(`${this.getSymptomName(symptom)} 선택됨`);
                } else {
                    label.classList.remove('selected');
                    this.speak(`${this.getSymptomName(symptom)} 선택 해제됨`);
                }
            });
        });
    }
    
    showScreen(screenName) {
        // 현재 화면 숨기기
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // 새 화면 보이기
        const targetScreen = document.getElementById(`${screenName}-screen`);
        if (targetScreen) {
            targetScreen.classList.add('active');
            this.currentScreen = screenName;
            
            // 접수 화면인 경우 첫 번째 단계로 설정
            if (screenName === 'reception') {
                this.showStep('patient-input');
            }
        }
        
        this.resetIdleTimer();
        this.announceScreenChange(screenName);
    }
    
    showStep(stepName) {
        // 현재 단계 숨기기
        document.querySelectorAll('.step-content').forEach(step => {
            step.classList.remove('active');
        });
        
        // 새 단계 보이기
        const targetStep = document.getElementById(stepName === 'symptoms' ? 'symptoms-input' : 
                                                stepName === 'department' ? 'department-input' :
                                                stepName === 'confirmation' ? 'confirmation' : stepName);
        if (targetStep) {
            targetStep.classList.add('active');
            this.currentStep = stepName;
        }
        
        this.resetIdleTimer();
    }
    
    nextStep(nextStepName) {
        // 현재 단계 데이터 검증
        if (!this.validateCurrentStep()) {
            return;
        }
        
        // 데이터 저장
        this.saveStepData();
        
        // 다음 단계로 이동
        this.showStep(nextStepName);
        
        // 단계별 음성 안내
        switch(nextStepName) {
            case 'symptoms':
                this.speak('증상을 선택해주세요. 여러 개 선택 가능합니다.');
                break;
            case 'department':
                this.speak('진료과를 선택해주세요.');
                break;
            case 'confirmation':
                this.generateQueueNumber();
                this.speak('접수가 완료되었습니다.');
                break;
        }
    }
    
    validateCurrentStep() {
        switch(this.currentStep) {
            case 'patient-input':
                const name = document.getElementById('patient-name').value.trim();
                const birth = document.getElementById('patient-birth').value;
                const phone = document.getElementById('patient-phone').value.trim();
                
                if (!name || !birth || !phone) {
                    this.speak('모든 필수 정보를 입력해주세요.');
                    this.showError('모든 필수 정보를 입력해주세요.');
                    return false;
                }
                
                if (!this.validatePhone(phone)) {
                    this.speak('올바른 전화번호를 입력해주세요.');
                    this.showError('올바른 전화번호를 입력해주세요.');
                    return false;
                }
                break;
                
            case 'symptoms-input':
                const selectedSymptoms = document.querySelectorAll('.symptom-item input:checked');
                if (selectedSymptoms.length === 0) {
                    this.speak('최소 하나의 증상을 선택해주세요.');
                    this.showError('최소 하나의 증상을 선택해주세요.');
                    return false;
                }
                break;
        }
        return true;
    }
    
    saveStepData() {
        switch(this.currentStep) {
            case 'patient-input':
                this.sessionData.patient = {
                    name: document.getElementById('patient-name').value.trim(),
                    birth: document.getElementById('patient-birth').value,
                    phone: document.getElementById('patient-phone').value.trim()
                };
                break;
                
            case 'symptoms-input':
                this.sessionData.symptoms = Array.from(
                    document.querySelectorAll('.symptom-item input:checked')
                ).map(input => input.value);
                break;
        }
    }
    
    selectDepartment(deptCode) {
        this.sessionData.department = deptCode;
        
        // 진료과별 위치 정보
        const locations = {
            'internal': '내과 - 2층 201호',
            'surgery': '외과 - 3층 301호', 
            'pediatrics': '소아과 - 1층 101호',
            'orthopedics': '정형외과 - 2층 202호',
            'dermatology': '피부과 - 1층 102호',
            'emergency': '응급실 - 별관'
        };
        
        document.getElementById('dept-location').textContent = locations[deptCode] || '확인 중';
        
        this.nextStep('confirmation');
        this.speak(`${this.getDepartmentName(deptCode)}가 선택되었습니다.`);
    }
    
    generateQueueNumber() {
        // 대기번호 생성 (실제로는 서버에서 받아옴)
        const queueNum = Math.floor(Math.random() * 50) + 1;
        const waitTime = Math.floor(Math.random() * 30) + 10;
        
        document.getElementById('queue-num').textContent = queueNum;
        document.getElementById('wait-time').textContent = `약 ${waitTime}분`;
        
        // 서버에 접수 정보 전송
        this.submitReception(queueNum);
    }
    
    async submitReception(queueNum) {
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/reception/walk-in', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...this.sessionData,
                    queue_number: queueNum
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('접수 완료:', result);
            } else {
                console.error('접수 실패:', response.statusText);
            }
        } catch (error) {
            console.error('네트워크 오류:', error);
        } finally {
            this.showLoading(false);
        }
    }
    
    goHome() {
        this.showScreen('home');
        this.resetSession();
        this.speak('홈 화면으로 돌아갑니다.');
    }
    
    resetSession() {
        this.sessionData = {};
        this.currentStep = 'patient-input';
        
        // 폼 초기화
        document.querySelectorAll('input').forEach(input => {
            if (input.type === 'checkbox') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        
        // 선택 상태 초기화
        document.querySelectorAll('.selected').forEach(el => {
            el.classList.remove('selected');
        });
    }
    
    // 타이머 관리
    startSession() {
        const sessionId = 'session_' + Date.now();
        this.sessionData.id = sessionId;
        
        // 서버에 세션 시작 알림
        fetch('/api/session/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
    }
    
    setupIdleTimer() {
        this.resetIdleTimer();
    }
    
    resetIdleTimer() {
        // 기존 타이머 정리
        if (this.idleTimer) clearTimeout(this.idleTimer);
        if (this.warningTimer) clearTimeout(this.warningTimer);
        
        // 경고 타이머 설정 (30초 전)
        this.warningTimer = setTimeout(() => {
            this.showTimeoutWarning();
        }, (this.sessionTimeout - this.warningTime) * 1000);
        
        // 세션 타임아웃 설정
        this.idleTimer = setTimeout(() => {
            this.handleSessionTimeout();
        }, this.sessionTimeout * 1000);
        
        // 서버에 활동 알림
        if (this.sessionData.id) {
            fetch(`/api/session/activity/${this.sessionData.id}`, {
                method: 'POST'
            });
        }
    }
    
    showTimeoutWarning() {
        const modal = document.getElementById('timeout-modal');
        modal.classList.add('show');
        this.speak('30초 후 초기화됩니다. 계속 사용하시려면 화면을 터치해주세요.');
        
        // 5초 후 자동 닫기
        setTimeout(() => {
            if (modal.classList.contains('show')) {
                modal.classList.remove('show');
            }
        }, 5000);
    }
    
    resetTimeout() {
        const modal = document.getElementById('timeout-modal');
        modal.classList.remove('show');
        this.resetIdleTimer();
        this.speak('계속 이용하실 수 있습니다.');
    }
    
    handleSessionTimeout() {
        this.speak('시간 초과로 초기 화면으로 돌아갑니다.');
        this.goHome();
        
        // 서버에 세션 종료 알림
        if (this.sessionData.id) {
            fetch(`/api/session/end/${this.sessionData.id}`, {
                method: 'POST'
            });
        }
    }
    
    // 접근성 관련 메서드
    initializeAccessibility() {
        // 스크린 리더 지원
        this.setupScreenReader();
        
        // 키보드 네비게이션
        this.setupKeyboardNavigation();
        
        // 포커스 관리
        this.setupFocusManagement();
    }
    
    setupScreenReader() {
        // ARIA 라이브 영역 생성
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-announcement';
        document.body.appendChild(liveRegion);
        this.liveRegion = liveRegion;
    }
    
    announceToScreenReader(message) {
        if (this.liveRegion) {
            this.liveRegion.textContent = message;
        }
    }
    
    setupKeyboardNavigation() {
        // Tab 키 순서 관리
        const focusableElements = 'button, input, select, textarea, [tabindex]:not([tabindex="-1"])';
        
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.manageFocusOrder(e);
            }
        });
    }
    
    manageFocusOrder(e) {
        const currentScreen = document.querySelector('.screen.active');
        if (!currentScreen) return;
        
        const focusable = currentScreen.querySelectorAll('button:not([disabled]), input:not([disabled]), select:not([disabled])');
        const firstFocusable = focusable[0];
        const lastFocusable = focusable[focusable.length - 1];
        
        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                lastFocusable.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                firstFocusable.focus();
                e.preventDefault();
            }
        }
    }
    
    setupFocusManagement() {
        // 화면 전환 시 첫 번째 요소에 포커스
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    const target = mutation.target;
                    if (target.classList.contains('screen') && target.classList.contains('active')) {
                        const firstFocusable = target.querySelector('button, input, select');
                        if (firstFocusable) {
                            setTimeout(() => firstFocusable.focus(), 100);
                        }
                    }
                }
            });
        });
        
        document.querySelectorAll('.screen').forEach(screen => {
            observer.observe(screen, { attributes: true });
        });
    }
    
    handleKeyboardNavigation(e) {
        switch(e.key) {
            case 'Escape':
                if (this.currentScreen !== 'home') {
                    this.goHome();
                }
                break;
            case 'Enter':
                if (e.target.classList.contains('service-btn')) {
                    e.target.click();
                }
                break;
            case 'F1':
                e.preventDefault();
                this.showHelp();
                break;
        }
    }
    
    // 음성 안내 (TTS)
    speak(text) {
        if ('speechSynthesis' in window && accessibility.voiceEnabled) {
            // 기존 음성 중지
            speechSynthesis.cancel();
            
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = i18n.currentLanguage || 'ko-KR';
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 0.8;
            
            speechSynthesis.speak(utterance);
        }
        
        // 스크린 리더에도 알림
        this.announceToScreenReader(text);
    }
    
    // 유틸리티 메서드
    validatePhone(phone) {
        const phoneRegex = /^01[0-9]-?[0-9]{3,4}-?[0-9]{4}$/;
        return phoneRegex.test(phone.replace(/[^\d]/g, ''));
    }
    
    showError(message) {
        // 에러 메시지 표시 (향후 구현)
        console.error(message);
        
        // 접근성을 위한 알림
        this.announceToScreenReader(`오류: ${message}`);
    }
    
    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.remove('hidden');
            this.speak('처리 중입니다. 잠시만 기다려주세요.');
        } else {
            loading.classList.add('hidden');
        }
    }
    
    announceScreenChange(screenName) {
        const announcements = {
            'home': '홈 화면입니다. 원하는 서비스를 선택해주세요.',
            'reception': '진료 접수 화면입니다. 환자 정보를 입력해주세요.',
            'payment': '진료비 수납 화면입니다.',
            'certificate': '증명서 발급 화면입니다.'
        };
        
        const message = announcements[screenName] || `${screenName} 화면입니다.`;
        this.announceToScreenReader(message);
    }
    
    getSymptomName(code) {
        const symptoms = {
            'fever': '발열',
            'cough': '기침', 
            'headache': '두통',
            'stomachache': '복통',
            'joint-pain': '관절통',
            'skin-rash': '피부발진'
        };
        return symptoms[code] || code;
    }
    
    getDepartmentName(code) {
        const departments = {
            'internal': '내과',
            'surgery': '외과',
            'pediatrics': '소아과',
            'orthopedics': '정형외과',
            'dermatology': '피부과',
            'emergency': '응급실'
        };
        return departments[code] || code;
    }
    
    showHelp() {
        this.speak('도움이 필요하시면 직원을 호출해드리겠습니다.');
        // 실제로는 직원 호출 시스템 연동
        alert('직원이 곧 도움을 드리러 갑니다.');
    }
}

// 전역 함수들 (HTML에서 호출)
function nextStep(stepName) {
    app.nextStep(stepName);
}

function goHome() {
    app.goHome();
}

function resetTimeout() {
    app.resetTimeout();
}

// 앱 초기화
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new KioskApp();
});

// 전역 오류 처리
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    if (app) {
        app.speak('시스템 오류가 발생했습니다. 처음부터 다시 시도해주세요.');
        app.goHome();
    }
});

// 연결 상태 모니터링
window.addEventListener('online', () => {
    console.log('네트워크 연결됨');
});

window.addEventListener('offline', () => {
    console.log('네트워크 연결 끊어짐');
    if (app) {
        app.speak('네트워크 연결이 불안정합니다.');
    }
});