from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import BookingRequest, Property, Tenant, User, Agreement, Payment
from schemas import BookingRequestResponse, BookingRequestCreate
from dependencies import get_current_user

router = APIRouter(
    prefix="/booking-requests",
    tags=["Booking Requests"]
)


@router.get("", response_model=List[BookingRequestResponse])
def get_booking_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(BookingRequest)

    if current_user.role == "manager":
        # Get requests for manager's properties
        managed_props = db.query(Property).filter(Property.owner_id == current_user.id).all()
        managed_prop_ids = [p.id for p in managed_props]
        query = query.filter(BookingRequest.property_id.in_(managed_prop_ids))

    elif current_user.role == "tenant":
        # Get requests for current tenant
        tenant_profile = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
        if tenant_profile:
            query = query.filter(BookingRequest.tenant_id == tenant_profile.id)
        else:
            return []

    return query.all()


@router.post("", response_model=BookingRequestResponse)
def create_booking_request(
    data: BookingRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify property is vacant
    prop = db.query(Property).filter(Property.id == data.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if prop.status != "vacant":
        raise HTTPException(status_code=400, detail="Property is not vacant and cannot be booked")

    # Verify tenant profile exists
    tenant = db.query(Tenant).filter(Tenant.id == data.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant profile not found")

    # Check for active agreements on this property
    active_agreement = db.query(Agreement).filter(
        Agreement.property_id == data.property_id,
        Agreement.status == "active"
    ).first()
    if active_agreement:
        raise HTTPException(status_code=400, detail="Property already has an active tenancy")

    new_request = BookingRequest(
        property_id=data.property_id,
        tenant_id=data.tenant_id,
        start_date=data.start_date,
        end_date=data.end_date,
        status="pending",
        created_at=datetime.now().strftime("%Y-%m-%d")
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request


@router.put("/{request_id}/approve")
def approve_booking_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Access denied: Admin or Manager permissions required")

    req = db.query(BookingRequest).filter(BookingRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Booking request not found")

    prop = req.property
    if not prop:
        raise HTTPException(status_code=404, detail="Associated property not found")

    if prop.status != "vacant":
        raise HTTPException(status_code=400, detail="Property is no longer vacant")

    # Update request status
    req.status = "approved"

    # Create lease agreement
    new_agreement = Agreement(
        property_id=req.property_id,
        tenant_id=req.tenant_id,
        start_date=req.start_date,
        end_date=req.end_date,
        rent_amount=prop.rent_amount,
        deposit_amount=prop.rent_amount * 2,
        status="active",
        document_url="lease_agreement.pdf"
    )
    db.add(new_agreement)
    db.commit()
    db.refresh(new_agreement)

    # Set property to occupied
    prop.status = "occupied"

    # Auto-reject conflicting pending booking requests for this same property or by the same tenant
    db.query(BookingRequest).filter(
        (BookingRequest.property_id == req.property_id) | (BookingRequest.tenant_id == req.tenant_id),
        BookingRequest.id != request_id,
        BookingRequest.status == "pending"
    ).update({"status": "rejected"})

    # Generate first payment record due in 1 month
    due_date = datetime.now() + timedelta(days=30)
    due_date_str = due_date.strftime("%Y-%m-%d")

    payment = Payment(
        agreement_id=new_agreement.id,
        amount=new_agreement.rent_amount,
        due_date=due_date_str,
        status="pending",
        payment_method=None
    )
    db.add(payment)
    db.commit()

    return {
        "message": "Booking approved and agreement created",
        "agreement_id": new_agreement.id
    }


@router.delete("/{request_id}")
def delete_booking_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    req = db.query(BookingRequest).filter(BookingRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Booking request not found")

    # Allow tenant signee or manager/admin to delete
    if current_user.role == "tenant":
        tenant_profile = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
        if not tenant_profile or req.tenant_id != tenant_profile.id:
            raise HTTPException(status_code=403, detail="Unauthorized to cancel this booking request")
    elif current_user.role == "manager":
        if req.property.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Unauthorized to manage this booking request")

    db.delete(req)
    db.commit()

    return {"message": "Booking request deleted successfully"}
