import urllib.parse

def generate_whatsapp_url(phone_number, message):
    """Generate WhatsApp URL with encoded message"""
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_message}"

def validate_order_data(items):
    """Validate order items data"""
    if not isinstance(items, list):
        return False, "Items must be a list"
    
    for idx, item in enumerate(items):
        if not item.get('name'):
            return False, f"Item {idx + 1}: Missing name"
        if not item.get('price'):
            return False, f"Item {idx + 1}: Missing price"
        if not isinstance(item.get('price'), (int, float)) or item['price'] <= 0:
            return False, f"Item {idx + 1}: Price must be a positive number"
        if 'qty' in item and (not isinstance(item['qty'], int) or item['qty'] <= 0):
            return False, f"Item {idx + 1}: Quantity must be a positive integer"
    
    return True, None

def generate_order_id():
    """Generate a short readable order ID"""
    import uuid
    return str(uuid.uuid4())[:8].upper()