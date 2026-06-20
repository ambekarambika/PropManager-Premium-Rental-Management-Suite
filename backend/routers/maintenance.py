from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Maintenance, User, Property, Agreement, Tenant
from schemas import MaintenanceResponse, MaintenanceCreate, MaintenanceUpdate
from dependencies import get_current_user

router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"]
)


@router.get("", response_model=List[MaintenanceResponse])
def get_maintenance_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Maintenance)

    if current_user.role == "manager":
        # Filter tickets for properties owned/managed by the manager
        managed_props = db.query(Property).filter(Property.owner_id == current_user.id).all()
        managed_prop_ids = [p.id for p in managed_props]
        query = query.filter(Maintenance.property_id.in_(managed_prop_ids))

    elif current_user.role == "tenant":
        # Filter tickets for properties currently leased by the tenant
        tenant_profile = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
        if tenant_profile:
            active_agreements = db.query(Agreement).filter(
                Agreement.tenant_id == tenant_profile.id,
                Agreement.status == "active"
            ).all()
            leased_prop_ids = [a.property_id for a in active_agreements]
            query = query.filter(Maintenance.property_id.in_(leased_prop_ids))
        else:
            return []

    return query.all()


@router.post("", response_model=MaintenanceResponse)
def create_maintenance_ticket(
    data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify property exists
    prop = db.query(Property).filter(Property.id == data.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    # Security check: tenant must be currently leasing it, or user is admin/manager of the property
    if current_user.role == "tenant":
        tenant_profile = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
        if not tenant_profile:
            raise HTTPException(status_code=403, detail="Tenant profile not found")
        leased = db.query(Agreement).filter(
            Agreement.property_id == data.property_id,
            Agreement.tenant_id == tenant_profile.id,
            Agreement.status == "active"
        ).first()
        if not leased:
            raise HTTPException(status_code=403, detail="Cannot file maintenance for a property you do not lease")
    elif current_user.role == "manager":
        if prop.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized to file maintenance for this property")

    ticket = Maintenance(
        property_id=data.property_id,
        description=data.description,
        status=data.status or "pending",
        reported_date=datetime.now().strftime("%Y-%m-%d"),
        notes=data.notes
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


@router.put("/{ticket_id}", response_model=MaintenanceResponse)
def update_maintenance_ticket(
    ticket_id: int,
    data: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(Maintenance).filter(Maintenance.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Maintenance ticket not found")

    # Security check: manager/admin only
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized to update maintenance tickets")

    if current_user.role == "manager":
        # Check if manager manages the property
        prop = db.query(Property).filter(Property.id == ticket.property_id).first()
        if not prop or prop.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized to update this ticket")

    ticket.status = data.status
    if data.notes is not None:
        ticket.notes = data.notes

    db.commit()
    db.refresh(ticket)
    return ticket