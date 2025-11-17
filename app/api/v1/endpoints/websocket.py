"""
WebSocket Endpoints
Maneja conexiones WebSocket para notificaciones en tiempo real
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.core.websocket import manager
from app.core.security import decode_access_token
from app.crud import user as crud_user
from app.models.user import UserRole

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token de autenticación"),
    db: Session = Depends(get_db)
):
    """
    Endpoint WebSocket para notificaciones en tiempo real
    
    **Autenticación:**
    Se debe enviar el token JWT como query parameter:
    `ws://localhost:8000/api/v1/ws?token=eyJ0eXAiOiJKV1QiLCJhb...`
    
    **Eventos que se reciben:**
    - `new_rma`: Se creó un nuevo RMA
    - `rma_status_changed`: Cambió el estado de un RMA
    
    **Formato de mensaje:**
    ```json
    {
        "type": "new_rma",
        "data": {
            "id": 123,
            "rma_number": "RMA-MX-2024-001",
            "status": "PENDING",
            ...
        },
        "timestamp": "2024-11-13T10:30:00Z"
    }
    ```
    
    **Permisos:**
    - SUPERADMIN: Recibe notificaciones de TODOS los RMAs
    - ADMIN: Recibe notificaciones de RMAs de su(s) país(es)
    - USER: Recibe notificaciones de RMAs de su(s) país(es)
    """
    
    # Decodificar token y obtener usuario
    try:
        payload = decode_access_token(token)
        if payload is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        user_id: int = payload.get("sub")
        if user_id is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Obtener usuario de la base de datos
        user = crud_user.get(db, id=user_id)
        if not user or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Obtener IDs de países del usuario
        country_ids = [country.id for country in user.countries]
        
        # Conectar WebSocket
        await manager.connect(websocket, user.role, country_ids)
        
        try:
            # Enviar mensaje de confirmación de conexión
            await manager.send_personal_message({
                "type": "connection_established",
                "message": f"Conectado como {user.role}",
                "user_id": user.id,
                "role": user.role,
                "countries": [{"id": c.id, "name": c.name} for c in user.countries]
            }, websocket)
            
            # Mantener la conexión abierta y escuchar mensajes
            while True:
                # Recibir mensajes del cliente (por si quieren implementar ping/pong)
                data = await websocket.receive_text()
                
                # Responder a ping
                if data == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": None
                    }, websocket)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket, user.role, country_ids)
            logger.info(f"WebSocket disconnected: user_id={user.id}, role={user.role}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass
