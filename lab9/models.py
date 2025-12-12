from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(250))
    description = db.Column(db.Text)  # поле для опису товару

    # 🔹 зв'язок з відгуками
    feedbacks = db.relationship("Feedback", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return self.name


class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)

    # Залишаємо поля, як в проектах: name,email,message
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    message = db.Column(db.String(500), nullable=False)

    # 🔹 зв'язок до продукту (nullable — дозволяємо загальні відгуки)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=True)
    product = db.relationship("Product", back_populates="feedbacks")

    def __repr__(self):
        return f"Відгук #{self.id} від {self.name}"


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(250), nullable=False)

    orders = db.relationship("Order", back_populates="client")

    def __repr__(self):
        return self.name


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), default="нове")
    total_price = db.Column(db.Float)
    date = db.Column(db.String(50))

    # 🔹 зв'язок з клієнтом
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    client = db.relationship("Client", back_populates="orders")

    # 🔹 список товарів через OrderItem
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Замовлення #{self.id}"


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, default=1)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product")

    def __repr__(self):
        return f"{self.product.name} x{self.quantity}"
