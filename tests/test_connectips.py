from unittest.mock import patch, MagicMock
import json
from nepalpay import ConnectIPSGateway, ConnectIPSConfig, Environment

def test_connectips_token_generation():
    config = ConnectIPSConfig(
        merchant_id="MER_TEST_101",
        app_id="APP_101",
        app_name="TestApp",
        password="test_password",
        cert_path_or_secret="test_secret_key",
        environment=Environment.TEST
    )
    gateway = ConnectIPSGateway(config)
    token = gateway.generate_token(
        txn_id="TXN-001",
        txn_date="31-10-2026",
        amount_paisa=50000,
        ref_id="REF-001",
        remarks="Test Payment",
        particulars="Order payment"
    )
    assert isinstance(token, str)
    assert len(token) == 64 # SHA256 hex digest length

def test_connectips_initiate_payment():
    config = ConnectIPSConfig(
        merchant_id="MER_TEST_101",
        app_id="APP_101",
        app_name="TestApp",
        password="test_password",
        cert_path_or_secret="test_secret_key",
        environment=Environment.TEST
    )
    gateway = ConnectIPSGateway(config)
    res = gateway.initiate_payment(
        amount_npr=500.0,
        txn_id="TXN-001",
        txn_date="31-10-2026",
        ref_id="REF-001",
        remarks="Test",
        particulars="Particulars"
    )
    assert res.success is True
    assert res.gateway == "connectips"
    assert res.form_fields["TXNAMT"] == "50000"
    assert res.form_fields["MERCHANTID"] == "MER_TEST_101"
    assert "TOKEN" in res.form_fields

def test_connectips_verify_payment():
    config = ConnectIPSConfig(
        merchant_id="MER_TEST_101",
        app_id="APP_101",
        app_name="TestApp",
        password="test_password",
        cert_path_or_secret="test_secret_key",
        environment=Environment.TEST
    )
    gateway = ConnectIPSGateway(config)

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"status": "SUCCESS"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        res = gateway.verify_payment("TXN-001", 50000, "REF-001")
        assert res.is_valid is True
        assert res.status == "SUCCESS"
        assert res.amount == 500.0
