from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine
from models import Base

from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.properties import router as properties_router
from routers.tenants import router as tenants_router
from routers.agreements import router as agreements_router
from routers.payments import router as payments_router
from routers.maintenance import router as maintenance_router
from routers.booking_requests import router as booking_requests_router
from routers.dashboard import router as dashboard_router
from routers.reviews import router as reviews_router


app = FastAPI()

import os
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = [
        "http://localhost:8080", 
        "http://127.0.0.1:8080",
        "http://localhost:5173",  # Vite dev server port
        "https://prop-manager-premium-rental-managem.vercel.app",
        "https://prop-manager-premium-rental-management-suite-2hrft3bmy.vercel.app",
        "https://prop-manager-premium-renta-git-53c513-ambikas-projects-d012f307.vercel.app"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------
# CREATE TABLES SAFELY
# ----------------------
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# ----------------------
# ROUTERS
# ----------------------
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(properties_router, prefix="/api")
app.include_router(tenants_router, prefix="/api")
app.include_router(agreements_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(maintenance_router, prefix="/api")
app.include_router(booking_requests_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")

print("All API routers registered successfully")

from fastapi.routing import APIRoute

@app.on_event("startup")
def show_routes():
    print("\n=== REGISTERED ROUTES ===")

    for route in app.routes:
        if isinstance(route, APIRoute):
            print(
                f"{','.join(route.methods)} -> {route.path}"
            )

    print("=========================\n")

import os
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../frontend/dist"), html=True))
