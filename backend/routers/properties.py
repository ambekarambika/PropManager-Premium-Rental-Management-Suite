from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Property, User, Agreement, Payment, BookingRequest, Maintenance, Review
from schemas import PropertyCreate, PropertyResponse
from dependencies import get_current_user

router = APIRouter(
    prefix="/properties",
    tags=["Properties"]
)


def map_property_to_response(p: Property) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "address": p.address,
        "city": p.city,
        "state": p.state,
        "pincode": p.pincode,
        "image_url": p.image_url,
        "type": p.property_type,
        "bedrooms": p.bedrooms,
        "bathrooms": p.bathrooms,
        "rent_amount": p.rent_amount,
        "status": p.status,
        "owner_id": p.owner_id,
        "manager_id": p.owner_id,
        "owner_name": p.owner_name,
        "owner_email": p.owner_email,
        "owner_phone": p.owner_phone,
        "interior_images": p.interior_images
    }


@router.post("", response_model=PropertyResponse)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(status_code=403, detail="Unauthorized role to create property")

    property_obj = Property(
        title=property_data.title,
        description=property_data.description,
        address=property_data.address,
        city=property_data.city,
        state=property_data.state,
        pincode=property_data.pincode,
        image_url=property_data.image_url,
        property_type=property_data.type,
        bedrooms=property_data.bedrooms,
        bathrooms=property_data.bathrooms,
        rent_amount=property_data.rent_amount,
        status=property_data.status or "vacant",
        owner_id=current_user.id,
        owner_name=property_data.owner_name,
        owner_email=property_data.owner_email,
        owner_phone=property_data.owner_phone,
        interior_images=property_data.interior_images
    )

    db.add(property_obj)
    db.commit()
    db.refresh(property_obj)

    return map_property_to_response(property_obj)


@router.get("", response_model=List[PropertyResponse])
def get_properties(
    status: str = Query("all"),
    search: str = Query(""),
    db: Session = Depends(get_db)
):
    query = db.query(Property)

    if status != "all":
        query = query.filter(Property.status == status)

    properties = query.all()
    result = []

    for p in properties:
        if search:
            search_text = search.lower()
            if (
                search_text not in (p.title or "").lower()
                and search_text not in (p.address or "").lower()
                and search_text not in (p.city or "").lower()
                and search_text not in (p.state or "").lower()
            ):
                continue

        result.append(map_property_to_response(p))

    return result


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db)
):
    p = db.query(Property).filter(Property.id == property_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Property not found")
    return map_property_to_response(p)


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    updated_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    property_item = db.query(Property).filter(Property.id == property_id).first()

    if not property_item:
        raise HTTPException(status_code=404, detail="Property not found")

    if current_user.role != "admin" and property_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to edit this property")

    property_item.title = updated_data.title
    property_item.description = updated_data.description
    property_item.address = updated_data.address
    property_item.city = updated_data.city
    property_item.state = updated_data.state
    property_item.pincode = updated_data.pincode
    property_item.image_url = updated_data.image_url
    property_item.property_type = updated_data.type
    property_item.bedrooms = updated_data.bedrooms
    property_item.bathrooms = updated_data.bathrooms
    property_item.rent_amount = updated_data.rent_amount
    property_item.status = updated_data.status or property_item.status
    property_item.owner_name = updated_data.owner_name
    property_item.owner_email = updated_data.owner_email
    property_item.owner_phone = updated_data.owner_phone
    property_item.interior_images = updated_data.interior_images

    db.commit()
    db.refresh(property_item)

    return map_property_to_response(property_item)


@router.delete("/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    property_item = db.query(Property).filter(Property.id == property_id).first()

    if not property_item:
        raise HTTPException(status_code=404, detail="Property not found")

    if current_user.role != "admin" and property_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this property")

    # Safely delete all associated features to prevent foreign key constraint violations
    db.query(Review).filter(Review.property_id == property_id).delete()
    db.query(BookingRequest).filter(BookingRequest.property_id == property_id).delete()
    db.query(Maintenance).filter(Maintenance.property_id == property_id).delete()
    
    # Delete all agreements and their associated payments
    agreements = db.query(Agreement).filter(Agreement.property_id == property_id).all()
    for agreement in agreements:
        db.query(Payment).filter(Payment.agreement_id == agreement.id).delete()
        db.delete(agreement)

    db.delete(property_item)
    db.commit()

    return {"message": "Property deleted successfully"}