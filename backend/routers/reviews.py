from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Review, Tenant, User, Agreement
from schemas import ReviewCreate, ReviewResponse
from dependencies import get_current_user

router = APIRouter(
    prefix="/properties",
    tags=["Reviews"]
)


@router.post("/{property_id}/reviews", response_model=ReviewResponse)
def create_review(
    property_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify the user is a tenant
    tenant = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
    if not tenant:
        raise HTTPException(status_code=403, detail="Only tenants can leave ratings and comments")

    # Verify tenant has/had an agreement on this property
    agreement = db.query(Agreement).filter(
        Agreement.property_id == property_id,
        Agreement.tenant_id == tenant.id
    ).first()
    if not agreement:
        raise HTTPException(status_code=403, detail="You can only review properties you have rented")

    # Limit rating between 1 and 5
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5 stars")

    new_review = Review(
        property_id=property_id,
        tenant_id=tenant.id,
        rating=data.rating,
        comment=data.comment,
        created_at=datetime.now().strftime("%Y-%m-%d")
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return {
        "id": new_review.id,
        "property_id": new_review.property_id,
        "tenant_id": new_review.tenant_id,
        "tenant_name": current_user.name,
        "rating": new_review.rating,
        "comment": new_review.comment,
        "created_at": new_review.created_at
    }


@router.get("/{property_id}/reviews", response_model=List[ReviewResponse])
def get_property_reviews(
    property_id: int,
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(Review.property_id == property_id).order_by(Review.id.desc()).all()
    result = []
    for r in reviews:
        tenant_name = "Unknown Tenant"
        if r.tenant and r.tenant.user:
            tenant_name = r.tenant.user.name
        result.append({
            "id": r.id,
            "property_id": r.property_id,
            "tenant_id": r.tenant_id,
            "tenant_name": tenant_name,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at
        })
    return result
