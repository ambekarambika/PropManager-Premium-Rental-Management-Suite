from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Tenant
from schemas import UserResponse, UserRegister, UserUpdate
from dependencies import get_current_user
from auth import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admin permissions required")
    return db.query(User).all()


@router.post("", response_model=UserResponse)
def create_admin_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admin permissions required")

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User email already exists")

    # Set default password if not provided
    password = user_data.password if user_data.password else "password123"

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hash_password(password),
        role=user_data.role,
        phone=user_data.phone,
        status="active"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    if new_user.role == "tenant":
        tenant = Tenant(
            user_id=new_user.id,
            phone=new_user.phone,
            emergency_contact="",
            id_proof_url=None
        )
        db.add(tenant)
        db.commit()

    return new_user


@router.put("/{id}/toggle-status", response_model=UserResponse)
def toggle_user_status(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admin permissions required")

    if current_user.id == id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own logged-in account")

    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = "deactivated" if user.status == "active" else "active"
    db.commit()
    db.refresh(user)
    return user


@router.put("/{id}/profile", response_model=UserResponse)
def update_user_profile(
    id: int,
    profile_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Standard security - users can only update their own profile unless they are admin
    if current_user.id != id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized to edit this profile")

    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = profile_data.name
    user.email = profile_data.email
    user.phone = profile_data.phone

    # If tenant, update linked Tenant emergency contact/phone
    if user.role == "tenant":
        tenant = db.query(Tenant).filter(Tenant.user_id == id).first()
        if tenant:
            tenant.phone = profile_data.phone
            if profile_data.emergency_contact is not None:
                tenant.emergency_contact = profile_data.emergency_contact
        else:
            # Create Tenant record if missing
            tenant = Tenant(
                user_id=id,
                phone=profile_data.phone,
                emergency_contact=profile_data.emergency_contact or "",
                id_proof_url=None
            )
            db.add(tenant)

    db.commit()
    db.refresh(user)
    return user