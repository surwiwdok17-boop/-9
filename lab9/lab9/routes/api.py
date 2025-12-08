from flask import Blueprint, jsonify, render_template, redirect, url_for, request
from models import db, Order, Feedback, Product

api_bp = Blueprint("api", __name__, url_prefix="/api")

# 🔹 Отримати всі товари
@api_bp.route("/products", methods=["GET"])
def get_products():
    """
    Get all products
    ---
    responses:
      200:
        description: Список товарів
        schema:
          type: array
          items:
            properties:
              id:
                type: integer
              name:
                type: string
              price:
                type: number
    """
    products = Product.query.all()

    def img_url_for(p):
        if not p.image_url:
            return None
        # якщо вже повний URL або абсолютний шлях — повертаємо як є
        if p.image_url.startswith("http") or p.image_url.startswith("/"):
            return p.image_url
        # інакше формуємо шлях до static
        return url_for('static', filename=p.image_url)

    return jsonify([{
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "image_url": img_url_for(p)
    } for p in products])

# 🔹 Створити замовлення (спрощено: створюємо порожнє замовлення для client_id, деталізація через items окремо)
@api_bp.route("/orders", methods=["POST"])
def create_order():
    """
    Create new order
    ---
    parameters:
      - name: client_id
        in: formData
        type: integer
        required: true
    responses:
      201:
        description: Замовлення створено
    """
    client_id = request.form.get("client_id") or (request.json and request.json.get("client_id"))
    if not client_id:
        return jsonify({"error": "client_id required"}), 400
    try:
        client_id = int(client_id)
    except (ValueError, TypeError):
        return jsonify({"error": "invalid client_id"}), 400

    order = Order(client_id=client_id, status="нове")
    db.session.add(order)
    db.session.commit()
    return jsonify({"message": "Order created", "id": order.id}), 201

# 🔹 Отримати всі відгуки
@api_bp.route("/feedback", methods=["GET"])
def get_feedback():
    """
    Get all feedback
    ---
    responses:
      200:
        description: Список відгуків
        schema:
          type: array
          items:
            properties:
              id:
                type: integer
              text:
                type: string
    """
    feedback = Feedback.query.all()
    return jsonify([{"id": f.id, "name": f.name, "email": f.email, "message": f.message, "product_id": f.product_id} for f in feedback])