from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "tenant"
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    status: str

    class Config:
        orm_mode = True
        from_attributes = True


class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None


class TenantCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    id_proof_url: Optional[str] = None


class TenantUpdate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    id_proof_url: Optional[str] = None


class TenantResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    id_proof_url: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


class PropertyCreate(BaseModel):
    title: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    image_url: Optional[str] = None
    type: str  # maps to property_type
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    rent_amount: int
    description: Optional[str] = None
    status: Optional[str] = "vacant"
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_phone: Optional[str] = None
    interior_images: Optional[str] = None


class PropertyResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    image_url: Optional[str] = None
    type: str  # maps from property_type
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    rent_amount: int
    status: str
    owner_id: int
    manager_id: int  # maps from owner_id for frontend compatibility
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_phone: Optional[str] = None
    interior_images: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


class AgreementCreate(BaseModel):
    property_id: int
    tenant_id: int
    start_date: str
    end_date: str
    rent_amount: Optional[int] = None
    deposit_amount: Optional[int] = None
    status: Optional[str] = "active"
    document_url: Optional[str] = None


class AgreementResponse(BaseModel):
    id: int
    property_id: int
    tenant_id: int
    start_date: str
    end_date: str
    rent_amount: int
    deposit_amount: int
    status: str
    document_url: Optional[str] = None
    outstanding_balance: int = 0

    class Config:
        orm_mode = True
        from_attributes = True


class PaymentCreate(BaseModel):
    agreement_id: int
    amount: int
    due_date: str
    status: Optional[str] = "pending"


class PaymentRecord(BaseModel):
    payment_method: str


class PaymentResponse(BaseModel):
    id: int
    agreement_id: int
    amount: int
    due_date: str
    payment_date: Optional[str] = None
    status: str
    payment_method: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


class MaintenanceCreate(BaseModel):
    property_id: int
    description: str
    status: Optional[str] = "pending"
    notes: Optional[str] = None


class MaintenanceResponse(BaseModel):
    id: int
    property_id: int
    description: str
    status: str
    reported_date: str
    notes: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


class MaintenanceUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


class BookingRequestCreate(BaseModel):
    property_id: int
    tenant_id: int
    start_date: str
    end_date: str


class BookingRequestResponse(BaseModel):
    id: int
    property_id: int
    tenant_id: int
    start_date: str
    end_date: str
    status: str
    created_at: str

    class Config:
        orm_mode = True
        from_attributes = True


class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    property_id: int
    tenant_id: int
    tenant_name: str
    rating: int
    comment: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True
        from_attributes = True