from unittest.mock import patch, MagicMock
import json
from nepalpay import ImePayGateway, ImePayConfig, Environment

def test_imepay_initiate_payment():
    config = ImePayConfig(
        merchant_code="TEST_MERCHANT",
        api_user="test_user",
        password="test_password",
        environment=Environment.TEST
    )
    gateway = ImePayGateway(config)

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "ResponseCode": 0,
            "ResponseDescription": "Success",
            "TokenId": "IME_TOKEN_9999"
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = gateway.initiate_payment(
            amount_npr=750.0,
            ref_id="REF-IME-01",
            return_url="https://example.com/callback"
        )
        assert res.success is True
        assert res.gateway == "imepay"
        assert res.transaction_id == "IME_TOKEN_9999"
        assert "TokenId=IME_TOKEN_9999" in res.redirect_url

def test_imepay_verify_payment():
    config = ImePayConfig(
        merchant_code="TEST_MERCHANT",
        api_user="test_user",
        password="test_password",
        environment=Environment.TEST
    )
    gateway = ImePayGateway(config)

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "ResponseCode": 0,
            "ResponseDescription": "Success"
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = gateway.verify_payment(token_id="IME_TOKEN_9999", ref_id="REF-IME-01", txn_amount=750.0)
        assert res.is_valid is True
        assert res.status == "SUCCESS"
        assert res.amount == 750.0
