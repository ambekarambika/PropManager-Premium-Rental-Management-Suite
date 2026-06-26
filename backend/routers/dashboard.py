from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from dependencies import get_current_user
from models import User, Property, Agreement, Payment, Maintenance, BookingRequest, Tenant

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def format_collected_rent(amount: float) -> str:
    if amount >= 100000:
        return f"₹{amount / 100000:.1f}L"
    elif amount >= 1000:
        return f"₹{amount / 1000:.0f}K"
    return f"₹{amount}"


def format_pending_rent(amount: float) -> str:
    if amount >= 1000:
        return f"₹{amount / 1000:.0f}K"
    return f"₹{amount}"


@router.get("/{role}")
def get_dashboard_data(
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if role in ("manager", "admin"):
        # Total properties
        if role == "admin":
            total_props = db.query(Property).count()
            occupied_props = db.query(Property).filter(Property.status == "occupied").count()
        else:
            total_props = db.query(Property).filter(Property.owner_id == current_user.id).count()
            occupied_props = db.query(Property).filter(
                Property.owner_id == current_user.id,
                Property.status == "occupied"
            ).count()

        occupancy_rate = f"{int(100 * occupied_props / total_props)}%" if total_props > 0 else "0%"

        # Rent Collected and Pending
        # Manager can only see payments linked to their properties
        payments_query = db.query(Payment).join(Agreement).join(Property)
        if role == "manager":
            payments_query = payments_query.filter(Property.owner_id == current_user.id)

        payments = payments_query.all()
        collected = sum(p.amount for p in payments if p.status == "paid")
        pending = sum(p.amount for p in payments if p.status != "paid")

        # Maintenance tickets count
        tickets_query = db.query(Maintenance).join(Property)
        if role == "manager":
            tickets_query = tickets_query.filter(Property.owner_id == current_user.id)

        tickets = tickets_query.all()
        open_tickets = sum(1 for t in tickets if t.status != "done")
        urgent_tickets = sum(1 for t in tickets if t.status == "urgent")

        # Due Rents list: unpaid payments
        due_query = db.query(Payment).join(Agreement).join(Property).filter(Payment.status != "paid")
        if role == "manager":
            due_query = due_query.filter(Property.owner_id == current_user.id)

        due_payments = due_query.order_by(Payment.due_date).limit(5).all()
        due_rents_list = []
        for dp in due_payments:
            tenant_profile = db.query(Tenant).filter(Tenant.id == dp.agreement.tenant_id).first()
            tenant_name = tenant_profile.user.name if (tenant_profile and tenant_profile.user) else "Unknown Tenant"
            due_rents_list.append({
                "id": dp.id,
                "tenantName": tenant_name,
                "dueDate": dp.due_date,
                "amount": f"₹{dp.amount:,}",
                "status": dp.status
            })

        # Recent activities: dynamically construct list from recent events in DB
        activities = []
        # 1. Recent payments
        recent_pays = db.query(Payment).join(Agreement).join(Property)
        if role == "manager":
            recent_pays = recent_pays.filter(Property.owner_id == current_user.id)
        recent_pays = recent_pays.filter(Payment.status == "paid").order_by(Payment.id.desc()).limit(3).all()
        for rp in recent_pays:
            tenant_profile = db.query(Tenant).filter(Tenant.id == rp.agreement.tenant_id).first()
            t_name = tenant_profile.user.name if (tenant_profile and tenant_profile.user) else "Tenant"
            activities.append({
                "id": f"act-pay-{rp.id}",
                "text": f"Rent received from <strong>{t_name}</strong> — ₹{rp.amount:,}",
                "time": "Recently",
                "type": "payment"
            })

        # 2. Recent agreements signed
        recent_agrs = db.query(Agreement).join(Property)
        if role == "manager":
            recent_agrs = recent_agrs.filter(Property.owner_id == current_user.id)
        recent_agrs = recent_agrs.order_by(Agreement.id.desc()).limit(2).all()
        for ra in recent_agrs:
            tenant_profile = db.query(Tenant).filter(Tenant.id == ra.tenant_id).first()
            t_name = tenant_profile.user.name if (tenant_profile and tenant_profile.user) else "Tenant"
            activities.append({
                "id": f"act-agr-{ra.id}",
                "text": f"Lease agreement signed for <strong>{ra.property.title}</strong> with <strong>{t_name}</strong>",
                "time": "Recently",
                "type": "agreement"
            })

        # Sort activities or fallback to standard list
        if not activities:
            activities = [
                { "id": "act-1", "text": "Welcome to PropManager Suite!", "time": "Just now", "type": "info" }
            ]

        # Calculate dynamic collection trend for the last 6 months
        import calendar
        trend_months = []
        current_year = datetime.now().year
        current_month = datetime.now().month

        for i in range(5, -1, -1):
            m = current_month - i
            y = current_year
            if m <= 0:
                m += 12
                y -= 1
            trend_months.append({
                "label": calendar.month_abbr[m],
                "year_month": f"{y}-{m:02d}"
            })

        collection_trend = []
        for tm in trend_months:
            prefix = tm["year_month"]
            month_paid_query = db.query(Payment).filter(
                Payment.status == "paid",
                Payment.payment_date.like(f"{prefix}%")
            )
            if role == "manager":
                month_paid_query = month_paid_query.join(Agreement).join(Property).filter(Property.owner_id == current_user.id)
            
            month_paid = sum(p.amount for p in month_paid_query.all())
            collection_trend.append(month_paid)

        max_val = max(collection_trend) if collection_trend else 0
        if max_val > 0:
            normalized_trend = [int(10 + 70 * (val / max_val)) for val in collection_trend]
        else:
            normalized_trend = [10, 10, 10, 10, 10, 10]

        return {
            "kpi": {
                "totalProperties": total_props,
                "occupancyRate": occupancy_rate,
                "rentCollected": format_collected_rent(collected),
                "pendingRent": format_pending_rent(pending),
                "openTickets": open_tickets,
                "urgentTickets": urgent_tickets
            },
            "dueRents": due_rents_list,
            "recentActivity": activities[:5],
            "collectionTrend": normalized_trend,
            "collectionTrendLabels": [tm["label"] for tm in trend_months]
        }

    elif role == "tenant":
        tenant_profile = db.query(Tenant).filter(Tenant.user_id == current_user.id).first()
        if not tenant_profile:
            return {
                "lease": None,
                "nextPayment": None,
                "payments": [],
                "maintenanceTickets": [],
                "contacts": {
                    "manager": {"name": "System Manager", "email": "manager@example.com", "phone": "+91 99999 99999"},
                    "owner": {"name": "Super Admin", "email": "admin@example.com", "phone": "+91 99999 88888"}
                }
            }

        # Active agreement
        active_agr = db.query(Agreement).filter(
            Agreement.tenant_id == tenant_profile.id,
            Agreement.status == "active"
        ).first()

        lease_data = None
        next_payment = None
        payments_list = []
        maintenance_tickets = []
        manager_contact = {"name": "System Manager", "email": "manager@example.com", "phone": "+91 99999 99999"}

        if active_agr:
            prop = active_agr.property
            lease_data = {
                "id": active_agr.id,
                "propertyName": prop.title,
                "address": f"{prop.address}, {prop.city or ''}",
                "rent": f"₹{active_agr.rent_amount:,}",
                "deposit": f"₹{active_agr.deposit_amount:,}",
                "startDate": active_agr.start_date,
                "endDate": active_agr.end_date,
                "status": active_agr.status
            }

            # Next Payment due
            next_due = db.query(Payment).filter(
                Payment.agreement_id == active_agr.id,
                Payment.status != "paid"
            ).order_by(Payment.due_date).first()

            if next_due:
                next_payment = {
                    "amount": f"₹{next_due.amount:,}",
                    "dueDate": next_due.due_date,
                    "status": next_due.status
                }

            # Payments history
            payments_list = db.query(Payment).filter(Payment.agreement_id == active_agr.id).order_by(Payment.id.desc()).limit(5).all()

            # Maintenance tickets
            maintenance_tickets = db.query(Maintenance).filter(Maintenance.property_id == prop.id).order_by(Maintenance.id.desc()).limit(5).all()

            # Manager details
            if prop.owner:
                manager_contact = {
                    "name": prop.owner.name,
                    "email": prop.owner.email,
                    "phone": prop.owner.phone or "+91 99999 99999"
                }
            
            # Owner details
            if prop.owner_name:
                owner_contact = {
                    "name": prop.owner_name,
                    "email": prop.owner_email or "admin@example.com",
                    "phone": prop.owner_phone or "+91 99999 88888"
                }
            else:
                owner_contact = {
                    "name": "Super Admin",
                    "email": "admin@example.com",
                    "phone": "+91 99999 88888"
                }
        else:
            owner_contact = {
                "name": "Super Admin",
                "email": "admin@example.com",
                "phone": "+91 99999 88888"
            }

        # Format payments list for JSON serialization
        formatted_payments = []
        for p in payments_list:
            formatted_payments.append({
                "id": p.id,
                "agreement_id": p.agreement_id,
                "amount": p.amount,
                "due_date": p.due_date,
                "payment_date": p.payment_date,
                "status": p.status,
                "payment_method": p.payment_method
            })

        # Format maintenance tickets
        formatted_maint = []
        for mt in maintenance_tickets:
            formatted_maint.append({
                "id": mt.id,
                "property_id": mt.property_id,
                "description": mt.description,
                "status": mt.status,
                "reported_date": mt.reported_date,
                "notes": mt.notes
            })

        return {
            "lease": lease_data,
            "nextPayment": next_payment,
            "payments": formatted_payments,
            "maintenanceTickets": formatted_maint,
            "contacts": {
                "manager": manager_contact,
                "owner": owner_contact
            }
        }

    return {}
