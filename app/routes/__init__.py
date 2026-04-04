# Routes package initialization
from app.routes.products import products_bp
from app.routes.orders import orders_bp
from app.routes.admin import admin_bp

__all__ = ['products_bp', 'orders_bp', 'admin_bp']