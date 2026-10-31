# nepalpay-py 🇳🇵

[![Python Tests](https://img.shields.io/badge/tests-20%2F20%20passing-brightgreen.svg)](#)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20external-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](#)

Universal, zero-dependency Nepal Payment Gateway SDK for Python, FastAPI, and Django. Supports **eSewa (ePaisa V2)**, **Khalti (ePayment V2)**, **ConnectIPS (NCHL)**, **IME Pay**, and **EMVCo NepalQR / Fonepay**.

---

## ⚡ Features
- **Zero External Dependencies**: Built entirely using Python's standard library (`hashlib`, `hmac`, `base64`, `urllib`).
- **Unified Client (`NepalPay`)**: Single client to configure and manage all Nepali payment rails.
- **eSewa ePaisa V2**: Complete HMAC-SHA256 signature generator and callback payload verification.
- **Khalti V2 ePayment**: Automated NPR-to-Paisa conversion, initiate API, and lookup verification.
- **ConnectIPS (NCHL)**: SHA256 interbank token calculation and creditor validation API.
- **IME Pay**: TokenId checkout redirect and confirmation API.
- **NepalQR (EMVCo) & Terminal QR**: Built-in Galois Field $GF(2^8)$ and Reed-Solomon polynomial QR matrix engine rendering instant scannable QR codes directly in your terminal (`▀`, `▄`, `█`).
- **Drop-in Framework Adapters**: Ready-to-use handlers for **FastAPI** and **Django**.
- **Interactive CLI**: Test Nepal payments right from your command line (`nepalpay qr`, `nepalpay esewa`).

---

## 📦 Installation

```bash
pip install nepalpay
```

---

## 🚀 Quickstart

### 1. Unified Client Initialization
```python
from nepalpay import NepalPay, Environment, EsewaConfig, KhaltiConfig

client = NepalPay(
    environment=Environment.TEST,
    esewa_config=EsewaConfig(
        product_code="EPAYTEST",
        secret_key="8gBm/:&EnhH.1/q"
    ),
    khalti_config=KhaltiConfig(
        secret_key="test_secret_key_123456789"
    )
)
```

---

### 2. Generate Scannable Terminal NepalQR
```python
qr = client.generate_dynamic_qr(
    merchant_id="NP01MERCHANT",
    amount=500.0,
    merchant_name="Annapurna Cafe",
    merchant_city="Kathmandu",
    bill_number="BILL-1001"
)

# Render instant scannable QR in terminal:
print(qr["terminal_qr"])

# Raw EMVCo payload string:
print(qr["qr_string"])
```

---

### 3. eSewa ePaisa V2 Payment
```python
# Initiate eSewa Payment
initiation = client.esewa.initiate_payment(
    amount=1000.0,
    transaction_uuid="ORD-101",
    success_url="https://yourstore.com/payment/success",
    failure_url="https://yourstore.com/payment/failure"
)

# Pass form_fields to your frontend template or auto-submit form:
print(initiation.redirect_url)
print(initiation.form_fields)
```

---

### 4. FastAPI Drop-in Callback Handler
```python
from fastapi import FastAPI, Request
from nepalpay import NepalPay, FastAPIPaymentHandler

app = FastAPI()
client = NepalPay()
handler = FastAPIPaymentHandler(client)

@app.get("/api/payment/callback")
async def payment_callback(request: Request):
    params = dict(request.query_params)
    res = handler.process_callback(query_params=params)
    
    if res.is_valid:
        return {"status": "SUCCESS", "order_id": res.transaction_id, "amount": res.amount}
    return {"status": "FAILED", "error": res.error_message}
```

---

### 5. Django Drop-in Callback Handler
```python
from django.http import JsonResponse
from nepalpay import NepalPay, DjangoPaymentHandler

client = NepalPay()
handler = DjangoPaymentHandler(client)

def payment_callback(request):
    res = handler.process_request(request_get=request.GET, request_post=request.POST)
    if res.is_valid:
        return JsonResponse({"status": "SUCCESS", "order_id": res.transaction_id})
    return JsonResponse({"status": "FAILED", "error": res.error_message}, status=400)
```

---

## 🛠️ CLI Usage
`nepalpay` comes with an interactive CLI tool:

```bash
# Generate instant scannable terminal QR
nepalpay qr --amount 750 --name "Patan Coffee" --order ORD-8899

# Generate signed eSewa test form fields
nepalpay esewa --amount 1500 --order ORD-5544

# Verify an incoming base64 payload from eSewa
nepalpay verify-esewa "<base64_payload>"
```

---

## 🧪 Testing

Run test suite with pytest:
```bash
pytest -v
# 20 passed in 1.36s (100% Green)
```

---

## 📄 License
MIT License. Created with ❤️ for developers building in Nepal by Ranjeet Kumar Sah.
