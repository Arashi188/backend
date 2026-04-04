from flask import Blueprint, jsonify, request
from app import db
from app.models import Product, Order

admin_bp = Blueprint('admin', __name__)

# Simple admin auth (in production, use proper JWT)
ADMIN_TOKEN = "admin-secret-token-change-this"

def verify_admin_token():
    """Verify admin authentication token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    token = auth_header.replace('Bearer ', '')
    return token == ADMIN_TOKEN


# ============ PRODUCT MANAGEMENT ============

@admin_bp.route('/admin/products', methods=['POST'])
def add_product():
    """Add a new product"""
    try:
        # Verify admin token
        if not verify_admin_token():
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Product name is required'}), 400
        if not data.get('price'):
            return jsonify({'error': 'Product price is required'}), 400
        if not isinstance(data.get('price'), (int, float)) or data.get('price') <= 0:
            return jsonify({'error': 'Price must be a positive number'}), 400
        
        product = Product(
            name=data['name'],
            price=float(data['price']),
            image_url=data.get('image_url', ''),
            description=data.get('description', '')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/admin/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    try:
        # Verify admin token
        if not verify_admin_token():
            return jsonify({'error': 'Unauthorized'}), 401
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'price' in data:
            if not isinstance(data['price'], (int, float)) or data['price'] <= 0:
                return jsonify({'error': 'Price must be a positive number'}), 400
            product.price = float(data['price'])
        if 'image_url' in data:
            product.image_url = data['image_url']
        if 'description' in data:
            product.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/admin/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        # Verify admin token
        if not verify_admin_token():
            return jsonify({'error': 'Unauthorized'}), 401
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ ORDER MANAGEMENT ============

@admin_bp.route('/admin/orders', methods=['GET'])
def get_all_orders():
    """Get all orders (admin view)"""
    try:
        # Verify admin token
        if not verify_admin_token():
            return jsonify({'error': 'Unauthorized'}), 401
        
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return jsonify([order.to_dict() for order in orders]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/admin/orders/<int:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    """Update order status"""
    try:
        # Verify admin token
        if not verify_admin_token():
            return jsonify({'error': 'Unauthorized'}), 401
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        valid_statuses = ['pending', 'processing', 'shipped', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        order.status = new_status
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ STATISTICS ============

@admin_bp.route('/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get admin dashboard statistics"""
    try:
        # Verify admin token
        if not verify_admin_token():
            return jsonify({'error': 'Unauthorized'}), 401
        
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
        
        # Get recent orders
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
        
        return jsonify({
            'totalProducts': total_products,
            'totalOrders': total_orders,
            'totalRevenue': float(total_revenue),
            'recentOrders': [order.to_dict() for order in recent_orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500