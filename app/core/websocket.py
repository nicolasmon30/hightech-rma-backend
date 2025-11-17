"""
WebSocket Connection Manager
Gestiona conexiones WebSocket activas y broadcasting de mensajes
"""
from typing import Dict, List
from fastapi import WebSocket
from app.models.user import UserRole
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gestiona las conexiones WebSocket activas organizadas por roles de usuario
    
    Estructura:
    {
        "superadmin": [websocket1, websocket2, ...],
        "admin": [websocket3, websocket4, ...],
        "user": [websocket5, websocket6, ...]
    }
    """
    
    def __init__(self):
        # Conexiones activas organizadas por rol y country_id
        self.active_connections: Dict[str, List[WebSocket]] = {
            UserRole.SUPERADMIN: [],
            UserRole.ADMIN: [],
            UserRole.USER: []
        }
        
        # Conexiones organizadas por país para admins/users
        # country_connections[country_id] = [websocket1, websocket2, ...]
        self.country_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(
        self, 
        websocket: WebSocket, 
        role: UserRole, 
        country_ids: List[int] = None
    ):
        """
        Acepta una nueva conexión WebSocket y la registra
        
        Args:
            websocket: La conexión WebSocket
            role: Rol del usuario (superadmin, admin, user)
            country_ids: Lista de IDs de países del usuario (para admin/user)
        """
        await websocket.accept()
        
        # Agregar a la lista de conexiones por rol
        if role not in self.active_connections:
            self.active_connections[role] = []
        self.active_connections[role].append(websocket)
        
        # Agregar a conexiones por país (para admins y users)
        if country_ids and role in [UserRole.ADMIN, UserRole.USER]:
            for country_id in country_ids:
                if country_id not in self.country_connections:
                    self.country_connections[country_id] = []
                self.country_connections[country_id].append(websocket)
        
        logger.info(f"WebSocket connected: role={role}, countries={country_ids}")
    
    def disconnect(
        self, 
        websocket: WebSocket, 
        role: UserRole, 
        country_ids: List[int] = None
    ):
        """
        Desconecta un WebSocket y lo elimina de todas las listas
        
        Args:
            websocket: La conexión WebSocket a desconectar
            role: Rol del usuario
            country_ids: Lista de IDs de países del usuario
        """
        # Remover de conexiones por rol
        if role in self.active_connections and websocket in self.active_connections[role]:
            self.active_connections[role].remove(websocket)
        
        # Remover de conexiones por país
        if country_ids:
            for country_id in country_ids:
                if country_id in self.country_connections and websocket in self.country_connections[country_id]:
                    self.country_connections[country_id].remove(websocket)
        
        logger.info(f"WebSocket disconnected: role={role}, countries={country_ids}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Envía un mensaje a una conexión WebSocket específica
        
        Args:
            message: Diccionario con el mensaje
            websocket: La conexión WebSocket destino
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_role(self, message: dict, role: UserRole):
        """
        Envía un mensaje a todos los usuarios con un rol específico
        
        Args:
            message: Diccionario con el mensaje
            role: Rol de los destinatarios
        """
        if role not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[role]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to role {role}: {e}")
                disconnected.append(connection)
        
        # Limpiar conexiones muertas
        for conn in disconnected:
            if conn in self.active_connections[role]:
                self.active_connections[role].remove(conn)
    
    async def broadcast_to_country(self, message: dict, country_id: int):
        """
        Envía un mensaje a todos los usuarios de un país específico
        
        Args:
            message: Diccionario con el mensaje
            country_id: ID del país
        """
        if country_id not in self.country_connections:
            return
        
        disconnected = []
        for connection in self.country_connections[country_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to country {country_id}: {e}")
                disconnected.append(connection)
        
        # Limpiar conexiones muertas
        for conn in disconnected:
            if conn in self.country_connections[country_id]:
                self.country_connections[country_id].remove(conn)
    
    async def notify_new_rma(self, rma_data: dict, country_id: int):
        """
        Notifica sobre un nuevo RMA creado
        
        Envía notificación a:
        - Todos los SUPERADMIN (ven todos los RMAs)
        - Todos los ADMIN del país del RMA
        
        Args:
            rma_data: Datos del RMA creado (serializado)
            country_id: ID del país del RMA
        """
        message = {
            "type": "new_rma",
            "data": rma_data,
            "timestamp": rma_data.get("created_at")
        }
        
        # Notificar a todos los superadmins
        await self.broadcast_to_role(message, UserRole.SUPERADMIN)
        
        # Notificar a admins del país
        await self.broadcast_to_country(message, country_id)
        
        logger.info(f"New RMA notification sent: RMA ID={rma_data.get('id')}, Country={country_id}")
    
    async def notify_rma_status_change(self, rma_data: dict, country_id: int):
        """
        Notifica sobre un cambio de estado en un RMA
        
        Args:
            rma_data: Datos del RMA actualizado
            country_id: ID del país del RMA
        """
        message = {
            "type": "rma_status_changed",
            "data": rma_data,
            "timestamp": rma_data.get("updated_at")
        }
        
        # Notificar a superadmins
        await self.broadcast_to_role(message, UserRole.SUPERADMIN)
        
        # Notificar a admins/users del país
        await self.broadcast_to_country(message, country_id)
        
        logger.info(f"RMA status change notification sent: RMA ID={rma_data.get('id')}, Status={rma_data.get('status')}")


# Instancia global del gestor de conexiones
manager = ConnectionManager()
