from flask_admin.contrib.sqla import ModelView
from models import Order

class OrderView(ModelView):
    # які колонки показувати
    column_list = ["id", "client", "client_address", "status", "products"]

    # як вони будуть називатися
    column_labels = {
        "id": "ID",
        "client": "Клієнт",
        "client_address": "Адреса доставки",
        "status": "Статус",
        "products": "Товари"
    }

    # як отримати адресу клієнта
    def _client_address(view, context, model, name):
        return model.client.address if model.client else None

    column_formatters = {
        "client_address": _client_address,
        "products": lambda v, c, m, n: ", ".join([p.name for p in m.products])
    }

    form_columns = ["client", "status", "products"]