from typing import Dict, Any, Callable, Optional
from ..types import PaymentVerificationResult
from ..client import NepalPay

class FastAPIPaymentHandler:
    """
    Drop-in FastAPI payment callback and webhook adapter for NepalPay.
    Zero external dependencies (works with standard dictionary or FastAPI Request).
    """

    def __init__(self, client: NepalPay):
        self.client = client

    def process_callback(self, query_params: Dict[str, Any], body: Optional[Dict[str, Any]] = None) -> PaymentVerificationResult:
        params = query_params or {}
        body = body or {}

        # 1. eSewa V2 check (sends base64 encoded 'data' param in query)
        if "data" in params:
            return self.client.esewa.verify_payment(params["data"])

        # 2. Khalti check (sends 'pidx' param in query or body)
        pidx = params.get("pidx") or body.get("pidx")
        if pidx and self.client.khalti:
            return self.client.khalti.verify_payment(pidx)

        # 3. ConnectIPS check (sends TXNID and TXNAMT)
        txn_id = params.get("TXNID") or body.get("TXNID")
        ref_id = params.get("REFERENCEID") or body.get("REFERENCEID")
        amt = params.get("TXNAMT") or body.get("TXNAMT")
        if txn_id and ref_id and amt and self.client.connectips:
            return self.client.connectips.verify_payment(txn_id, int(amt), ref_id)

        # 4. IME Pay check (sends TokenId, RefId)
        token_id = params.get("TokenId") or body.get("TokenId")
        if token_id and self.client.imepay:
            ime_ref = params.get("RefId") or body.get("RefId", "")
            return self.client.imepay.verify_payment(token_id, ime_ref)

        return PaymentVerificationResult(
            gateway="unknown",
            is_valid=False,
            status="UNRECOGNIZED_PAYLOAD",
            transaction_id="",
            amount=0.0,
            error_message="Could not auto-detect Nepal payment gateway from request payload"
        )
