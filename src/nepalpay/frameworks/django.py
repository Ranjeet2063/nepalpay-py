from typing import Dict, Any, Optional
from ..types import PaymentVerificationResult
from ..client import NepalPay

class DjangoPaymentHandler:
    """
    Drop-in Django payment callback and webhook adapter for NepalPay.
    Zero external dependencies.
    """

    def __init__(self, client: NepalPay):
        self.client = client

    def process_request(self, request_get: Dict[str, Any], request_post: Optional[Dict[str, Any]] = None) -> PaymentVerificationResult:
        get_params = request_get or {}
        post_params = request_post or {}

        # Merge parameters with POST taking priority
        merged = {**get_params, **post_params}

        # 1. eSewa V2
        if "data" in merged:
            return self.client.esewa.verify_payment(merged["data"])

        # 2. Khalti
        if "pidx" in merged and self.client.khalti:
            return self.client.khalti.verify_payment(merged["pidx"])

        # 3. ConnectIPS
        if "TXNID" in merged and "REFERENCEID" in merged and "TXNAMT" in merged and self.client.connectips:
            return self.client.connectips.verify_payment(merged["TXNID"], int(merged["TXNAMT"]), merged["REFERENCEID"])

        # 4. IME Pay
        if "TokenId" in merged and self.client.imepay:
            return self.client.imepay.verify_payment(merged["TokenId"], merged.get("RefId", ""))

        return PaymentVerificationResult(
            gateway="unknown",
            is_valid=False,
            status="UNRECOGNIZED_PAYLOAD",
            transaction_id="",
            amount=0.0,
            error_message="Could not auto-detect Nepal payment gateway from request parameters"
        )
