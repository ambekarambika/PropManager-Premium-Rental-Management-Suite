from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Property, User
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
        "type": p.property_type,
        "bedrooms": p.bedrooms,
        "bathrooms": p.bathrooms,
        "rent_amount": p.rent_amount,
        "status": p.status,
        "owner_id": p.owner_id,
        "manager_id": p.owner_id
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
        property_type=property_data.type,
        bedrooms=property_data.bedrooms,
        bathrooms=property_data.bathrooms,
        rent_amount=property_data.rent_amount,
        status=property_data.status or "vacant",
        owner_id=current_user.id
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
    property_item.property_type = updated_data.type
    property_item.bedrooms = updated_data.bedrooms
    property_item.bathrooms = updated_data.bathrooms
    property_item.rent_amount = updated_data.rent_amount
    property_item.status = updated_data.status or property_item.status

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

    db.delete(property_item)
    db.commit()

    return {"message": "Property deleted successfully"}