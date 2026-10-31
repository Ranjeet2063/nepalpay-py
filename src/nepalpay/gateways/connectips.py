import hmac
import hashlib
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from ..types import ConnectIPSConfig, Environment, PaymentInitiationResult, PaymentVerificationResult

class ConnectIPSGateway:
    """
    ConnectIPS (NCHL) Interbank Payment Gateway.
    Pure Python standard library implementation.
    """
    TEST_FORM_URL = "https://uat.connectips.com:7443/connectipswebgw/loginpage"
    PROD_FORM_URL = "https://login.connectips.com/connectipswebgw/loginpage"
    TEST_VALIDATE_URL = "https://uat.connectips.com:7443/connectipswebgw/api/creditor/validatetransaction"
    PROD_VALIDATE_URL = "https://login.connectips.com/connectipswebgw/api/creditor/validatetransaction"

    def __init__(self, config: ConnectIPSConfig):
        self.config = config

    @property
    def form_url(self) -> str:
        return self.TEST_FORM_URL if self.config.environment == Environment.TEST else self.PROD_FORM_URL

    @property
    def validate_url(self) -> str:
        return self.TEST_VALIDATE_URL if self.config.environment == Environment.TEST else self.PROD_VALIDATE_URL

    def generate_token(
        self,
        txn_id: str,
        txn_date: str,
        amount_paisa: int,
        ref_id: str,
        remarks: str,
        particulars: str
    ) -> str:
        msg = (
            f"MERCHANTID={self.config.merchant_id},"
            f"APPID={self.config.app_id},"
            f"APPNAME={self.config.app_name},"
            f"TXNID={txn_id},"
            f"TXNDATE={txn_date},"
            f"TXNCRNCY=NPR,"
            f"TXNAMT={amount_paisa},"
            f"REFERENCEID={ref_id},"
            f"REMARKS={remarks},"
            f"PARTICULARS={particulars},"
            f"TOKEN=TOKEN"
        )
        secret = self.config.cert_path_or_secret.encode("utf-8")
        return hmac.new(secret, msg.encode("utf-8"), hashlib.sha256).hexdigest()

    def initiate_payment(
        self,
        amount_npr: float,
        txn_id: str,
        txn_date: str,
        ref_id: str,
        remarks: str,
        particulars: str
    ) -> PaymentInitiationResult:
        amount_paisa = int(round(amount_npr * 100))
        token = self.generate_token(txn_id, txn_date, amount_paisa, ref_id, remarks, particulars)

        form_fields = {
            "MERCHANTID": self.config.merchant_id,
            "APPID": self.config.app_id,
            "APPNAME": self.config.app_name,
            "TXNID": txn_id,
            "TXNDATE": txn_date,
            "TXNCRNCY": "NPR",
            "TXNAMT": str(amount_paisa),
            "REFERENCEID": ref_id,
            "REMARKS": remarks,
            "PARTICULARS": particulars,
            "TOKEN": token
        }

        return PaymentInitiationResult(
            gateway="connectips",
            success=True,
            redirect_url=self.form_url,
            form_fields=form_fields,
            transaction_id=txn_id
        )

    def verify_payment(self, txn_id: str, txn_amt_paisa: int, ref_id: str) -> PaymentVerificationResult:
        token_msg = f"MERCHANTID={self.config.merchant_id},APPID={self.config.app_id},REFERENCEID={ref_id},TXNAMT={txn_amt_paisa}"
        secret = self.config.cert_path_or_secret.encode("utf-8")
        token = hmac.new(secret, token_msg.encode("utf-8"), hashlib.sha256).hexdigest()

        payload = {
            "merchantId": self.config.merchant_id,
            "appId": self.config.app_id,
            "referenceId": ref_id,
            "txnAmt": txn_amt_paisa,
            "token": token
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.config.password}"
        }

        req = urllib.request.Request(
            self.validate_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                status = data.get("status", "")
                is_valid = status.upper() == "SUCCESS"
                return PaymentVerificationResult(
                    gateway="connectips",
                    is_valid=is_valid,
                    status=status,
                    transaction_id=txn_id,
                    amount=float(txn_amt_paisa) / 100.0,
                    reference_id=ref_id,
                    raw_data=data
                )
        except urllib.error.HTTPError as e:
            return PaymentVerificationResult(
                gateway="connectips",
                is_valid=False,
                status="ERROR",
                transaction_id=txn_id,
                amount=float(txn_amt_paisa) / 100.0,
                error_message=f"HTTP {e.code}: {e.read().decode('utf-8')}"
            )
        except Exception as e:
            return PaymentVerificationResult(
                gateway="connectips",
                is_valid=False,
                status="ERROR",
                transaction_id=txn_id,
                amount=float(txn_amt_paisa) / 100.0,
                error_message=str(e)
            )
