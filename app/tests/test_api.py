import secrets
import unittest
import json

from flask import Flask
from flask_jwt_extended import JWTManager

from app.api import db
from app.api import init_db

from app.api.auth import auth
from app.api.routes import main


def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def get_token_header(response):
    header = get_auth_header(json.loads(response.data.decode())['token'])
    return header


def get_auth_response(client, username=None, password=None):
    payload = {}
    if password:
        payload["password"] = password
    if username:
        payload["username"] = username

    response = client.post(
        '/api/auth',
        data=json.dumps(payload),
        content_type='application/json'
    )

    return response


def get_info(client, username, password):
    auth_response = get_auth_response(client, username, password)
    auth_header = get_token_header(auth_response)
    info_response = client.get('/api/info', headers=auth_header)
    return info_response


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
        JWTManager(self.app)
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        init_db(self.app)

        self.app.register_blueprint(auth)
        self.app.register_blueprint(main)

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_auth_create_user_success(self):
        response = get_auth_response(self.client, "testuser", "testpass")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("token", data)

    def test_auth_create_user_no_password(self):
        response = get_auth_response(self.client, "testuser2")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode())
        self.assertEqual("Username and password are required.", data["errors"])

    def test_auth_create_user_wrong_password(self):
        response = get_auth_response(self.client, "testuser", "testpassword")
        response = get_auth_response(self.client, "testuser", "wrong")
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data.decode())
        self.assertEqual("Invalid username or password.", data["errors"])

    def test_info(self):
        response = get_info(self.client, "testuser", "testpass")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("coins", data)
        self.assertIn("inventory", data)
        self.assertIn("coinHistory", data)

    def test_send_coins_success(self):
        sender_auth = get_auth_response(self.client, username="sender", password="senderPass")
        sender_header = get_token_header(sender_auth)
        receiver_auth = get_auth_response(self.client, username="receiver", password="receiverPass")

        send_payload = {"toUser": "receiver", "amount": 100}
        response = self.client.post(
            '/api/sendCoin',
            data=json.dumps(send_payload),
            content_type='application/json',
            headers=sender_header
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertIn("Successfully sent", data.get("message", ""))

        receiver_info = get_info(self.client, username="receiver", password="receiverPass")
        self.assertEqual(receiver_info.status_code, 200)
        data = json.loads(receiver_info.data.decode())
        self.assertEqual(1100, data["coins"])
        self.assertEqual([{"fromUser": "sender", "amount": 100}], data["coinHistory"]["received"])

        sender_info = get_info(self.client, username="sender", password="senderPass")
        self.assertEqual(sender_info.status_code, 200)
        data = json.loads(sender_info.data.decode())
        self.assertEqual(900, data["coins"])
        self.assertEqual([{"toUser": "receiver", "amount": 100}], data["coinHistory"]["sent"])

    def test_send_coins_error(self):
        sender_auth = get_auth_response(self.client, username="sender", password="senderPass")
        receiver_auth = get_auth_response(self.client, username="receiver", password="receiverPass")
        sender_header = get_token_header(sender_auth)

        send_payload = {"toUser": "receiver", "amount": 10000}
        response = self.client.post(
            '/api/sendCoin',
            data=json.dumps(send_payload),
            content_type='application/json',
            headers=sender_header
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode())
        self.assertEqual("Not enough coins to send.", data["errors"])

    def test_buy_item_success(self):
        auth_response = get_auth_response(self.client, username="client", password="clientPass")
        auth_header = get_token_header(auth_response)
        response = self.client.get('/api/buy/t-shirt', headers=auth_header)
        self.assertEqual(response.status_code, 200)

        info = get_info(self.client, username="client", password="clientPass")
        self.assertEqual(info.status_code, 200)
        data = json.loads(info.data.decode())
        self.assertEqual(920, data["coins"])
        self.assertEqual([{
            "type": "t-shirt",
            "quantity": 1,
        }], data["inventory"])

    def test_buy_item_error(self):
        auth_response = get_auth_response(self.client, username="client", password="clientPass")
        auth_header = get_token_header(auth_response)

        response = self.client.get('/api/buy/nonexistent', headers=auth_header)

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode())
        self.assertEqual("Item not available.", data["errors"])


if __name__ == '__main__':
    unittest.main()
