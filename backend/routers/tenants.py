from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Tenant, User
from schemas import TenantResponse, TenantCreate, TenantUpdate
from dependencies import get_current_user
from auth import hash_password

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"]
)


def map_tenant_to_response(t: Tenant) -> dict:
    return {
        "id": t.id,
        "user_id": t.user_id,
        "name": t.user.name if t.user else "",
        "email": t.user.email if t.user else "",
        "phone": t.phone,
        "emergency_contact": t.emergency_contact,
        "id_proof_url": t.id_proof_url
    }


@router.get("", response_model=List[TenantResponse])
def get_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tenants = db.query(Tenant).all()
    return [map_tenant_to_response(t) for t in tenants]


@router.post("", response_model=TenantResponse)
def create_tenant(
    data: TenantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Access denied: Admin or Manager permissions required")

    # Check if user email already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User email already exists")

    # Create User account for tenant
    new_user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password("tenant123"),  # default password
        role="tenant",
        phone=data.phone,
        status="active"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create Tenant profile linked to the User
    tenant = Tenant(
        user_id=new_user.id,
        phone=data.phone,
        emergency_contact=data.emergency_contact or "",
        id_proof_url=data.id_proof_url
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    return map_tenant_to_response(tenant)


@router.put("/{id}", response_model=TenantResponse)
def update_tenant(
    id: int,
    data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tenant = db.query(Tenant).filter(Tenant.id == id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if current_user.role != "admin" and tenant.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to edit this tenant")

    # Update Tenant properties
    tenant.phone = data.phone
    tenant.emergency_contact = data.emergency_contact
    if data.id_proof_url:
        tenant.id_proof_url = data.id_proof_url

    # Update linked User details
    if tenant.user:
        tenant.user.name = data.name
        tenant.user.email = data.email
        tenant.user.phone = data.phone

    db.commit()
    db.refresh(tenant)

    return map_tenant_to_response(tenant)


@router.delete("/{id}")
def delete_tenant(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Access denied: Admin or Manager permissions required")

    tenant = db.query(Tenant).filter(Tenant.id == id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Cascade deletions:
    # 1. Delete reviews by this tenant
    from models import Review, BookingRequest, Agreement, Payment
    db.query(Review).filter(Review.tenant_id == id).delete()

    # 2. Delete booking requests by this tenant
    db.query(BookingRequest).filter(BookingRequest.tenant_id == id).delete()

    # 3. Handle agreements
    agreements = db.query(Agreement).filter(Agreement.tenant_id == id).all()
    for agr in agreements:
        # Revert property status to vacant if agreement is active
        if agr.status == "active" and agr.property:
            agr.property.status = "vacant"
        # Delete payments linked to agreement
        db.query(Payment).filter(Payment.agreement_id == agr.id).delete()
        db.delete(agr)

    # 4. Save linked User to delete later
    linked_user = tenant.user

    # 5. Delete Tenant profile
    db.delete(tenant)

    # 6. Delete linked User account
    if linked_user:
        db.delete(linked_user)

    db.commit()
    return {"message": "Tenant and associated user account, agreements, payments, reviews, and bookings deleted successfully"}

