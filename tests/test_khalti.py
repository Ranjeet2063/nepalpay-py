from unittest.mock import patch, MagicMock
import json
from nepalpay import KhaltiGateway, KhaltiConfig, Environment

def test_khalti_amount_paisa_conversion():
    config = KhaltiConfig(secret_key="test_secret_key", environment=Environment.TEST)
    gateway = KhaltiGateway(config)

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "pidx": "k_pidx_12345",
            "payment_url": "https://test-pay.khalti.com/?pidx=k_pidx_12345"
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = gateway.initiate_payment(
            return_url="https://example.com/callback",
            website_url="https://example.com",
            amount_npr=150.50,
            purchase_order_id="ORD-101",
            purchase_order_name="Test Product"
        )

        assert res.success is True
        assert res.gateway == "khalti"
        assert res.transaction_id == "k_pidx_12345"
        assert res.redirect_url == "https://test-pay.khalti.com/?pidx=k_pidx_12345"

def test_khalti_verify_payment():
    config = KhaltiConfig(secret_key="test_secret_key", environment=Environment.TEST)
    gateway = KhaltiGateway(config)

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "pidx": "k_pidx_12345",
            "status": "Completed",
            "total_amount": 15050,
            "transaction_id": "KHALTI_TXN_8888"
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = gateway.verify_payment("k_pidx_12345")
        assert res.is_valid is True
        assert res.status == "Completed"
        assert res.amount == 150.50
        assert res.reference_id == "KHALTI_TXN_8888"
