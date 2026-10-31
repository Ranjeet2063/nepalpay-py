"""
Universal Zero-Dependency Payment SDK for Nepal (Python, FastAPI, Django).
Supports eSewa, Khalti, ConnectIPS, IME Pay, Fonepay & NepalQR.
"""

from .client import NepalPay
from .types import (
    Environment,
    GatewayName,
    EsewaConfig,
    KhaltiConfig,
    ConnectIPSConfig,
    ImePayConfig,
    PaymentInitiationResult,
    PaymentVerificationResult
)
from .gateways.esewa import EsewaGateway
from .gateways.khalti import KhaltiGateway
from .gateways.connectips import ConnectIPSGateway
from .gateways.imepay import ImePayGateway
from .gateways.nepalqr import NepalQRGenerator
from .utils.qr import QRCodeGenerator
from .frameworks.fastapi import FastAPIPaymentHandler
from .frameworks.django import DjangoPaymentHandler

__version__ = "1.0.0"
__all__ = [
    "NepalPay",
    "Environment",
    "GatewayName",
    "EsewaConfig",
    "KhaltiConfig",
    "ConnectIPSConfig",
    "ImePayConfig",
    "PaymentInitiationResult",
    "PaymentVerificationResult",
    "EsewaGateway",
    "KhaltiGateway",
    "ConnectIPSGateway",
    "ImePayGateway",
    "NepalQRGenerator",
    "QRCodeGenerator",
    "FastAPIPaymentHandler",
    "DjangoPaymentHandler",
]
