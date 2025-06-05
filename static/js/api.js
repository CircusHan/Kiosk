/**
 * API 통신 모듈
 */

class ApiClient {
    constructor() {
        this.baseURL = '/api';
        this.timeout = 10000; // 10초
        this.retryCount = 3;
        this.sessionId = null;
    }
    
    // HTTP 요청 헬퍼
    async request(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            signal: controller.signal,
            ...options
        };
        
        try {
            const response = await fetch(`${this.baseURL}${url}`, defaultOptions);
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('요청 시간이 초과되었습니다.');
            }
            
            throw error;
        }
    }
    
    // GET 요청
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        
        return this.request(fullUrl, { method: 'GET' });
    }
    
    // POST 요청
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // PUT 요청
    async put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    // DELETE 요청
    async delete(url) {
        return this.request(url, { method: 'DELETE' });
    }
    
    // 재시도 로직이 있는 요청
    async requestWithRetry(url, options, retries = this.retryCount) {
        try {
            return await this.request(url, options);
        } catch (error) {
            if (retries > 0 && this.shouldRetry(error)) {
                console.warn(`요청 실패, ${retries}번 재시도 중...`, error.message);
                await this.delay(1000);
                return this.requestWithRetry(url, options, retries - 1);
            }
            throw error;
        }
    }
    
    shouldRetry(error) {
        // 네트워크 오류나 서버 오류인 경우 재시도
        return error.message.includes('Failed to fetch') ||
               error.message.includes('HTTP 5') ||
               error.message.includes('시간이 초과');
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // 세션 관리
    async startSession() {
        try {
            const response = await this.post('/session/start');
            this.sessionId = response.session_id;
            return response;
        } catch (error) {
            console.error('세션 시작 실패:', error);
            throw error;
        }
    }
    
    async updateActivity() {
        if (!this.sessionId) return;
        
        try {
            await this.post(`/session/activity/${this.sessionId}`);
        } catch (error) {
            console.error('활동 업데이트 실패:', error);
        }
    }
    
    async endSession() {
        if (!this.sessionId) return;
        
        try {
            await this.post(`/session/end/${this.sessionId}`);
            this.sessionId = null;
        } catch (error) {
            console.error('세션 종료 실패:', error);
        }
    }
    
    async getSessionStatus() {
        if (!this.sessionId) return null;
        
        try {
            return await this.get(`/session/status/${this.sessionId}`);
        } catch (error) {
            console.error('세션 상태 조회 실패:', error);
            return null;
        }
    }
    
    // 접수 관련 API
    async searchPatient(phone = null, cardUid = null) {
        const params = {};
        if (phone) params.phone = phone;
        if (cardUid) params.card_uid = cardUid;
        
        try {
            return await this.get('/reception/patient/search', params);
        } catch (error) {
            if (error.message.includes('404')) {
                return null; // 환자를 찾지 못함
            }
            throw error;
        }
    }
    
    async createPatient(patientData) {
        return this.post('/reception/patient', patientData);
    }
    
    async getPatientAppointments(patientId, date = null) {
        const params = { patient_id: patientId };
        if (date) params.date = date;
        
        return this.get(`/reception/appointments/${patientId}`, params);
    }
    
    async createWalkInAppointment(patientId, symptoms, department = null) {
        return this.post('/reception/walk-in', {
            patient_id: patientId,
            symptoms: symptoms,
            department: department
        });
    }
    
    async checkInAppointment(patientId, appointmentId) {
        return this.post('/reception/check-in', {
            patient_id: patientId,
            appointment_id: appointmentId
        });
    }
    
    async getQueueStatus(department) {
        return this.get(`/reception/queue-status/${department}`);
    }
    
    async getDepartments() {
        return this.get('/reception/departments');
    }
    
    async getSymptoms() {
        return this.get('/reception/symptoms');
    }
    
    // 결제 관련 API
    async processPayment(patientId, amount, method, transactionData = null) {
        return this.post('/payment/process', {
            patient_id: patientId,
            amount: amount,
            method: method,
            transaction_data: transactionData
        });
    }
    
    async getPendingPayments(patientId) {
        return this.get(`/payment/pending/${patientId}`);
    }
    
    async getPaymentHistory(patientId, limit = 10) {
        return this.get(`/payment/history/${patientId}`, { limit });
    }
    
    async getPaymentMethods() {
        return this.get('/payment/methods');
    }
    
    async getReceipt(paymentId) {
        return this.get(`/payment/receipt/${paymentId}`);
    }
    
    // 증명서 관련 API
    async issueCertificate(certificateData, paymentMethod = null) {
        const data = { ...certificateData };
        if (paymentMethod) {
            data.payment_method = paymentMethod;
        }
        
        return this.post('/certificate/issue', data);
    }
    
    async getCertificateTypes() {
        return this.get('/certificate/types');
    }
    
    async getPatientCertificates(patientId) {
        return this.get(`/certificate/patient/${patientId}`);
    }
    
    async downloadCertificate(certificateId) {
        // 파일 다운로드의 경우 별도 처리
        const url = `${this.baseURL}/certificate/download/${certificateId}`;
        window.open(url, '_blank');
    }
    
    async verifyCertificate(certificateId) {
        return this.get(`/certificate/verify/${certificateId}`);
    }
    
    async reprintCertificate(certificateId) {
        return this.post(`/certificate/reprint/${certificateId}`);
    }
    
    // 도움 요청 API
    async requestHelp(type = 'assistance', location = 'kiosk') {
        return this.post('/help/request', {
            type: type,
            location: location,
            timestamp: new Date().toISOString(),
            session_id: this.sessionId
        });
    }
    
    // 관리자 API (인증 필요)
    async getStatistics(authToken) {
        return this.request('/admin/stats', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
    }
    
    async getDeviceLogs(authToken, limit = 100, level = null) {
        const params = { limit };
        if (level) params.level = level;
        
        return this.request('/admin/logs', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
    }
    
    // 오프라인 지원
    async queueOfflineRequest(url, options) {
        const request = {
            id: Date.now(),
            url: url,
            options: options,
            timestamp: new Date().toISOString()
        };
        
        // IndexedDB나 localStorage에 저장
        const offlineQueue = JSON.parse(localStorage.getItem('offlineQueue') || '[]');
        offlineQueue.push(request);
        localStorage.setItem('offlineQueue', JSON.stringify(offlineQueue));
        
        console.log('오프라인 요청 큐에 추가:', request);
    }
    
    async processOfflineQueue() {
        const offlineQueue = JSON.parse(localStorage.getItem('offlineQueue') || '[]');
        const processedRequests = [];
        
        for (const request of offlineQueue) {
            try {
                await this.request(request.url, request.options);
                processedRequests.push(request);
                console.log('오프라인 요청 처리 완료:', request.id);
            } catch (error) {
                console.error('오프라인 요청 처리 실패:', request.id, error);
                // 실패한 요청은 큐에 유지
            }
        }
        
        // 처리된 요청들을 큐에서 제거
        const remainingQueue = offlineQueue.filter(
            req => !processedRequests.find(processed => processed.id === req.id)
        );
        localStorage.setItem('offlineQueue', JSON.stringify(remainingQueue));
    }
    
    // 네트워크 상태 모니터링
    setupNetworkMonitoring() {
        window.addEventListener('online', () => {
            console.log('네트워크 연결됨');
            this.processOfflineQueue();
        });
        
        window.addEventListener('offline', () => {
            console.log('네트워크 연결 끊어짐');
        });
    }
    
    // 오류 처리 헬퍼
    handleError(error, context = '') {
        console.error(`API 오류 (${context}):`, error);
        
        let userMessage = '서비스 이용 중 오류가 발생했습니다.';
        
        if (error.message.includes('시간이 초과')) {
            userMessage = '요청 시간이 초과되었습니다. 다시 시도해주세요.';
        } else if (error.message.includes('Failed to fetch')) {
            userMessage = '네트워크 연결을 확인해주세요.';
        } else if (error.message.includes('HTTP 404')) {
            userMessage = '요청한 정보를 찾을 수 없습니다.';
        } else if (error.message.includes('HTTP 400')) {
            userMessage = '입력 정보를 확인해주세요.';
        } else if (error.message.includes('HTTP 5')) {
            userMessage = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        }
        
        // 사용자에게 알림
        if (window.app && window.app.speak) {
            app.speak(userMessage);
        }
        
        return userMessage;
    }
    
    // 캐시 관리
    setupCache() {
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5분
    }
    
    async getCached(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        return null;
    }
    
    setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }
    
    clearCache() {
        this.cache.clear();
    }
}

// WebSocket 클래스
class WebSocketClient {
    constructor(url = null) {
        this.url = url || `ws://${window.location.host}/ws`;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.listeners = new Map();
    }
    
    connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                console.log('WebSocket 연결됨');
                this.reconnectAttempts = 0;
                this.emit('connected');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.emit('message', data);
                    
                    // 특정 타입별 이벤트 발생
                    if (data.type) {
                        this.emit(data.type, data);
                    }
                } catch (error) {
                    console.error('WebSocket 메시지 파싱 오류:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket 연결 끊어짐');
                this.emit('disconnected');
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket 오류:', error);
                this.emit('error', error);
            };
            
        } catch (error) {
            console.error('WebSocket 연결 실패:', error);
            this.attemptReconnect();
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket이 연결되지 않음');
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`WebSocket 재연결 시도 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('WebSocket 재연결 실패');
        }
    }
    
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }
    
    off(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }
    
    emit(event, data = null) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`WebSocket 이벤트 처리 오류 (${event}):`, error);
                }
            });
        }
    }
}

// 전역 API 클라이언트 인스턴스
let api;
let wsClient;

document.addEventListener('DOMContentLoaded', () => {
    api = new ApiClient();
    api.setupCache();
    api.setupNetworkMonitoring();
    
    // WebSocket 연결 (선택적)
    if (window.location.protocol !== 'file:') {
        wsClient = new WebSocketClient();
        
        // 실시간 업데이트 처리
        wsClient.on('queue_update', (data) => {
            console.log('대기열 업데이트:', data);
            // UI 업데이트
        });
        
        wsClient.on('announcement', (data) => {
            console.log('공지사항:', data);
            if (window.app && window.app.speak) {
                app.speak(data.message);
            }
        });
        
        wsClient.connect();
    }
});

// 전역 접근
window.api = api;
window.wsClient = wsClient;