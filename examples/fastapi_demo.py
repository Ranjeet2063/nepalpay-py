"""
FastAPI Demo for nepalpay
Run: uvicorn examples.fastapi_demo:app --reload
"""

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse
except ImportError:
    raise ImportError("FastAPI is required to run this example. Install via: pip install fastapi uvicorn")

from nepalpay import NepalPay, Environment, EsewaConfig, FastAPIPaymentHandler

app = FastAPI(title="NepalPay FastAPI Demo")

client = NepalPay(
    environment=Environment.TEST,
    esewa_config=EsewaConfig(product_code="EPAYTEST", secret_key="8gBm/:&EnhH.1/q")
)
handler = FastAPIPaymentHandler(client)

@app.get("/")
def home():
    return {"message": "NepalPay Python SDK is active!", "docs": "/docs"}

@app.post("/create-order")
def create_order(amount: float, order_id: str):
    res = client.esewa.initiate_payment(
        amount=amount,
        transaction_uuid=order_id,
        success_url="http://localhost:8000/callback",
        failure_url="http://localhost:8000/callback"
    )
    return res

@app.get("/callback")
async def payment_callback(request: Request):
    params = dict(request.query_params)
    verification = handler.process_callback(query_params=params)
    return verification
