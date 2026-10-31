import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from ..types import KhaltiConfig, Environment, PaymentInitiationResult, PaymentVerificationResult

class KhaltiGateway:
    """
    Khalti V2 ePayment Gateway Integration.
    Pure Python standard library implementation using urllib.request.
    """
    TEST_INITIATE_URL = "https://a.khalti.com/api/v2/epayment/initiate/"
    PROD_INITIATE_URL = "https://khalti.com/api/v2/epayment/initiate/"
    TEST_LOOKUP_URL = "https://a.khalti.com/api/v2/epayment/lookup/"
    PROD_LOOKUP_URL = "https://khalti.com/api/v2/epayment/lookup/"

    def __init__(self, config: KhaltiConfig):
        self.config = config

    @property
    def initiate_url(self) -> str:
        return self.TEST_INITIATE_URL if self.config.environment == Environment.TEST else self.PROD_INITIATE_URL

    @property
    def lookup_url(self) -> str:
        return self.TEST_LOOKUP_URL if self.config.environment == Environment.TEST else self.PROD_LOOKUP_URL

    def initiate_payment(
        self,
        return_url: str,
        website_url: str,
        amount_npr: float,
        purchase_order_id: str,
        purchase_order_name: str,
        customer_info: Optional[Dict[str, str]] = None,
        amount_breakdown: Optional[list] = None,
        product_details: Optional[list] = None
    ) -> PaymentInitiationResult:
        # Convert NPR to Paisa (integer)
        amount_paisa = int(round(amount_npr * 100))

        payload: Dict[str, Any] = {
            "return_url": return_url,
            "website_url": website_url,
            "amount": amount_paisa,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": purchase_order_name,
        }
        if customer_info:
            payload["customer_info"] = customer_info
        if amount_breakdown:
            payload["amount_breakdown"] = amount_breakdown
        if product_details:
            payload["product_details"] = product_details

        headers = {
            "Authorization": f"Key {self.config.secret_key}",
            "Content-Type": "application/json",
            "User-Agent": "nepalpay-py/1.0"
        }

        req = urllib.request.Request(
            self.initiate_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return PaymentInitiationResult(
                    gateway="khalti",
                    success=True,
                    redirect_url=data.get("payment_url"),
                    transaction_id=data.get("pidx"),
                    raw_response=data
                )
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            return PaymentInitiationResult(
                gateway="khalti",
                success=False,
                error_message=f"HTTP {e.code}: {err_body}"
            )
        except Exception as e:
            return PaymentInitiationResult(
                gateway="khalti",
                success=False,
                error_message=str(e)
            )

    def verify_payment(self, pidx: str) -> PaymentVerificationResult:
        """
        Verify payment status using Khalti Lookup API.
        """
        payload = {"pidx": pidx}
        headers = {
            "Authorization": f"Key {self.config.secret_key}",
            "Content-Type": "application/json",
            "User-Agent": "nepalpay-py/1.0"
        }

        req = urllib.request.Request(
            self.lookup_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                status = data.get("status", "")
                is_valid = status.upper() == "COMPLETED"
                total_paisa = data.get("total_amount", 0)

                return PaymentVerificationResult(
                    gateway="khalti",
                    is_valid=is_valid,
                    status=status,
                    transaction_id=pidx,
                    amount=float(total_paisa) / 100.0,
                    reference_id=data.get("transaction_id"),
                    raw_data=data
                )
        except urllib.error.HTTPError as e:
            return PaymentVerificationResult(
                gateway="khalti",
                is_valid=False,
                status="ERROR",
                transaction_id=pidx,
                amount=0.0,
                error_message=f"HTTP {e.code}: {e.read().decode('utf-8')}"
            )
        except Exception as e:
            return PaymentVerificationResult(
                gateway="khalti",
                is_valid=False,
                status="ERROR",
                transaction_id=pidx,
                amount=0.0,
                error_message=str(e)
            )
