from flask import Blueprint, render_template, redirect, url_for, request
from models import db, Feedback, Order

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# 🔹 Головна адмін-панель
@admin_bp.route("/")
def admin_panel():
    orders = Order.query.all()
    feedback = Feedback.query.all()
    return render_template("admin.html", orders=orders, feedback=feedback)

# 🔹 Видалення відгуку
@admin_bp.route("/delete_feedback/<int:id>", methods=["POST"])
def delete_feedback(id):
    fb = Feedback.query.get_or_404(id)
    db.session.delete(fb)
    db.session.commit()
    return redirect(url_for("admin.admin_panel"))

# 🔹 Деталі замовлення
@admin_bp.route("/order/<int:order_id>")
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("order_details.html", order=order)

# 🔹 Оновлення статусу замовлення
@admin_bp.route("/update_order_status/<int:order_id>", methods=["POST"])
def update_order(order_id):
    status = request.form["status"]
    order = Order.query.get_or_404(order_id)
    order.status = status
    db.session.commit()
    return redirect(url_for("admin.admin_panel"))

# 🔹 Видалення замовлення
@admin_bp.route("/delete_order/<int:order_id>", methods=["POST"])
def delete_order_route(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for("admin.admin_panel"))
