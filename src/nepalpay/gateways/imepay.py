import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from ..types import ImePayConfig, Environment, PaymentInitiationResult, PaymentVerificationResult

class ImePayGateway:
    """
    IME Pay Wallet Gateway Integration.
    Pure Python standard library implementation.
    """
    TEST_BASE = "https://stg.imepay.com.np:7979"
    PROD_BASE = "https://payment.imepay.com.np:7979"

    def __init__(self, config: ImePayConfig):
        self.config = config

    @property
    def base_url(self) -> str:
        return self.TEST_BASE if self.config.environment == Environment.TEST else self.PROD_BASE

    def initiate_payment(
        self,
        amount_npr: float,
        ref_id: str,
        return_url: str
    ) -> PaymentInitiationResult:
        payload = {
            "MerchantCode": self.config.merchant_code,
            "Amount": f"{amount_npr:.2f}",
            "RefId": ref_id,
            "Source": "WEB"
        }
        headers = {
            "Content-Type": "application/json",
            "Module": self.config.module,
            "User": self.config.api_user,
            "Password": self.config.password
        }

        url = f"{self.base_url}/api/Web/GetToken"
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                response_code = data.get("ResponseCode")
                if response_code == 0:
                    token_id = data.get("TokenId")
                    checkout_url = f"{self.base_url}/WebCheckout/Checkout?TokenId={token_id}&MerchantCode={self.config.merchant_code}&RefId={ref_id}"
                    return PaymentInitiationResult(
                        gateway="imepay",
                        success=True,
                        redirect_url=checkout_url,
                        transaction_id=token_id,
                        raw_response=data
                    )
                else:
                    return PaymentInitiationResult(
                        gateway="imepay",
                        success=False,
                        error_message=data.get("ResponseDescription", "IME Pay Token Generation Failed"),
                        raw_response=data
                    )
        except urllib.error.HTTPError as e:
            return PaymentInitiationResult(
                gateway="imepay",
                success=False,
                error_message=f"HTTP {e.code}: {e.read().decode('utf-8')}"
            )
        except Exception as e:
            return PaymentInitiationResult(
                gateway="imepay",
                success=False,
                error_message=str(e)
            )

    def verify_payment(self, token_id: str, ref_id: str, msisdn: str = "", txn_amount: float = 0.0) -> PaymentVerificationResult:
        payload = {
            "MerchantCode": self.config.merchant_code,
            "TokenId": token_id,
            "RefId": ref_id,
            "Msisdn": msisdn,
            "TransactionAmount": f"{txn_amount:.2f}"
        }
        headers = {
            "Content-Type": "application/json",
            "Module": self.config.module,
            "User": self.config.api_user,
            "Password": self.config.password
        }

        url = f"{self.base_url}/api/Web/Confirm"
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                code = data.get("ResponseCode")
                is_valid = code == 0
                return PaymentVerificationResult(
                    gateway="imepay",
                    is_valid=is_valid,
                    status="SUCCESS" if is_valid else "FAILED",
                    transaction_id=token_id,
                    amount=txn_amount,
                    reference_id=ref_id,
                    raw_data=data
                )
        except urllib.error.HTTPError as e:
            return PaymentVerificationResult(
                gateway="imepay",
                is_valid=False,
                status="ERROR",
                transaction_id=token_id,
                amount=txn_amount,
                reference_id=ref_id,
                error_message=f"HTTP {e.code}: {e.read().decode('utf-8')}"
            )
        except Exception as e:
            return PaymentVerificationResult(
                gateway="imepay",
                is_valid=False,
                status="ERROR",
                transaction_id=token_id,
                amount=txn_amount,
                reference_id=ref_id,
                error_message=str(e)
            )
