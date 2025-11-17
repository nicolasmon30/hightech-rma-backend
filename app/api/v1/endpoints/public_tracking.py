"""Endpoint público para tracking de RMA por número.
No requiere autenticación.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import rma as crud_rma
from app.schemas.rma_public import RMAPublicResponse, RMAPublicItem, RMAPublicHistory

router = APIRouter()


@router.get("/rma/{rma_number}", response_model=RMAPublicResponse, summary="Consultar RMA público por número")
def track_rma(rma_number: str, db: Session = Depends(get_db)):
    """Devuelve información pública del RMA, excluyendo documentos adjuntos.
    Requiere que el RMA esté aprobado (tiene rma_number).
    """
    rma_obj = crud_rma.get_by_number_with_relations(db, rma_number=rma_number)
    if not rma_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="RMA no encontrado")

    # Construir items públicos
    public_items = []
    for item in rma_obj.items:
        public_items.append(
            RMAPublicItem(
                id=item.id,
                serial_number=item.serial_number,
                service_type=item.service_type,
                issue_description=item.issue_description,
                brand_id=item.brand_id,
                brand_name=item.brand.name if item.brand else None,
                product_id=item.product_id,
                product_name=item.product.name if item.product else None,
                model_id=item.model_id,
                model_name=item.model.name if item.model else None,
            )
        )

    # Historial simplificado
    public_history = [
        RMAPublicHistory(
            previous_status=h.previous_status,
            new_status=h.new_status,
            changed_at=h.changed_at,
            comment=h.comment
        )
        for h in sorted(rma_obj.history, key=lambda x: x.changed_at)
    ]

    return RMAPublicResponse(
        rma_number=rma_obj.rma_number,
        status=rma_obj.status,
        company_name=rma_obj.company_name,
        company_address=rma_obj.company_address,
        postal_code=rma_obj.postal_code,
        country_id=rma_obj.country_id,
        created_at=rma_obj.created_at,
        updated_at=rma_obj.updated_at,
        shipping_company=rma_obj.shipping_company,
        tracking_id=rma_obj.tracking_id,
        items=public_items,
        history=public_history
    )
