import threading
import time
import unittest
import requests
from app.api import create_app


class E2ETestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.server_thread = threading.Thread(
            target=cls.app.run,
            kwargs={'debug': False, 'use_reloader': False, 'port': 8081}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)
        cls.base_url = "http://127.0.0.1:8081/api"

    def setUp(self):
        reset_url = f"{self.base_url}/test/reset"
        response = requests.post(reset_url, timeout=5)
        self.assertEqual(response.status_code, 200)

    def authenticate(self, username, password):
        auth_url = f"{self.base_url}/auth"
        payload = {"username": username, "password": password}
        response = requests.post(auth_url, json=payload, timeout=5)
        self.assertEqual(response.status_code, 200)
        token = response.json().get("token")
        self.assertIsNotNone(token)
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    def get_info(self, headers):
        response = requests.get(f"{self.base_url}/info", headers=headers)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_e2e_buy_item(self):
        headers = self.authenticate("buyer", "password")
        buy_url = f"{self.base_url}/buy/pink-hoody"
        response = requests.get(buy_url, headers=headers, timeout=5)
        self.assertEqual(response.status_code, 200)

        info = self.get_info(headers)

        self.assertEqual(500, info.get("coins"))
        self.assertEqual([{"type": "pink-hoody", "quantity": 1}], info.get("inventory"))

    def test_e2e_send_coins(self):
        headers_sender = self.authenticate("sender", "password1")
        headers_receiver = self.authenticate("receiver", "password2")

        sendcoin_url = f"{self.base_url}/sendCoin"
        send_payload = {"toUser": "receiver", "amount": 100}
        response = requests.post(sendcoin_url, json=send_payload, headers=headers_sender, timeout=5)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully sent", response.json().get("message", ""))

        info_sender = self.get_info(headers_sender)
        self.assertEqual(900, info_sender.get("coins"))
        self.assertEqual([{"toUser": "receiver", "amount": 100}],
                         info_sender["coinHistory"]["sent"])

        info_receiver = self.get_info(headers_receiver)
        self.assertEqual(1100, info_receiver.get("coins"))
        self.assertEqual([{"fromUser": "sender", "amount": 100}],
                         info_receiver["coinHistory"]["received"])


if __name__ == '__main__':
    unittest.main()
