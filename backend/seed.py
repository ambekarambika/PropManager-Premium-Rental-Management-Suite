import os
import sys
from datetime import datetime

# Adjust Python path to import backend components properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base
from models import User, Tenant, Property, Agreement, Payment, Maintenance, BookingRequest
from auth import hash_password


def seed_database():
    print("Connecting and resetting database tables...")
    
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding Users...")
        # 1. Users
        admin_user = User(
            name="Super Admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            role="admin",
            phone="+91 99999 88888",
            status="active"
        )
        manager_user = User(
            name="Rajesh Kumar",
            email="rajesh@example.com",
            hashed_password=hash_password("manager123"),
            role="manager",
            phone="+91 98765 43210",
            status="active"
        )
        tenant_arjun = User(
            name="Arjun Sharma",
            email="arjun@example.com",
            hashed_password=hash_password("tenant123"),
            role="tenant",
            phone="+91 98765 11111",
            status="active"
        )
        tenant_priya = User(
            name="Priya Desai",
            email="priya@example.com",
            hashed_password=hash_password("tenant123"),
            role="tenant",
            phone="+91 98765 22222",
            status="active"
        )
        tenant_kiran = User(
            name="Kiran Nair",
            email="kiran@example.com",
            hashed_password=hash_password("tenant123"),
            role="tenant",
            phone="+91 98765 33333",
            status="active"
        )
        tenant_sunita = User(
            name="Sunita Rao",
            email="sunita@example.com",
            hashed_password=hash_password("tenant123"),
            role="tenant",
            phone="+91 98765 44444",
            status="active"
        )
        
        db.add_all([admin_user, manager_user, tenant_arjun, tenant_priya, tenant_kiran, tenant_sunita])
        db.commit()
        
        print("Seeding Tenant profiles...")
        # 2. Tenants
        t1 = Tenant(
            user_id=tenant_arjun.id,
            phone=tenant_arjun.phone,
            emergency_contact="Amit Sharma: +91 98765 99991",
            id_proof_url="id_arjun.pdf"
        )
        t2 = Tenant(
            user_id=tenant_priya.id,
            phone=tenant_priya.phone,
            emergency_contact="Ravi Desai: +91 98765 99992",
            id_proof_url="id_priya.pdf"
        )
        t3 = Tenant(
            user_id=tenant_kiran.id,
            phone=tenant_kiran.phone,
            emergency_contact="Gopal Nair: +91 98765 99993",
            id_proof_url="id_kiran.pdf"
        )
        t4 = Tenant(
            user_id=tenant_sunita.id,
            phone=tenant_sunita.phone,
            emergency_contact="Dev Rao: +91 98765 99994",
            id_proof_url="id_sunita.pdf"
        )
        
        db.add_all([t1, t2, t3, t4])
        db.commit()
        
        print("Seeding Properties...")
        # 3. Properties (owned by Rajesh manager)
        p1 = Property(
            title="Sunrise Apartments — B-204",
            description="Cozy 2BHK flat with a spacious balcony overlooking the park.",
            address="Koregaon Park",
            city="Pune",
            property_type="flat",
            bedrooms=2,
            bathrooms=2,
            rent_amount=28000,
            status="occupied",
            owner_id=manager_user.id
        )
        p2 = Property(
            title="Green Valley Villa — 7A",
            description="Luxurious 4BHK gated community villa with private garden.",
            address="Baner",
            city="Pune",
            property_type="villa",
            bedrooms=4,
            bathrooms=4,
            rent_amount=55000,
            status="occupied",
            owner_id=manager_user.id
        )
        p3 = Property(
            title="MG Road Commercial Space",
            description="Premium ground floor commercial showroom location.",
            address="Deccan",
            city="Pune",
            property_type="commercial",
            bedrooms=None,
            bathrooms=1,
            rent_amount=42000,
            status="vacant",
            owner_id=manager_user.id
        )
        p4 = Property(
            title="Shivaji Nagar PG Suites",
            description="Furnished studio spaces for students and working professionals.",
            address="Shivaji Nagar",
            city="Pune",
            property_type="studio",
            bedrooms=1,
            bathrooms=1,
            rent_amount=12000,
            status="occupied",
            owner_id=manager_user.id
        )
        
        db.add_all([p1, p2, p3, p4])
        db.commit()
        
        print("Seeding Agreements...")
        # 4. Agreements
        a1 = Agreement(
            property_id=p1.id,
            tenant_id=t1.id,
            start_date="2025-06-01",
            end_date="2026-06-01",
            rent_amount=28000,
            deposit_amount=60000,
            status="active",
            document_url="lease_b204.pdf"
        )
        a2 = Agreement(
            property_id=p2.id,
            tenant_id=t2.id,
            start_date="2025-09-15",
            end_date="2026-09-15",
            rent_amount=55000,
            deposit_amount=110000,
            status="active",
            document_url="lease_villa7a.pdf"
        )
        a3 = Agreement(
            property_id=p4.id,
            tenant_id=t3.id,
            start_date="2026-01-01",
            end_date="2026-12-31",
            rent_amount=12000,
            deposit_amount=25000,
            status="active",
            document_url="lease_pg.pdf"
        )
        
        db.add_all([a1, a2, a3])
        db.commit()
        
        print("Seeding Payments...")
        # 5. Payments
        pay1 = Payment(
            agreement_id=a1.id,
            amount=28000,
            due_date="2026-06-17",
            payment_date="2026-06-17",
            status="paid",
            payment_method="UPI"
        )
        pay2 = Payment(
            agreement_id=a2.id,
            amount=55000,
            due_date="2026-06-20",
            payment_date=None,
            status="pending",
            payment_method=None
        )
        pay3 = Payment(
            agreement_id=a3.id,
            amount=12000,
            due_date="2026-06-22",
            payment_date=None,
            status="pending",
            payment_method=None
        )
        pay4 = Payment(
            agreement_id=a1.id,
            amount=28000,
            due_date="2026-05-17",
            payment_date="2026-05-17",
            status="paid",
            payment_method="Net Banking"
        )
        pay5 = Payment(
            agreement_id=a2.id,
            amount=55000,
            due_date="2026-05-15",
            payment_date="2026-05-16",
            status="paid",
            payment_method="UPI"
        )
        pay6 = Payment(
            agreement_id=a1.id,
            amount=28000,
            due_date="2026-04-17",
            payment_date=None,
            status="overdue",
            payment_method=None
        )
        
        db.add_all([pay1, pay2, pay3, pay4, pay5, pay6])
        db.commit()
        
        print("Seeding Maintenance...")
        # 6. Maintenance
        m1 = Maintenance(
            property_id=p1.id,
            description="Pipe leak in master bathroom toilet unit.",
            status="urgent",
            reported_date="2026-06-17",
            notes="Plumber assigned, visiting today."
        )
        m2 = Maintenance(
            property_id=p2.id,
            description="Power outage in kitchen heating appliance line.",
            status="pending",
            reported_date="2026-06-16",
            notes="Waiting for electrician slot."
        )
        m3 = Maintenance(
            property_id=p4.id,
            description="Common area walls repainting.",
            status="done",
            reported_date="2026-06-05",
            notes="Completed painting work on June 14."
        )
        
        db.add_all([m1, m2, m3])
        db.commit()
        
        print("Seeding Booking Requests...")
        # 7. Booking Requests
        br = BookingRequest(
            property_id=p3.id,
            tenant_id=t4.id,
            start_date="2026-07-01",
            end_date="2027-07-01",
            status="pending",
            created_at="2026-06-18"
        )
        db.add(br)
        db.commit()
        
        print("Database seeded successfully with premium mock records!")
        
    except Exception as e:
        db.rollback()
        print("Error during database seeding:", e)
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
