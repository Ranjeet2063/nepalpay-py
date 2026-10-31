from nepalpay import NepalPay, FastAPIPaymentHandler, DjangoPaymentHandler, EsewaConfig

def test_fastapi_esewa_callback():
    client = NepalPay(esewa_config=EsewaConfig(product_code="EPAYTEST", secret_key="8gBm/:&EnhH.1/q"))
    handler = FastAPIPaymentHandler(client)

    sig = client.esewa.generate_signature("100", "ORD-FA-1", "EPAYTEST")
    import json, base64
    payload = {
        "status": "COMPLETE",
        "signature": sig,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "total_amount": "100",
        "transaction_uuid": "ORD-FA-1",
        "product_code": "EPAYTEST"
    }
    encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    res = handler.process_callback(query_params={"data": encoded})
    assert res.is_valid is True
    assert res.gateway == "esewa"
    assert res.transaction_id == "ORD-FA-1"

def test_django_esewa_callback():
    client = NepalPay(esewa_config=EsewaConfig(product_code="EPAYTEST", secret_key="8gBm/:&EnhH.1/q"))
    handler = DjangoPaymentHandler(client)

    sig = client.esewa.generate_signature("250", "ORD-DJ-1", "EPAYTEST")
    import json, base64
    payload = {
        "status": "COMPLETE",
        "signature": sig,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "total_amount": "250",
        "transaction_uuid": "ORD-DJ-1",
        "product_code": "EPAYTEST"
    }
    encoded = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    res = handler.process_request(request_get={"data": encoded})
    assert res.is_valid is True
    assert res.gateway == "esewa"
    assert res.transaction_id == "ORD-DJ-1"

def test_unrecognized_callback():
    client = NepalPay()
    handler = FastAPIPaymentHandler(client)
    res = handler.process_callback(query_params={"random_key": "some_value"})
    assert res.is_valid is False
    assert res.status == "UNRECOGNIZED_PAYLOAD"
