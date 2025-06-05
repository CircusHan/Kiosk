/**
 * 다국어 지원 모듈
 */

class I18nManager {
    constructor() {
        this.currentLanguage = 'ko';
        this.fallbackLanguage = 'ko';
        this.translations = {};
        this.loadTranslations();
    }
    
    loadTranslations() {
        this.translations = {
            ko: {
                // 공통
                app_title: '보건소 키오스크',
                welcome: '환영합니다',
                select_service: '서비스를 선택해주세요',
                back: '뒤로',
                cancel: '취소',
                confirm: '확인',
                next: '다음',
                print: '출력',
                close: '닫기',
                loading: '처리 중...',
                
                // 메인 메뉴
                reception: '접수',
                reception_desc: '진료 접수 및 순번표 발급',
                payment: '수납',
                payment_desc: '진료비 결제',
                certificate: '증명서 발급',
                certificate_desc: '각종 의료 증명서',
                
                // 접수
                reception_title: '진료 접수',
                enter_patient_info: '환자 정보를 입력해주세요',
                name: '이름',
                birthdate: '생년월일',
                phone: '전화번호',
                select_symptoms: '증상을 선택해주세요',
                select_department: '진료과를 선택해주세요',
                queue_number: '대기번호',
                estimated_wait: '예상 대기시간',
                location: '위치',
                
                // 증상
                fever: '발열',
                cough: '기침',
                headache: '두통',
                stomachache: '복통',
                joint_pain: '관절통',
                skin_rash: '피부발진',
                depression: '우울감',
                pregnancy: '임신',
                fracture: '골절',
                breathing_difficulty: '호흡곤란',
                
                // 진료과
                internal_medicine: '내과',
                surgery: '외과',
                pediatrics: '소아과',
                obstetrics: '산부인과',
                orthopedics: '정형외과',
                dermatology: '피부과',
                psychiatry: '정신건강의학과',
                emergency: '응급실',
                
                // 접근성
                font_size: '글자 크기',
                high_contrast: '고대비',
                voice_guide: '음성안내',
                emergency_help: '도움요청',
                
                // 메시지
                reception_complete: '접수가 완료되었습니다!',
                timeout_warning: '30초 후 초기 화면으로 돌아갑니다',
                continue_use: '계속 사용하기',
                go_home: '홈으로 돌아가기',
                
                // 오류 메시지
                fill_required_fields: '모든 필수 정보를 입력해주세요',
                select_symptom: '최소 하나의 증상을 선택해주세요',
                invalid_phone: '올바른 전화번호를 입력해주세요',
                network_error: '네트워크 연결이 불안정합니다',
                
                // 음성 안내
                voice_welcome: '보건소 키오스크에 오신 것을 환영합니다. 서비스를 선택해주세요.',
                voice_reception: '진료 접수 화면입니다.',
                voice_payment: '진료비 수납 화면입니다.',
                voice_certificate: '증명서 발급 화면입니다.',
                voice_home: '홈 화면으로 돌아갑니다.',
                voice_timeout: '시간 초과로 초기 화면으로 돌아갑니다.',
                voice_help: '직원을 호출하고 있습니다. 잠시만 기다려주세요.'
            },
            
            en: {
                // Common
                app_title: 'Health Center Kiosk',
                welcome: 'Welcome',
                select_service: 'Please select a service',
                back: 'Back',
                cancel: 'Cancel',
                confirm: 'Confirm',
                next: 'Next',
                print: 'Print',
                close: 'Close',
                loading: 'Processing...',
                
                // Main menu
                reception: 'Reception',
                reception_desc: 'Medical reception and queue number',
                payment: 'Payment',
                payment_desc: 'Medical fee payment',
                certificate: 'Certificate',
                certificate_desc: 'Various medical certificates',
                
                // Reception
                reception_title: 'Medical Reception',
                enter_patient_info: 'Please enter patient information',
                name: 'Name',
                birthdate: 'Date of Birth',
                phone: 'Phone Number',
                select_symptoms: 'Please select symptoms',
                select_department: 'Please select department',
                queue_number: 'Queue Number',
                estimated_wait: 'Estimated Wait Time',
                location: 'Location',
                
                // Symptoms
                fever: 'Fever',
                cough: 'Cough',
                headache: 'Headache',
                stomachache: 'Stomachache',
                joint_pain: 'Joint Pain',
                skin_rash: 'Skin Rash',
                depression: 'Depression',
                pregnancy: 'Pregnancy',
                fracture: 'Fracture',
                breathing_difficulty: 'Breathing Difficulty',
                
                // Departments
                internal_medicine: 'Internal Medicine',
                surgery: 'Surgery',
                pediatrics: 'Pediatrics',
                obstetrics: 'Obstetrics',
                orthopedics: 'Orthopedics',
                dermatology: 'Dermatology',
                psychiatry: 'Psychiatry',
                emergency: 'Emergency',
                
                // Accessibility
                font_size: 'Font Size',
                high_contrast: 'High Contrast',
                voice_guide: 'Voice Guide',
                emergency_help: 'Emergency Help',
                
                // Messages
                reception_complete: 'Reception completed!',
                timeout_warning: 'Returning to home screen in 30 seconds',
                continue_use: 'Continue',
                go_home: 'Go Home',
                
                // Error messages
                fill_required_fields: 'Please fill in all required fields',
                select_symptom: 'Please select at least one symptom',
                invalid_phone: 'Please enter a valid phone number',
                network_error: 'Network connection is unstable',
                
                // Voice guidance
                voice_welcome: 'Welcome to the health center kiosk. Please select a service.',
                voice_reception: 'This is the medical reception screen.',
                voice_payment: 'This is the medical payment screen.',
                voice_certificate: 'This is the certificate issuance screen.',
                voice_home: 'Returning to home screen.',
                voice_timeout: 'Returning to home screen due to timeout.',
                voice_help: 'Calling staff for assistance. Please wait.'
            },
            
            zh: {
                // 常用
                app_title: '保健所自助服务机',
                welcome: '欢迎',
                select_service: '请选择服务',
                back: '返回',
                cancel: '取消',
                confirm: '确认',
                next: '下一步',
                print: '打印',
                close: '关闭',
                loading: '处理中...',
                
                // 主菜单
                reception: '挂号',
                reception_desc: '医疗挂号和排队号码',
                payment: '缴费',
                payment_desc: '医疗费用支付',
                certificate: '证明书',
                certificate_desc: '各种医疗证明书',
                
                // 挂号
                reception_title: '医疗挂号',
                enter_patient_info: '请输入患者信息',
                name: '姓名',
                birthdate: '出生日期',
                phone: '电话号码',
                select_symptoms: '请选择症状',
                select_department: '请选择科室',
                queue_number: '排队号码',
                estimated_wait: '预计等待时间',
                location: '位置',
                
                // 症状
                fever: '发热',
                cough: '咳嗽',
                headache: '头痛',
                stomachache: '腹痛',
                joint_pain: '关节痛',
                skin_rash: '皮疹',
                depression: '抑郁',
                pregnancy: '怀孕',
                fracture: '骨折',
                breathing_difficulty: '呼吸困难'
            },
            
            vi: {
                // Chung
                app_title: 'Kiosk Trung tâm Y tế',
                welcome: 'Chào mừng',
                select_service: 'Vui lòng chọn dịch vụ',
                back: 'Quay lại',
                cancel: 'Hủy',
                confirm: 'Xác nhận',
                next: 'Tiếp theo',
                print: 'In',
                close: 'Đóng',
                loading: 'Đang xử lý...',
                
                // Menu chính
                reception: 'Đăng ký',
                reception_desc: 'Đăng ký khám bệnh và số thứ tự',
                payment: 'Thanh toán',
                payment_desc: 'Thanh toán phí y tế',
                certificate: 'Giấy chứng nhận',
                certificate_desc: 'Các loại giấy chứng nhận y tế',
                
                // Đăng ký
                reception_title: 'Đăng ký khám bệnh',
                enter_patient_info: 'Vui lòng nhập thông tin bệnh nhân',
                name: 'Họ tên',
                birthdate: 'Ngày sinh',
                phone: 'Số điện thoại',
                select_symptoms: 'Vui lòng chọn triệu chứng',
                select_department: 'Vui lòng chọn khoa',
                queue_number: 'Số thứ tự',
                estimated_wait: 'Thời gian chờ dự kiến',
                location: 'Vị trí'
            }
        };
    }
    
    setLanguage(langCode) {
        if (this.translations[langCode]) {
            this.currentLanguage = langCode;
            this.updatePageTexts();
            this.saveLanguagePreference();
            
            // TTS 언어도 변경
            this.updateTTSLanguage();
        }
    }
    
    get(key, params = {}) {
        let text = this.translations[this.currentLanguage]?.[key] || 
                  this.translations[this.fallbackLanguage]?.[key] || 
                  key;
        
        // 매개변수 치환
        Object.keys(params).forEach(param => {
            text = text.replace(`{${param}}`, params[param]);
        });
        
        return text;
    }
    
    updatePageTexts() {
        // data-i18n 속성을 가진 모든 요소 업데이트
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = this.get(key);
        });
        
        // 특정 요소들 직접 업데이트
        this.updateSpecificElements();
    }
    
    updateSpecificElements() {
        // 메인 타이틀
        const mainTitle = document.querySelector('.main-title');
        if (mainTitle) {
            mainTitle.textContent = this.get('welcome');
        }
        
        // 서브타이틀
        const subtitle = document.querySelector('.subtitle');
        if (subtitle) {
            subtitle.textContent = this.get('select_service');
        }
        
        // 서비스 버튼들
        const serviceButtons = {
            'reception-btn': { title: 'reception', desc: 'reception_desc' },
            'payment-btn': { title: 'payment', desc: 'payment_desc' },
            'certificate-btn': { title: 'certificate', desc: 'certificate_desc' }
        };
        
        Object.entries(serviceButtons).forEach(([id, keys]) => {
            const button = document.getElementById(id);
            if (button) {
                const titleEl = button.querySelector('h2');
                const descEl = button.querySelector('p');
                if (titleEl) titleEl.textContent = this.get(keys.title);
                if (descEl) descEl.textContent = this.get(keys.desc);
            }
        });
        
        // 폼 라벨들
        const formLabels = {
            'patient-name': 'name',
            'patient-birth': 'birthdate',
            'patient-phone': 'phone'
        };
        
        Object.entries(formLabels).forEach(([inputId, key]) => {
            const input = document.getElementById(inputId);
            if (input) {
                const label = document.querySelector(`label[for="${inputId}"]`);
                if (label) {
                    label.textContent = this.get(key);
                }
            }
        });
        
        // 버튼들
        const buttons = document.querySelectorAll('.next-btn');
        buttons.forEach(btn => {
            btn.textContent = this.get('next');
        });
        
        const backBtns = document.querySelectorAll('.back-btn');
        backBtns.forEach(btn => {
            btn.innerHTML = `<i class="fas fa-arrow-left"></i> ${this.get('back')}`;
        });
        
        const completeBtns = document.querySelectorAll('.complete-btn');
        completeBtns.forEach(btn => {
            btn.textContent = this.get('go_home');
        });
        
        // 화면 제목들
        const screenTitles = {
            'reception-screen': 'reception_title',
            'payment-screen': 'payment',
            'certificate-screen': 'certificate'
        };
        
        Object.entries(screenTitles).forEach(([screenId, key]) => {
            const screen = document.getElementById(screenId);
            if (screen) {
                const title = screen.querySelector('.screen-header h1');
                if (title) {
                    title.textContent = this.get(key);
                }
            }
        });
    }
    
    updateTTSLanguage() {
        const languageMap = {
            'ko': 'ko-KR',
            'en': 'en-US',
            'zh': 'zh-CN',
            'vi': 'vi-VN'
        };
        
        // TTS 언어 설정 (app.js와 연동)
        if (window.app) {
            app.ttsLanguage = languageMap[this.currentLanguage] || 'ko-KR';
        }
    }
    
    saveLanguagePreference() {
        localStorage.setItem('kioskLanguage', this.currentLanguage);
    }
    
    loadLanguagePreference() {
        const saved = localStorage.getItem('kioskLanguage');
        if (saved && this.translations[saved]) {
            this.currentLanguage = saved;
            
            // 언어 선택기 업데이트
            const selector = document.getElementById('language-selector');
            if (selector) {
                selector.value = saved;
            }
        }
    }
    
    formatNumber(number) {
        // 언어별 숫자 형식
        const formatters = {
            'ko': new Intl.NumberFormat('ko-KR'),
            'en': new Intl.NumberFormat('en-US'),
            'zh': new Intl.NumberFormat('zh-CN'),
            'vi': new Intl.NumberFormat('vi-VN')
        };
        
        const formatter = formatters[this.currentLanguage] || formatters['ko'];
        return formatter.format(number);
    }
    
    formatCurrency(amount) {
        // 언어별 통화 형식
        const formatters = {
            'ko': new Intl.NumberFormat('ko-KR', { style: 'currency', currency: 'KRW' }),
            'en': new Intl.NumberFormat('en-US', { style: 'currency', currency: 'KRW' }),
            'zh': new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'KRW' }),
            'vi': new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'KRW' })
        };
        
        const formatter = formatters[this.currentLanguage] || formatters['ko'];
        return formatter.format(amount);
    }
    
    formatDate(date) {
        // 언어별 날짜 형식
        const formatters = {
            'ko': new Intl.DateTimeFormat('ko-KR'),
            'en': new Intl.DateTimeFormat('en-US'),
            'zh': new Intl.DateTimeFormat('zh-CN'),
            'vi': new Intl.DateTimeFormat('vi-VN')
        };
        
        const formatter = formatters[this.currentLanguage] || formatters['ko'];
        return formatter.format(date);
    }
    
    formatTime(date) {
        // 언어별 시간 형식
        const formatters = {
            'ko': new Intl.DateTimeFormat('ko-KR', { timeStyle: 'short' }),
            'en': new Intl.DateTimeFormat('en-US', { timeStyle: 'short' }),
            'zh': new Intl.DateTimeFormat('zh-CN', { timeStyle: 'short' }),
            'vi': new Intl.DateTimeFormat('vi-VN', { timeStyle: 'short' })
        };
        
        const formatter = formatters[this.currentLanguage] || formatters['ko'];
        return formatter.format(date);
    }
    
    getDirection() {
        // 텍스트 방향 (RTL 언어 지원을 위해)
        const rtlLanguages = ['ar', 'he', 'fa'];
        return rtlLanguages.includes(this.currentLanguage) ? 'rtl' : 'ltr';
    }
    
    pluralize(count, key) {
        // 복수형 처리 (언어별 규칙 적용)
        const pluralRules = {
            'ko': () => key, // 한국어는 복수형 없음
            'en': (n) => n === 1 ? key : `${key}s`,
            'zh': () => key, // 중국어는 복수형 없음
            'vi': () => key  // 베트남어는 복수형 없음
        };
        
        const rule = pluralRules[this.currentLanguage] || pluralRules['ko'];
        return rule(count);
    }
    
    // 접근성을 위한 언어별 설명
    getAccessibilityDescription(key) {
        const descriptions = {
            'ko': {
                'reception': '진료 접수 서비스입니다. 환자 정보를 입력하고 대기번호를 받을 수 있습니다.',
                'payment': '진료비 수납 서비스입니다. 현금, 카드, QR코드로 결제할 수 있습니다.',
                'certificate': '증명서 발급 서비스입니다. 진단서, 진료확인서, 접종증명서를 발급받을 수 있습니다.'
            },
            'en': {
                'reception': 'Medical reception service. You can enter patient information and receive a queue number.',
                'payment': 'Medical payment service. You can pay with cash, card, or QR code.',
                'certificate': 'Certificate issuance service. You can get medical certificates, treatment confirmations, and vaccination certificates.'
            }
        };
        
        return descriptions[this.currentLanguage]?.[key] || descriptions['ko']?.[key] || '';
    }
}

// 전역 i18n 인스턴스
let i18n;

document.addEventListener('DOMContentLoaded', () => {
    i18n = new I18nManager();
    
    // 저장된 언어 설정 로드
    i18n.loadLanguagePreference();
    
    // 초기 텍스트 업데이트
    i18n.updatePageTexts();
    
    // 언어 변경 이벤트 리스너
    const languageSelector = document.getElementById('language-selector');
    if (languageSelector) {
        languageSelector.addEventListener('change', (e) => {
            i18n.setLanguage(e.target.value);
        });
    }
});

// 외부 접근용
window.i18n = i18n;