from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import Agreement, Property, User, Tenant, Payment
from schemas import AgreementCreate, AgreementResponse
from dependencies import get_current_user

router = APIRouter(
    prefix="/agreements",
    tags=["Agreements"]
)


def map_agreement_to_response(a: Agreement, db: Session) -> dict:
    # Calculate outstanding balance: sum of unpaid payments
    unpaid_payments = db.query(Payment).filter(
        Payment.agreement_id == a.id,
        Payment.status != "paid"
    ).all()
    outstanding = sum(p.amount for p in unpaid_payments)

    return {
        "id": a.id,
        "property_id": a.property_id,
        "tenant_id": a.tenant_id,
        "start_date": a.start_date,
        "end_date": a.end_date,
        "rent_amount": a.rent_amount,
        "deposit_amount": a.deposit_amount,
        "status": a.status,
        "document_url": a.document_url,
        "outstanding_balance": outstanding
    }


@router.post("", response_model=AgreementResponse)
def create_agreement(
    data: AgreementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Access denied: Admin or Manager permissions required")

    property_obj = db.query(Property).filter(Property.id == data.property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    if property_obj.status != "vacant":
        raise HTTPException(status_code=400, detail="Property is currently not vacant and cannot be leased")

    # Check for active agreements on this property
    active_agreement = db.query(Agreement).filter(
        Agreement.property_id == data.property_id,
        Agreement.status == "active"
    ).first()
    if active_agreement:
        raise HTTPException(status_code=400, detail="Property already has an active agreement")

    tenant_obj = db.query(Tenant).filter(Tenant.id == data.tenant_id).first()
    if not tenant_obj:
        raise HTTPException(status_code=404, detail="Tenant profile not found")

    rent = data.rent_amount if data.rent_amount is not None else property_obj.rent_amount
    deposit = data.deposit_amount if data.deposit_amount is not None else (rent * 2)

    agreement = Agreement(
        property_id=data.property_id,
        tenant_id=data.tenant_id,
        start_date=data.start_date,
        end_date=data.end_date,
        rent_amount=rent,
        deposit_amount=deposit,
        status="active",
        document_url=data.document_url or "lease_agreement.pdf"
    )

    db.add(agreement)
    db.commit()
    db.refresh(agreement)

    # Set property status to occupied
    property_obj.status = "occupied"

    # Generate first payment record due in 1 month
    due_date = datetime.now() + timedelta(days=30)
    due_date_str = due_date.strftime("%Y-%m-%d")

    first_payment = Payment(
        agreement_id=agreement.id,
        amount=agreement.rent_amount,
        due_date=due_date_str,
        status="pending",
        payment_method=None
    )
    db.add(first_payment)
    db.commit()

    return map_agreement_to_response(agreement, db)


@router.get("", response_model=List[AgreementResponse])
def get_agreements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Agreement)

    if current_user.role == "manager":
        # Get agreements for properties managed by this user
        managed_props = db.query(Property).filter(Property.owner_id == current_user.id).all()
        managed_prop_ids = [p.id for p in managed_props]
        query = query.filter(Agreement.property_id.in_(managed_prop_ids))
    elif current_user.role == "tenant":
        # Get agreements for the current tenant user
        tenant_profile = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
        if tenant_profile:
            query = query.filter(Agreement.tenant_id == tenant_profile.id)
        else:
            return []

    agreements = query.all()
    return [map_agreement_to_response(a, db) for a in agreements]


@router.get("/{agreement_id}", response_model=AgreementResponse)
def get_agreement(
    agreement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agreement = db.query(Agreement).filter(Agreement.id == agreement_id).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")

    # Security check
    if current_user.role == "manager":
        if agreement.property.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized to view this agreement")
    elif current_user.role == "tenant":
        tenant_profile = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
        if not tenant_profile or agreement.tenant_id != tenant_profile.id:
            raise HTTPException(status_code=403, detail="Unauthorized to view this agreement")

    return map_agreement_to_response(agreement, db)


@router.put("/{agreement_id}/terminate", response_model=AgreementResponse)
def terminate_agreement(
    agreement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agreement = db.query(Agreement).filter(Agreement.id == agreement_id).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")

    # Security check
    if current_user.role != "admin":
        if current_user.role == "manager":
            if agreement.property.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="Unauthorized to terminate this agreement")
        elif current_user.role == "tenant":
            tenant_profile = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
            if not tenant_profile or agreement.tenant_id != tenant_profile.id:
                raise HTTPException(status_code=403, detail="Unauthorized to terminate this agreement")

    agreement.status = "terminated"
    
    # Update property status back to vacant
    if agreement.property:
        agreement.property.status = "vacant"

    db.commit()
    db.refresh(agreement)
    return map_agreement_to_response(agreement, db)


@router.delete("/{agreement_id}")
def delete_agreement(
    agreement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete agreements")

    agreement = db.query(Agreement).filter(Agreement.id == agreement_id).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found")

    db.delete(agreement)
    db.commit()
    return {"message": "Agreement deleted successfully"}