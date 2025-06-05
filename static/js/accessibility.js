/**
 * 접근성 관리 모듈
 */

class AccessibilityManager {
    constructor() {
        this.settings = {
            fontSize: 16,
            highContrast: false,
            voiceEnabled: true,
            colorblindMode: 'none',
            largeTouch: false,
            simplifiedUI: false,
            enhancedFocus: false
        };
        
        this.init();
    }
    
    init() {
        this.loadSettings();
        this.setupControls();
        this.applySettings();
        this.setupColorblindFilters();
    }
    
    loadSettings() {
        // 로컬 스토리지에서 설정 로드
        const savedSettings = localStorage.getItem('kioskAccessibilitySettings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
        
        // 시스템 설정 감지
        this.detectSystemPreferences();
    }
    
    saveSettings() {
        localStorage.setItem('kioskAccessibilitySettings', JSON.stringify(this.settings));
    }
    
    detectSystemPreferences() {
        // 고대비 모드 감지
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            this.settings.highContrast = true;
        }
        
        // 다크 모드 감지
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('dark-mode');
        }
        
        // 애니메이션 줄이기 감지
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.body.classList.add('reduced-motion');
        }
        
        // 투명도 줄이기 감지
        if (window.matchMedia('(prefers-reduced-transparency: reduce)').matches) {
            document.body.classList.add('reduced-transparency');
        }
    }
    
    setupControls() {
        // 글자 크기 조절
        const fontSlider = document.getElementById('font-slider');
        const fontDecrease = document.getElementById('font-decrease');
        const fontIncrease = document.getElementById('font-increase');
        
        if (fontSlider) {
            fontSlider.value = this.settings.fontSize;
            fontSlider.addEventListener('input', (e) => {
                this.changeFontSize(parseInt(e.target.value));
            });
        }
        
        if (fontDecrease) {
            fontDecrease.addEventListener('click', () => {
                this.changeFontSize(Math.max(12, this.settings.fontSize - 2));
            });
        }
        
        if (fontIncrease) {
            fontIncrease.addEventListener('click', () => {
                this.changeFontSize(Math.min(24, this.settings.fontSize + 2));
            });
        }
        
        // 고대비 모드
        const contrastToggle = document.getElementById('contrast-toggle');
        if (contrastToggle) {
            contrastToggle.addEventListener('click', () => {
                this.toggleHighContrast();
            });
        }
        
        // 음성 안내
        const voiceToggle = document.getElementById('voice-toggle');
        if (voiceToggle) {
            voiceToggle.addEventListener('click', () => {
                this.toggleVoice();
            });
        }
        
        // 언어 변경
        const languageSelector = document.getElementById('language-selector');
        if (languageSelector) {
            languageSelector.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }
        
        // 도움 요청
        const helpBtn = document.getElementById('help-btn');
        if (helpBtn) {
            helpBtn.addEventListener('click', () => {
                this.requestHelp();
            });
        }
        
        // 키보드 단축키
        this.setupKeyboardShortcuts();
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + 조합
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '=':
                    case '+':
                        e.preventDefault();
                        this.changeFontSize(Math.min(24, this.settings.fontSize + 2));
                        break;
                    case '-':
                        e.preventDefault();
                        this.changeFontSize(Math.max(12, this.settings.fontSize - 2));
                        break;
                    case '0':
                        e.preventDefault();
                        this.changeFontSize(16);
                        break;
                }
            }
            
            // Alt 조합
            if (e.altKey) {
                switch(e.key) {
                    case 'c':
                        e.preventDefault();
                        this.toggleHighContrast();
                        break;
                    case 'v':
                        e.preventDefault();
                        this.toggleVoice();
                        break;
                    case 'h':
                        e.preventDefault();
                        this.requestHelp();
                        break;
                }
            }
        });
    }
    
    changeFontSize(size) {
        this.settings.fontSize = size;
        document.documentElement.style.setProperty('--font-size-base', `${size}px`);
        document.documentElement.style.setProperty('--font-size-large', `${size * 1.5}px`);
        document.documentElement.style.setProperty('--font-size-xlarge', `${size * 2}px`);
        
        // 슬라이더 업데이트
        const fontSlider = document.getElementById('font-slider');
        if (fontSlider) {
            fontSlider.value = size;
        }
        
        // 큰 텍스트 모드 클래스 적용
        document.body.classList.toggle('large-text', size > 18);
        
        this.saveSettings();
        this.announceChange(`글자 크기가 ${size}포인트로 변경되었습니다.`);
    }
    
    toggleHighContrast() {
        this.settings.highContrast = !this.settings.highContrast;
        document.body.classList.toggle('high-contrast', this.settings.highContrast);
        
        const button = document.getElementById('contrast-toggle');
        if (button) {
            button.classList.toggle('active', this.settings.highContrast);
        }
        
        this.saveSettings();
        this.announceChange(this.settings.highContrast ? '고대비 모드가 켜졌습니다.' : '고대비 모드가 꺼졌습니다.');
    }
    
    toggleVoice() {
        this.settings.voiceEnabled = !this.settings.voiceEnabled;
        
        const button = document.getElementById('voice-toggle');
        if (button) {
            button.classList.toggle('active', this.settings.voiceEnabled);
            const icon = button.querySelector('i');
            if (icon) {
                icon.className = this.settings.voiceEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
            }
        }
        
        this.saveSettings();
        
        if (this.settings.voiceEnabled) {
            this.speak('음성 안내가 켜졌습니다.');
        } else {
            // 음성이 꺼지기 전에 마지막 안내
            this.speak('음성 안내가 꺼졌습니다.');
        }
    }
    
    changeLanguage(langCode) {
        if (window.i18n) {
            i18n.setLanguage(langCode);
            this.announceChange(`언어가 변경되었습니다.`);
            
            // 페이지 새로고침 없이 텍스트 업데이트
            this.updateTexts();
        }
    }
    
    updateTexts() {
        // 모든 텍스트 요소 업데이트 (i18n.js와 연동)
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (window.i18n && i18n.get) {
                element.textContent = i18n.get(key);
            }
        });
    }
    
    toggleColorblindMode(mode) {
        this.settings.colorblindMode = mode;
        
        // 기존 색맹 모드 클래스 제거
        document.body.classList.remove('colorblind-protanopia', 'colorblind-deuteranopia', 'colorblind-tritanopia');
        
        // 새 모드 적용
        if (mode !== 'none') {
            document.body.classList.add(`colorblind-${mode}`);
        }
        
        this.saveSettings();
        this.announceChange(`색맹 모드가 ${mode === 'none' ? '해제' : '설정'}되었습니다.`);
    }
    
    setupColorblindFilters() {
        // SVG 필터 생성
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'colorblind-filters');
        svg.innerHTML = `
            <defs>
                <filter id="protanopia-filter">
                    <feColorMatrix type="matrix" values="0.567,0.433,0,0,0 0.558,0.442,0,0,0 0,0.242,0.758,0,0 0,0,0,1,0"/>
                </filter>
                <filter id="deuteranopia-filter">
                    <feColorMatrix type="matrix" values="0.625,0.375,0,0,0 0.7,0.3,0,0,0 0,0.3,0.7,0,0 0,0,0,1,0"/>
                </filter>
                <filter id="tritanopia-filter">
                    <feColorMatrix type="matrix" values="0.95,0.05,0,0,0 0,0.433,0.567,0,0 0,0.475,0.525,0,0 0,0,0,1,0"/>
                </filter>
            </defs>
        `;
        document.body.appendChild(svg);
    }
    
    toggleLargeTouch() {
        this.settings.largeTouch = !this.settings.largeTouch;
        document.body.classList.toggle('large-touch', this.settings.largeTouch);
        this.saveSettings();
        this.announceChange(this.settings.largeTouch ? '큰 터치 영역 모드가 켜졌습니다.' : '큰 터치 영역 모드가 꺼졌습니다.');
    }
    
    toggleSimplifiedUI() {
        this.settings.simplifiedUI = !this.settings.simplifiedUI;
        document.body.classList.toggle('simplified', this.settings.simplifiedUI);
        this.saveSettings();
        this.announceChange(this.settings.simplifiedUI ? '간소화된 인터페이스 모드가 켜졌습니다.' : '일반 인터페이스 모드로 변경되었습니다.');
    }
    
    toggleEnhancedFocus() {
        this.settings.enhancedFocus = !this.settings.enhancedFocus;
        document.body.classList.toggle('enhanced-focus', this.settings.enhancedFocus);
        this.saveSettings();
        this.announceChange(this.settings.enhancedFocus ? '강화된 포커스 표시가 켜졌습니다.' : '일반 포커스 표시로 변경되었습니다.');
    }
    
    applySettings() {
        // 모든 설정 적용
        this.changeFontSize(this.settings.fontSize);
        
        if (this.settings.highContrast) {
            document.body.classList.add('high-contrast');
            const button = document.getElementById('contrast-toggle');
            if (button) button.classList.add('active');
        }
        
        if (!this.settings.voiceEnabled) {
            const button = document.getElementById('voice-toggle');
            if (button) {
                button.classList.remove('active');
                const icon = button.querySelector('i');
                if (icon) icon.className = 'fas fa-volume-mute';
            }
        }
        
        if (this.settings.colorblindMode !== 'none') {
            this.toggleColorblindMode(this.settings.colorblindMode);
        }
        
        if (this.settings.largeTouch) {
            document.body.classList.add('large-touch');
        }
        
        if (this.settings.simplifiedUI) {
            document.body.classList.add('simplified');
        }
        
        if (this.settings.enhancedFocus) {
            document.body.classList.add('enhanced-focus');
        }
    }
    
    requestHelp() {
        this.speak('직원을 호출하고 있습니다. 잠시만 기다려주세요.');
        
        // 실제 구현에서는 직원 호출 시스템과 연동
        this.showHelpModal();
        
        // 서버에 도움 요청 전송
        fetch('/api/help/request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                timestamp: new Date().toISOString(),
                location: 'kiosk',
                type: 'assistance'
            })
        }).catch(console.error);
    }
    
    showHelpModal() {
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.innerHTML = `
            <div class="modal-content">
                <h2><i class="fas fa-phone"></i> 도움 요청</h2>
                <p>직원이 곧 도움을 드리러 갑니다.<br>잠시만 기다려주세요.</p>
                <button onclick="this.closest('.modal').remove()" class="modal-btn">확인</button>
            </div>
        `;
        document.body.appendChild(modal);
        
        // 10초 후 자동 닫기
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 10000);
    }
    
    speak(text) {
        if (this.settings.voiceEnabled && window.app) {
            app.speak(text);
        }
    }
    
    announceChange(message) {
        this.speak(message);
        
        // 시각적 피드백도 제공
        this.showAccessibilityFeedback(message);
    }
    
    showAccessibilityFeedback(message) {
        const feedback = document.createElement('div');
        feedback.className = 'accessibility-feedback';
        feedback.textContent = message;
        feedback.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--primary-color);
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            z-index: 1000;
            animation: fadeInOut 3s ease-in-out;
        `;
        
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 3000);
    }
    
    // 터치 피드백
    addTouchFeedback(element) {
        element.classList.add('touch-feedback');
        
        element.addEventListener('touchstart', (e) => {
            if ('vibrate' in navigator) {
                navigator.vibrate(50); // 50ms 진동
            }
        });
    }
    
    // 모든 버튼에 터치 피드백 추가
    setupTouchFeedback() {
        document.querySelectorAll('button, .service-btn, .symptom-item, .department-btn').forEach(element => {
            this.addTouchFeedback(element);
        });
    }
    
    // 접근성 리포트 생성
    generateAccessibilityReport() {
        const report = {
            timestamp: new Date().toISOString(),
            settings: this.settings,
            systemPreferences: {
                highContrast: window.matchMedia('(prefers-contrast: high)').matches,
                reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
                darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches
            },
            screenReader: {
                available: 'speechSynthesis' in window,
                voices: speechSynthesis ? speechSynthesis.getVoices().length : 0
            },
            touch: {
                supported: 'ontouchstart' in window,
                vibrationSupported: 'vibrate' in navigator
            }
        };
        
        return report;
    }
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateX(100%); }
        20% { opacity: 1; transform: translateX(0); }
        80% { opacity: 1; transform: translateX(0); }
        100% { opacity: 0; transform: translateX(100%); }
    }
`;
document.head.appendChild(style);

// 전역 접근성 매니저 인스턴스
let accessibility;

document.addEventListener('DOMContentLoaded', () => {
    accessibility = new AccessibilityManager();
    
    // 터치 피드백 설정
    accessibility.setupTouchFeedback();
    
    // 접근성 리포트 로깅
    console.log('Accessibility Report:', accessibility.generateAccessibilityReport());
});

// 외부에서 접근 가능하도록 전역 객체에 추가
window.accessibility = accessibility;