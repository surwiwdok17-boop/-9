from flask import Blueprint, render_template

demo_bp = Blueprint("demo", __name__)

@demo_bp.route("/api-demo")
def api_demo():
    return render_template("api-demo.html")