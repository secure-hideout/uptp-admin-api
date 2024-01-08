from fastapi import APIRouter

main_router = APIRouter()
from .auth_routes import router as auth_router
from routes.routes import router as routes
from routes.user_routes import router as user_router

main_router.include_router(auth_router, tags=["Auth"])
main_router.include_router(user_router, tags=["User"])
main_router.include_router(routes, tags=["All"])