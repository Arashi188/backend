from flask import Blueprint, jsonify, request
from app import db
from app.models import Order, OrderItem
from app.utils.helpers import generate_whatsapp_url, validate_order_data
import uuid

orders_bp = Blueprint('orders', __name__)

# WhatsApp number (same as frontend)
WHATSAPP_NUMBER = '2347088028747'

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """Create a new order for WhatsApp checkout"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'items' not in data:
            return jsonify({'error': 'Missing items in order data'}), 400
        
        items_data = data.get('items', [])
        total = data.get('total', 0)
        
        if not items_data:
            return jsonify({'error': 'Order must contain at least one item'}), 400
        
        # Validate items structure
        is_valid, error_msg = validate_order_data(items_data)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Create order
        order = Order(
            order_id=str(uuid.uuid4()),
            total=total,
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email'),
            customer_phone=data.get('customer_phone')
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID without committing
        
        # Create order items
        for item in items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_name=item.get('name'),
                price=item.get('price'),
                quantity=item.get('qty', 1)
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Generate WhatsApp message and URL
        whatsapp_message = format_whatsapp_message(order, items_data, total)
        whatsapp_url = generate_whatsapp_url(WHATSAPP_NUMBER, whatsapp_message)
        
        return jsonify({
            'order_id': order.order_id,
            'whatsapp_url': whatsapp_url,
            'message': 'Order created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def format_whatsapp_message(order, items, total):
    """Format WhatsApp message with order details"""
    message = f"🛍️ *NEW ORDER #{order.order_id[:8]}* 🛍️\n\n"
    message += "*Order Details:*\n"
    
    for idx, item in enumerate(items, 1):
        message += f"{idx}. {item.get('name')} - x{item.get('qty')} @ ₦{item.get('price'):,.2f}\n"
    
    message += f"\n📦 *Total: ₦{total:,.2f}*\n\n"
    message += "Thank you for shopping with ShopHub! 🚀"
    
    return message


@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders (admin view)"""
    try:
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return jsonify([order.to_dict() for order in orders]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get single order by UUID"""
    try:
        order = Order.query.filter_by(order_id=order_id).first()
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        return jsonify(order.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500