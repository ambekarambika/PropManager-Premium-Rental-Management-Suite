from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="tenant")  # admin, manager, tenant
    phone = Column(String, nullable=True)
    status = Column(String, default="active")  # active, deactivated


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    phone = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    id_proof_url = Column(String, nullable=True)

    user = relationship("User")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=True)
    property_type = Column(String, nullable=False)  # flat, villa, commercial, studio
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    rent_amount = Column(Integer, nullable=False)
    status = Column(String, default="vacant")  # vacant, occupied, maintenance
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")


class Agreement(Base):
    __tablename__ = "agreements"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    rent_amount = Column(Integer, nullable=False)
    deposit_amount = Column(Integer, nullable=False)
    status = Column(String, default="active")  # active, expired, terminated
    document_url = Column(String, nullable=True)

    property = relationship("Property")
    tenant = relationship("Tenant")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(Integer, ForeignKey("agreements.id"))
    amount = Column(Integer, nullable=False)
    due_date = Column(String, nullable=False)
    payment_date = Column(String, nullable=True)
    status = Column(String, default="pending")  # paid, pending, overdue
    payment_method = Column(String, nullable=True)  # UPI, Net Banking, Card, etc.

    agreement = relationship("Agreement")


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    description = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, urgent, done
    reported_date = Column(String, nullable=False)
    notes = Column(String, nullable=True)

    property = relationship("Property")


class BookingRequest(Base):
    __tablename__ = "booking_requests"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(String, nullable=False)

    property = relationship("Property")
    tenant = relationship("Tenant")


