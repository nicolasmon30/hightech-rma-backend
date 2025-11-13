from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.rma import RMAStatus

if TYPE_CHECKING:
    from app.schemas.user import UserResponse


class RMAHistoryBase(BaseModel):
    """Base para historial de RMA"""
    previous_status: Optional[RMAStatus] = None
    new_status: RMAStatus
    comment: Optional[str] = None


class RMAHistoryResponse(RMAHistoryBase):
    """Respuesta de historial"""
    id: int
    rma_id: int
    changed_by: int
    changed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RMAHistoryWithUser(RMAHistoryResponse):
    """Historial con información del usuario que hizo el cambio"""
    changer: "UserResponse"
    
    model_config = ConfigDict(from_attributes=True)


# Resolver referencias
from app.schemas.user import UserResponse
RMAHistoryWithUser.model_rebuild()