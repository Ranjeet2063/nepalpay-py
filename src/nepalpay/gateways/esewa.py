import hmac
import hashlib
import base64
import json
from typing import Dict, Any, Optional
from ..types import EsewaConfig, Environment, PaymentInitiationResult, PaymentVerificationResult

class EsewaGateway:
    """
    eSewa ePaisa V2 Gateway Integration.
    Pure Python standard library implementation using HMAC-SHA256.
    """
    TEST_FORM_URL = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
    PROD_FORM_URL = "https://epay.esewa.com.np/api/epay/main/v2/form"

    def __init__(self, config: Optional[EsewaConfig] = None):
        self.config = config or EsewaConfig()

    @property
    def form_url(self) -> str:
        return self.TEST_FORM_URL if self.config.environment == Environment.TEST else self.PROD_FORM_URL

    def generate_signature(self, total_amount: str, transaction_uuid: str, product_code: Optional[str] = None) -> str:
        code = product_code or self.config.product_code
        message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={code}"
        secret = self.config.secret_key.encode("utf-8")
        signature = hmac.new(secret, message.encode("utf-8"), hashlib.sha256).digest()
        return base64.b64encode(signature).decode("utf-8")

    def initiate_payment(
        self,
        amount: float,
        transaction_uuid: str,
        success_url: str,
        failure_url: str,
        tax_amount: float = 0.0,
        service_charge: float = 0.0,
        delivery_charge: float = 0.0,
        product_code: Optional[str] = None
    ) -> PaymentInitiationResult:
        code = product_code or self.config.product_code
        total_amount = f"{amount + tax_amount + service_charge + delivery_charge:.2f}".rstrip('0').rstrip('.')
        
        signature = self.generate_signature(total_amount, transaction_uuid, code)

        fields = {
            "amount": f"{amount:.2f}".rstrip('0').rstrip('.'),
            "tax_amount": f"{tax_amount:.2f}".rstrip('0').rstrip('.'),
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
            "product_code": code,
            "product_service_charge": f"{service_charge:.2f}".rstrip('0').rstrip('.'),
            "product_delivery_charge": f"{delivery_charge:.2f}".rstrip('0').rstrip('.'),
            "success_url": success_url,
            "failure_url": failure_url,
            "signed_field_names": "total_amount,transaction_uuid,product_code",
            "signature": signature
        }

        return PaymentInitiationResult(
            gateway="esewa",
            success=True,
            redirect_url=self.form_url,
            form_fields=fields,
            transaction_id=transaction_uuid
        )

    def verify_payment(self, encoded_data: str) -> PaymentVerificationResult:
        """
        Verify incoming callback base64 encoded data from eSewa V2.
        eSewa sends `data` param in GET/POST containing base64 JSON payload.
        """
        try:
            decoded_bytes = base64.b64decode(encoded_data)
            data: Dict[str, Any] = json.loads(decoded_bytes.decode("utf-8"))

            status = data.get("status", "")
            signature = data.get("signature", "")
            signed_field_names = data.get("signed_field_names", "")
            transaction_code = data.get("transaction_code", "")
            total_amount = str(data.get("total_amount", ""))
            transaction_uuid = str(data.get("transaction_uuid", ""))
            product_code = data.get("product_code", self.config.product_code)

            # Reconstruct message based on signed_field_names
            fields = signed_field_names.split(",")
            parts = []
            for f in fields:
                f_strip = f.strip()
                if f_strip in data:
                    parts.append(f"{f_strip}={data[f_strip]}")
            message = ",".join(parts)

            secret = self.config.secret_key.encode("utf-8")
            expected_sig = base64.b64encode(
                hmac.new(secret, message.encode("utf-8"), hashlib.sha256).digest()
            ).decode("utf-8")

            is_valid = (expected_sig == signature) and (status.upper() == "COMPLETE")

            return PaymentVerificationResult(
                gateway="esewa",
                is_valid=is_valid,
                status="COMPLETED" if is_valid else status,
                transaction_id=transaction_uuid,
                amount=float(total_amount) if total_amount else 0.0,
                reference_id=transaction_code,
                raw_data=data
            )
        except Exception as e:
            return PaymentVerificationResult(
                gateway="esewa",
                is_valid=False,
                status="FAILED",
                transaction_id="",
                amount=0.0,
                error_message=str(e)
            )
