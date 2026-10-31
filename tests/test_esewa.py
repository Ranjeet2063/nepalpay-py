import json
import base64
from nepalpay import EsewaGateway, EsewaConfig, Environment

def test_esewa_signature_generation():
    gateway = EsewaGateway(EsewaConfig(product_code="EPAYTEST", secret_key="8gBm/:&EnhH.1/q"))
    sig = gateway.generate_signature(total_amount="100", transaction_uuid="TEST-123", product_code="EPAYTEST")
    assert isinstance(sig, str)
    assert len(sig) > 0

def test_esewa_initiate_payment():
    gateway = EsewaGateway(EsewaConfig(product_code="EPAYTEST", secret_key="8gBm/:&EnhH.1/q"))
    res = gateway.initiate_payment(
        amount=500.0,
        transaction_uuid="ORD-9999",
        success_url="https://example.com/success",
        failure_url="https://example.com/fail"
    )
    assert res.success is True
    assert res.gateway == "esewa"
    assert res.form_fields["amount"] == "500"
    assert res.form_fields["total_amount"] == "500"
    assert res.form_fields["product_code"] == "EPAYTEST"
    assert "signature" in res.form_fields

def test_esewa_verify_payment_valid():
    gateway = EsewaGateway(EsewaConfig(product_code="EPAYTEST", secret_key="8gBm/:&EnhH.1/q"))
    
    # Craft valid signed payload
    total_amount = "100"
    transaction_uuid = "ORD-VALID-1"
    product_code = "EPAYTEST"
    sig = gateway.generate_signature(total_amount, transaction_uuid, product_code)

    payload = {
        "status": "COMPLETE",
        "signature": sig,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "transaction_code": "ESEWA-REF-777"
    }

    encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    result = gateway.verify_payment(encoded)

    assert result.is_valid is True
    assert result.status == "COMPLETED"
    assert result.transaction_id == "ORD-VALID-1"
    assert result.amount == 100.0
    assert result.reference_id == "ESEWA-REF-777"

def test_esewa_verify_payment_tampered():
    gateway = EsewaGateway(EsewaConfig(product_code="EPAYTEST", secret_key="8gBm/:&EnhH.1/q"))
    payload = {
        "status": "COMPLETE",
        "signature": "INVALID_SIGNATURE",
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "total_amount": "100",
        "transaction_uuid": "ORD-TAMPERED",
        "product_code": "EPAYTEST"
    }
    encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    result = gateway.verify_payment(encoded)
    assert result.is_valid is False
