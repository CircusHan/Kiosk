"""WebSocket endpoints for real-time communication"""

import json
import logging
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

logger = logging.getLogger(__name__)

router = APIRouter()

# 연결된 WebSocket 클라이언트들 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_info: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """클라이언트 연결"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_info[client_id] = {
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "client_type": "kiosk"
        }
        logger.info(f"WebSocket client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        """클라이언트 연결 해제"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.client_info:
            del self.client_info[client_id]
        logger.info(f"WebSocket client disconnected: {client_id}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """특정 클라이언트에게 메시지 전송"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(json.dumps(message))
                    return True
                except Exception as e:
                    logger.error(f"Failed to send message to {client_id}: {e}")
                    self.disconnect(client_id)
        return False
    
    async def broadcast(self, message: dict):
        """모든 연결된 클라이언트에게 브로드캐스트"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
                else:
                    disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # 연결이 끊어진 클라이언트들 정리
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_to_type(self, message: dict, client_type: str):
        """특정 타입의 클라이언트들에게 전송"""
        for client_id, info in self.client_info.items():
            if info.get("client_type") == client_type:
                await self.send_personal_message(message, client_id)
    
    def get_connected_clients(self) -> Dict:
        """연결된 클라이언트 정보 반환"""
        return {
            "total": len(self.active_connections),
            "clients": self.client_info
        }

# 전역 연결 매니저
manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket 연결 엔드포인트"""
    await manager.connect(websocket, client_id)
    
    try:
        # 연결 확인 메시지 전송
        await manager.send_personal_message({
            "type": "connection_confirmed",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "message": "WebSocket 연결이 설정되었습니다."
        }, client_id)
        
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(message, client_id)
                
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "잘못된 JSON 형식입니다."
                }, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)


async def handle_websocket_message(message: dict, client_id: str):
    """WebSocket 메시지 처리"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # 연결 상태 확인
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }, client_id)
        
    elif message_type == "session_activity":
        # 세션 활동 업데이트
        if client_id in manager.client_info:
            manager.client_info[client_id]["last_activity"] = datetime.now().isoformat()
        
        await manager.send_personal_message({
            "type": "activity_acknowledged",
            "timestamp": datetime.now().isoformat()
        }, client_id)
        
    elif message_type == "queue_status_request":
        # 대기열 상태 요청
        department = message.get("department")
        queue_status = await get_queue_status(department)
        
        await manager.send_personal_message({
            "type": "queue_status_update",
            "department": department,
            "data": queue_status,
            "timestamp": datetime.now().isoformat()
        }, client_id)
        
    elif message_type == "help_request":
        # 도움 요청
        await handle_help_request(message, client_id)
        
    elif message_type == "screen_change":
        # 화면 변경 알림
        screen = message.get("screen")
        logger.info(f"Client {client_id} changed to screen: {screen}")
        
        # 관리자 클라이언트에게 알림 (있는 경우)
        await manager.send_to_type({
            "type": "client_screen_change", 
            "client_id": client_id,
            "screen": screen,
            "timestamp": datetime.now().isoformat()
        }, "admin")
        
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": f"알 수 없는 메시지 타입: {message_type}"
        }, client_id)


async def get_queue_status(department: str) -> dict:
    """대기열 상태 조회 (실제로는 데이터베이스에서 조회)"""
    # 모의 데이터 - 실제로는 app.services.reception을 사용
    import random
    
    return {
        "current_number": random.randint(1, 50),
        "waiting_count": random.randint(0, 20),
        "estimated_wait_time": random.randint(5, 45),
        "location": f"{department} - 2층 201호"
    }


async def handle_help_request(message: dict, client_id: str):
    """도움 요청 처리"""
    help_type = message.get("help_type", "general")
    location = message.get("location", "kiosk")
    
    # 관리자나 직원에게 알림 전송
    help_notification = {
        "type": "help_request",
        "client_id": client_id,
        "help_type": help_type,
        "location": location,
        "timestamp": datetime.now().isoformat(),
        "message": "키오스크에서 도움이 요청되었습니다."
    }
    
    # 관리자 클라이언트들에게 전송
    await manager.send_to_type(help_notification, "admin")
    
    # 요청자에게 확인 메시지
    await manager.send_personal_message({
        "type": "help_request_confirmed",
        "message": "도움 요청이 전달되었습니다. 직원이 곧 도움을 드리겠습니다.",
        "timestamp": datetime.now().isoformat()
    }, client_id)


# 관리자 기능: 브로드캐스트 메시지 전송
async def send_announcement(message: str, target_type: str = "all"):
    """공지사항 전송"""
    announcement = {
        "type": "announcement",
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "priority": "normal"
    }
    
    if target_type == "all":
        await manager.broadcast(announcement)
    else:
        await manager.send_to_type(announcement, target_type)


# 대기열 업데이트 전송
async def send_queue_update(department: str, queue_data: dict):
    """대기열 업데이트 전송"""
    queue_update = {
        "type": "queue_update",
        "department": department,
        "data": queue_data,
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.broadcast(queue_update)


# 긴급 알림 전송
async def send_emergency_alert(message: str):
    """긴급 알림 전송"""
    alert = {
        "type": "emergency_alert",
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "priority": "high"
    }
    
    await manager.broadcast(alert)


# WebSocket 상태 조회 엔드포인트
@router.get("/ws/status")
async def websocket_status():
    """WebSocket 연결 상태 조회"""
    return {
        "websocket_status": "active",
        "connections": manager.get_connected_clients()
    }


# 관리자용 브로드캐스트 엔드포인트
@router.post("/ws/broadcast")
async def broadcast_message(message: dict):
    """관리자용 브로드캐스트 메시지 전송"""
    # 실제로는 관리자 인증이 필요
    await manager.broadcast(message)
    return {"status": "message_sent", "recipients": len(manager.active_connections)}


# 개별 클라이언트에게 메시지 전송
@router.post("/ws/send/{client_id}")
async def send_to_client(client_id: str, message: dict):
    """특정 클라이언트에게 메시지 전송"""
    success = await manager.send_personal_message(message, client_id)
    return {"status": "sent" if success else "failed", "client_id": client_id}


# 시스템 알림 전송 함수들 (다른 모듈에서 호출용)
async def notify_appointment_called(patient_name: str, queue_number: int, department: str):
    """진료 호출 알림"""
    notification = {
        "type": "appointment_called",
        "patient_name": patient_name,
        "queue_number": queue_number,
        "department": department,
        "message": f"{queue_number}번 {patient_name}님, {department}로 오세요.",
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.broadcast(notification)


async def notify_system_maintenance(start_time: str, duration_minutes: int):
    """시스템 점검 알림"""
    notification = {
        "type": "system_maintenance",
        "start_time": start_time,
        "duration_minutes": duration_minutes,
        "message": f"시스템 점검이 {start_time}에 시작됩니다. 약 {duration_minutes}분 소요됩니다.",
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.broadcast(notification)


from datetime import datetime