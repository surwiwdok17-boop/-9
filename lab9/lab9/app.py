import os
from flask import Flask, jsonify, render_template
from models import db, Product, Order, Feedback, Client
from routes import blueprints
from routes.demo import demo_bp
from routes.admin import admin_bp   # імпортуємо адмінку
from flasgger import Swagger
from routes.shop import shop_bp
from routes import api_bp
from dotenv import load_dotenv
from sqlalchemy import text

# Завантажуємо змінні з .env
load_dotenv()

DATABASE_PATH = os.environ.get("DATABASE_PATH", "data/database.db")
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "your_secret_key")

swagger = Swagger(app)
db.init_app(app)

# ---- ДОДАНО: централізована проста "міграція" колонок ----
def ensure_db_columns():
    """
    Перевіряє і додає відсутні колонки у sqlite таблицях:
    - product.description (TEXT)
    - feedback.product_id (INTEGER)
    Викликається в app.app_context() одразу після db.create_all().
    """
    try:
        # створити таблиці якщо відсутні
        db.create_all()

        def has_column(table, col):
            res = db.session.execute(text(f"PRAGMA table_info({table});")).fetchall()
            cols = [r[1] for r in res] if res else []
            return col in cols

        # product.description
        if not has_column("product", "description"):
            db.session.execute(text("ALTER TABLE product ADD COLUMN description TEXT;"))

        # feedback.product_id
        if not has_column("feedback", "product_id"):
            db.session.execute(text("ALTER TABLE feedback ADD COLUMN product_id INTEGER;"))

        db.session.commit()
    except Exception:
        db.session.rollback()

# Реєстрація blueprint'ів
# 🔹 shop_bp реєструємо один раз, без name='shop1'
app.register_blueprint(shop_bp)
app.register_blueprint(demo_bp)
app.register_blueprint(admin_bp)  # адмінка окремо
app.register_blueprint(api_bp)

# 🔹 у циклі виключаємо shop, щоб не дублювати
for bp in blueprints:
    if bp.name not in ["admin", "api", "shop"]:
        app.register_blueprint(bp)

# Healthcheck
@app.route('/health')
def health():
    try:
        db.session.execute(text('SELECT 1'))
        return {'status': 'healthy'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500

with app.app_context():
    db.create_all()

    # 🔹 Проста міграція: перевірка/додавання колонок, щоб уникнути OperationalError у існуючій sqlite БД
    def _ensure_column(table, column_name, col_def):
        try:
            res = db.session.execute(text(f"PRAGMA table_info({table});")).fetchall()
            cols = [r[1] for r in res]
            if column_name not in cols:
                db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_def};"))
                db.session.commit()
        except Exception:
            db.session.rollback()

    # гарантуємо наявність потрібних колонок
    _ensure_column("product", "description", "description TEXT")
    _ensure_column("feedback", "product_id", "product_id INTEGER")

# Обробка помилок
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad Request"}), 400

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server Error"}), 500

# Картинки для головної сторінки
images = [
    "https://cloudy.kyiv.ua/image/cache/catalog/products/Rdini/Zhizha-NOVA-Red-Bull-Blue-Raspberry-Salt-30ml-65mg-870x1131.jpg",
    "https://uestore.in.ua/image/cache/catalog/doublerasp-600x600-900x900.jpg",
    "https://v7par.com.ua/image/cache/catalog/1212/disposablle/elfbarrr/geekbar/2022-09-08%2012.35.34-650x650.jpg",
    "https://vapehub.shop/image/cache/catalog/import_files/51/51785680820711edfc8700505687efca_b93a26048f6811edcd9600505687efca-600x600.jpg",
    "https://uestore.in.ua/image/cache/catalog/pineapplelemonade-600x600-900x900.jpg",
    "https://terra-vape.com.ua/image/cache/catalog/Chaser/Nova-salt-30ml/nova-salt-30ml-mango-peach-1000x1000.jpg",
    "https://v7par.org.ua/image/cache/catalog/1212/disposablle/elfbarrr/geekbar/2-650x650.jpg",
]
index = 0

@app.route('/')
def home():
    global index
    image_url = images[index]
    index = (index + 1) % len(images)
    return render_template('home.html', image_url=image_url)

# -----------------------
# Нове: простий "міграційний" чек для sqlite
def ensure_product_description_column():
    """
    Перевіряє таблицю product і додає колонку description TEXT, якщо її немає.
    Робиться через PRAGMA table_info + ALTER TABLE (SQLite підтримує ALTER ADD COLUMN).
    """
    try:
        # Отримати інформацію про колонки таблиці product
        res = db.session.execute(text("PRAGMA table_info(product);")).fetchall()
        cols = [r[1] for r in res]  # формат рядка: (cid, name, type, notnull, dflt_value, pk)
        if "description" not in cols:
            db.session.execute(text("ALTER TABLE product ADD COLUMN description TEXT;"))
            db.session.commit()
    except Exception:
        # якщо таблиці ще немає або сталася інша помилка — відкат і продовження
        db.session.rollback()

if __name__ == "__main__":
    with app.app_context():
        # гарантуємо що таблиці створені
        db.create_all()

        # НОВЕ: застосовуємо просту міграцію перед зверненнями до моделей
        ensure_product_description_column()

        # --- НОВЕ: додати описи для уже наявних продуктів, якщо їх немає ---
        descriptions = {
            "Apple": "Соковитий яблучний мікс — свіжий, солодко‑кислий аромат, як щойно зірване яблуко.",
            "Berry & Mint": "Ягідна суміш із прохолодною ноткою м'яти — освіжає та підкреслює ягідний букет.",
            "Blueberry": "Насичений чорничний смак з легкою солодкою кислинкою та натуральним післясмаком.",
            "Cola Lemon": "Класична кола з яскравою цитрусовою ноткою лимона — газований, солодко‑освіжаючий вкус.",
            "Double Grape": "Подвійний виноград: насичений та солодкий, з легкою шовковистою солодкістю.",
            "Double Raspberry": "Інтенсивна подвійна малина — яскравий фруктовий аромат з тонкою кислинкою.",
            "Mango & Peach": "Тропічна суміш манго та персика — соковита і ніжна, як літній коктейль.",
            "Nova Cranberry & Mors": "Кисло‑солодкий журавлинний мікс з ягідним морсом — освіжаючий і з характером.",
            "Nova Red Bull": "Енергетичний бустер з цитрусовими та фруктовими нотками — робить настрій бадьорим.",
            "Nova Spearmint": "Різка і свіжа спірмінтова м’ята — чудове освіження після кожного затяжку.",
            "Pineapple Lemonade": "Ананасовий лимонад: тропіки та легка кислинка лимона для соковитого балансу.",
            "Tabacoo": "Класичний тютюновий аромат з теплими деревними відтінками — для шанувальників традиції.",
            "Watermelon & Melon": "Соковита диня з кавуном — легкий, солодкий та дуже літній смак."
        }

        updated = False
        for p in Product.query.all():
            if not (p.description and str(p.description).strip()):
                p.description = descriptions.get(p.name, "Опис поки відсутній")
                updated = True
        if updated:
            db.session.commit()
        # --- /кінець нового блока ---

        if not Product.query.first():
            demo_products = [
                Product(name="Apple", price=240, image_url="images/apple.jpg",
                        description="Соковитий яблучний мікс — свіжий, солодко‑кислий аромат, як щойно зірване яблуко."),
                Product(name="Berry & Mint", price=260, image_url="images/berry_mint.jpg",
                        description="Ягідна суміш із прохолодною ноткою м'яти — освіжає та підкреслює ягідний букет."),
                Product(name="Blueberry", price=270, image_url="images/blueberry.jpg",
                        description="Насичений чорничний смак з легкою солодкою кислинкою та натуральним післясмаком."),
                Product(name="Cola Lemon", price=322, image_url="images/cola_lemon.jpg",
                        description="Класична кола з яскравою цитрусовою ноткою лимона — газований, солодко‑освіжаючий вкус."),
                Product(name="Double Grape", price=255, image_url="images/double_grape.jpg",
                        description="Подвійний виноград: насичений та солодкий, з легкою шовковистою солодкістю."),
                Product(name="Double Raspberry", price=250, image_url="images/double_raspberry.jpg",
                        description="Інтенсивна подвійна малина — яскравий фруктовий аромат з тонкою кислинкою."),
                Product(name="Mango & Peach", price=275, image_url="images/mango_peach.jpg",
                        description="Тропічна суміш манго та персика — соковита і ніжна, як літній коктейль."),
                Product(name="Nova Cranberry & Mors", price=350, image_url="images/nova_cranberry.jpg",
                        description="Кисло‑солодкий журавлинний мікс з ягідним морсом — освіжаючий і з характером."),
                Product(name="Nova Red Bull", price=290, image_url="images/nova_redbull.jpg",
                        description="Енергетичний бустер з цитрусовими та фруктовими нотками — робить настрій бадьорим."),
                Product(name="Nova Spearmint", price=250, image_url="images/nova_spearmint.jpg",
                        description="Різка і свіжа спірмінтова м’ята — чудове освіження після кожного затяжку."),
                Product(name="Pineapple Lemonade", price=242, image_url="images/pineapple_lemonade.jpg",
                        description="Ананасовий лимонад: тропіки та легка кислинка лимона для соковитого балансу."),
                Product(name="Tabacoo", price=230, image_url="images/tabacoo.jpg",
                        description="Класичний тютюновий аромат з теплими деревними відтінками — для шанувальників традиції."),
                Product(name="Watermelon & Melon", price=265, image_url="images/watermelon_melon.jpg",
                        description="Соковита диня з кавуном — легкий, солодкий та дуже літній смак.")
            ]
            db.session.add_all(demo_products)
            db.session.commit()
            print("✅ База заповнена демо‑товарами")
    app.run(debug=True)
