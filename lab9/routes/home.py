from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__)

images = [
    "https://cloudy.kyiv.ua/image/cache/catalog/products/Rdini/Zhizha-NOVA-Red-Bull-Blue-Raspberry-Salt-30ml-65mg-870x1131.jpg",
    "https://uestore.in.ua/image/cache/catalog/doublerasp-600x600-900x900.jpg",
    "https://v7par.com.ua/image/cache/catalog/1212/disposablle/elfbarrr/geekbar/2022-09-08%2012.35.34-650x650.jpg",
]

index = 0

@home_bp.route("/")
def home():
    global index
    image_url = images[index]
    index = (index + 1) % len(images)
    return render_template("home.html", image_url=image_url)

@home_bp.route("/about")
def about():
    return render_template("about.html")
