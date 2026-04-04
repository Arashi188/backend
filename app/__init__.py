from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://localhost:5500",
                "http://127.0.0.1:5500",
                "https://your-frontend.vercel.app"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    
    # ========== ROOT ENDPOINT (Fixes the 404 error) ==========
    @app.route('/')
    def index():
        return jsonify({
            'message': 'ShopHub API is running successfully!',
            'status': 'online',
            'version': '1.0.0',
            'timestamp': '2025-04-04',
            'endpoints': {
                'products': {
                    'GET /api/products': 'Get all products',
                    'GET /api/products/<id>': 'Get single product'
                },
                'orders': {
                    'POST /api/orders': 'Create new order',
                    'GET /api/orders': 'Get all orders (admin)'
                },
                'admin': {
                    'POST /api/admin/products': 'Add product',
                    'PUT /api/admin/products/<id>': 'Update product',
                    'DELETE /api/admin/products/<id>': 'Delete product',
                    'GET /api/admin/orders': 'Get all orders',
                    'PATCH /api/admin/orders/<id>/status': 'Update order status',
                    'GET /api/admin/stats': 'Get dashboard stats'
                }
            },
            'documentation': 'https://your-backend.onrender.com/api/products'
        }), 200
    
    # ========== HEALTH CHECK ENDPOINT ==========
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if check_database() else 'disconnected'
        }), 200
    
    # ========== API INFO ENDPOINT ==========
    @app.route('/api/info')
    def api_info():
        return jsonify({
            'name': 'ShopHub E-commerce API',
            'version': '1.0.0',
            'base_url': '/api',
            'available_endpoints': [
                '/api/products',
                '/api/products/<id>',
                '/api/orders',
                '/api/admin/products',
                '/api/admin/products/<id>',
                '/api/admin/orders',
                '/api/admin/orders/<id>/status',
                '/api/admin/stats'
            ]
        }), 200
    
    # ========== ERROR HANDLERS ==========
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Resource not found',
            'message': 'The requested URL was not found on the server',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong on our end',
            'status_code': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': 'Invalid request parameters',
            'status_code': 400
        }), 400
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method not allowed',
            'message': 'HTTP method not supported for this endpoint',
            'status_code': 405
        }), 405
    
    return app

# Helper function for health check
def check_database():
    """Check if database is accessible"""
    try:
        from app.models import Product
        db.session.execute('SELECT 1')
        return True
    except Exception:
        return False