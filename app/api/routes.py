from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import init_db
from .extensions import db
from .models import User, Item, Purchase, CoinTransaction

main = Blueprint('main', __name__, url_prefix='/api')


@main.route('/info', methods=['GET'])
@jwt_required()
def info():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()

    inventory_dict = {}
    for purchase in user.purchases:
        inventory_dict[purchase.item_name] = inventory_dict.get(purchase.item_name, 0) + 1
    inventory = [{"type": k, "quantity": v} for k, v in inventory_dict.items()]

    received = []
    for tx in user.received_transactions:
        sender = User.query.get(tx.from_user_id)
        received.append({
            "fromUser": sender.username if sender else "Unknown",
            "amount": tx.amount
        })

    sent = []
    for tx in user.sent_transactions:
        receiver = User.query.get(tx.to_user_id)
        sent.append({
            "toUser": receiver.username if receiver else "Unknown",
            "amount": tx.amount
        })

    response = {
        "coins": user.balance,
        "inventory": inventory,
        "coinHistory": {
            "received": received,
            "sent": sent
        }
    }
    return jsonify(response), 200


@main.route('/sendCoin', methods=['POST'])
@jwt_required()
def send_coin():
    data = request.get_json()
    if not data or "toUser" not in data or "amount" not in data:
        return jsonify({"errors": "toUser and amount are required."}), 400

    to_user = data["toUser"]
    amount = data["amount"]
    if not isinstance(amount, int) or amount <= 0:
        return jsonify({"errors": "Amount must be a positive integer."}), 400

    from_username = get_jwt_identity()
    sender = User.query.filter_by(username=from_username).first()
    receiver = User.query.filter_by(username=to_user).first()

    if not receiver:
        return jsonify({"errors": "Recipient user not found."}), 400

    if sender.balance < amount:
        return jsonify({"errors": "Not enough coins to send."}), 400

    sender.balance -= amount
    receiver.balance += amount

    transaction = CoinTransaction(from_user_id=sender.id, to_user_id=receiver.id, amount=amount)
    db.session.add(transaction)
    db.session.commit()

    return jsonify({"message": f"Successfully sent {amount} coins to {to_user}."}), 200


@main.route('/buy/<string:item>', methods=['GET'])
@jwt_required()
def buy_item(item):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"errors": "User not found."}), 404

    product = Item.query.filter_by(name=item).first()
    if not product:
        return jsonify({"errors": "Item not available."}), 400

    if user.balance < product.price:
        return jsonify({"errors": "Not enough coins to buy this item."}), 400

    user.balance -= product.price
    purchase = Purchase(user_id=user.id, item_name=product.name, price=product.price)
    db.session.add(purchase)
    db.session.commit()

    return {}, 200


@main.route('/test/reset', methods=['POST'])
def reset_database():
    if not current_app.config.get("TESTING", False):
        return {"errors": "Not allowed"}, 403

    db.drop_all()
    db.create_all()
    init_db(current_app)
    return {"message": "Database reset."}, 200
