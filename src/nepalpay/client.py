from typing import Optional, Dict, Any
from .types import (
    EsewaConfig,
    KhaltiConfig,
    ConnectIPSConfig,
    ImePayConfig,
    Environment,
    PaymentInitiationResult,
    PaymentVerificationResult,
    GatewayName
)
from .gateways.esewa import EsewaGateway
from .gateways.khalti import KhaltiGateway
from .gateways.connectips import ConnectIPSGateway
from .gateways.imepay import ImePayGateway
from .gateways.nepalqr import NepalQRGenerator
from .utils.qr import QRCodeGenerator

class NepalPay:
    """
    Universal Unified Client for Nepal Payments (Python).
    Supports eSewa, Khalti, ConnectIPS, IME Pay, Fonepay & NepalQR.
    Zero external dependencies.
    """

    def __init__(
        self,
        environment: Environment = Environment.TEST,
        esewa_config: Optional[EsewaConfig] = None,
        khalti_config: Optional[KhaltiConfig] = None,
        connectips_config: Optional[ConnectIPSConfig] = None,
        imepay_config: Optional[ImePayConfig] = None,
    ):
        self.environment = environment

        # eSewa default fallback
        cfg_esewa = esewa_config or EsewaConfig(environment=environment)
        self.esewa = EsewaGateway(cfg_esewa)

        self.khalti = KhaltiGateway(khalti_config) if khalti_config else None
        self.connectips = ConnectIPSGateway(connectips_config) if connectips_config else None
        self.imepay = ImePayGateway(imepay_config) if imepay_config else None

    def generate_dynamic_qr(
        self,
        merchant_id: str,
        amount: float,
        merchant_name: str,
        merchant_city: str = "Kathmandu",
        bill_number: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates EMVCo dynamic NepalQR payload and terminal ASCII/Unicode block string.
        """
        qr_string = NepalQRGenerator.generate_emvco_payload(
            merchant_id=merchant_id,
            amount=amount,
            merchant_name=merchant_name,
            merchant_city=merchant_city,
            bill_number=bill_number,
            reference_id=reference_id
        )

        qr_gen = QRCodeGenerator(qr_string)
        terminal_qr = qr_gen.render_terminal()

        return {
            "qr_string": qr_string,
            "terminal_qr": terminal_qr,
            "version": qr_gen.version,
            "size": qr_gen.size
        }
