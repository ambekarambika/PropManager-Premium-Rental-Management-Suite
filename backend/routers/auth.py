from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, Tenant
from schemas import UserRegister, UserLogin

from auth import hash_password, verify_password, create_access_token
from dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
        phone=user.phone,
        status="active"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Automatically create Tenant profile if role is tenant
    if new_user.role == "tenant":
        tenant_profile = Tenant(
            user_id=new_user.id,
            phone=new_user.phone,
            emergency_contact="",
            id_proof_url=None
        )
        db.add(tenant_profile)
        db.commit()

    return {"message": "User created"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if db_user.status == "deactivated":
        raise HTTPException(status_code=403, detail="Your account is deactivated. Please contact the administrator.")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": db_user.email,
        "role": db_user.role
    })

    return {
        "token": token,
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "role": db_user.role,
            "phone": db_user.phone,
            "status": db_user.status
        }
    }


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "phone": current_user.phone,
        "status": current_user.status
    }