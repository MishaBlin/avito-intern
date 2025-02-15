from app.api.models import Item
from .extensions import db


def init_db(app):
    with app.app_context():
        db.create_all()
        if not Item.query.first():
            items = [
                Item(name="t-shirt", price=80),
                Item(name="cup", price=20),
                Item(name="book", price=50),
                Item(name="pen", price=10),
                Item(name="powerbank", price=200),
                Item(name="hoody", price=300),
                Item(name="umbrella", price=200),
                Item(name="socks", price=10),
                Item(name="wallet", price=50),
                Item(name="pink-hoody", price=500),
            ]
            db.session.bulk_save_objects(items)
            db.session.commit()
