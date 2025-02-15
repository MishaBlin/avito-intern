from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Integer, default=1000)
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    sent_transactions = db.relationship('CoinTransaction',
                                        foreign_keys='CoinTransaction.from_user_id',
                                        backref='sender',
                                        lazy=True)
    received_transactions = db.relationship('CoinTransaction',
                                            foreign_keys='CoinTransaction.to_user_id',
                                            backref='receiver',
                                            lazy=True)


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)


class CoinTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
