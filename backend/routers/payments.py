from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import Payment, User, Agreement, Property, Tenant
from schemas import PaymentResponse, PaymentCreate, PaymentRecord
from dependencies import get_current_user

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.get("", response_model=List[PaymentResponse])
def get_payments(
    agreementId: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Payment)

    if agreementId:
        query = query.filter(Payment.agreement_id == agreementId)

    if current_user.role == "manager":
        # Filter payments for agreements linked to manager's properties
        managed_props = db.query(Property).filter(Property.owner_id == current_user.id).all()
        managed_prop_ids = [p.id for p in managed_props]
        agreements = db.query(Agreement).filter(Agreement.property_id.in_(managed_prop_ids)).all()
        agr_ids = [a.id for a in agreements]
        query = query.filter(Payment.agreement_id.in_(agr_ids))

    elif current_user.role == "tenant":
        # Filter payments for agreements linked to current tenant
        tenant_profile = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
        if tenant_profile:
            agreements = db.query(Agreement).filter(Agreement.tenant_id == tenant_profile.id).all()
            agr_ids = [a.id for a in agreements]
            query = query.filter(Payment.agreement_id.in_(agr_ids))
        else:
            return []

    return query.all()


@router.post("", response_model=PaymentResponse)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Access denied: Admin or Manager permissions required")

    payment = Payment(
        agreement_id=data.agreement_id,
        amount=data.amount,
        due_date=data.due_date,
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
def record_payment(
    payment_id: int,
    data: PaymentRecord,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")

    agreement = payment.agreement
    if not agreement:
         raise HTTPException(status_code=404, detail="Agreement linked to payment not found")

    # Security check: manager must own the property of the agreement
    if current_user.role == "manager":
        if agreement.property.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized to collect payments for this property")
    elif current_user.role == "tenant":
        raise HTTPException(status_code=403, detail="Tenants cannot record/collect payments directly")

    payment.status = "paid"
    payment.payment_date = datetime.now().strftime("%Y-%m-%d")
    payment.payment_method = data.payment_method

    db.commit()
    db.refresh(payment)

    return payment