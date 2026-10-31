from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, Union

class Environment(str, Enum):
    TEST = "test"
    PRODUCTION = "production"

class GatewayName(str, Enum):
    ESEWA = "esewa"
    KHALTI = "khalti"
    CONNECTIPS = "connectips"
    IMEPAY = "imepay"
    FONEPAY = "fonepay"

@dataclass
class EsewaConfig:
    product_code: str = "EPAYTEST"
    secret_key: str = "8gBm/:&EnhH.1/q"
    environment: Environment = Environment.TEST

@dataclass
class KhaltiConfig:
    secret_key: str
    public_key: Optional[str] = None
    environment: Environment = Environment.TEST

@dataclass
class ConnectIPSConfig:
    merchant_id: str
    app_id: str
    app_name: str
    password: str
    cert_path_or_secret: str
    environment: Environment = Environment.TEST

@dataclass
class ImePayConfig:
    merchant_code: str
    api_user: str
    password: str
    module: str = "MERCHANT"
    environment: Environment = Environment.TEST

@dataclass
class PaymentInitiationResult:
    gateway: str
    success: bool
    redirect_url: Optional[str] = None
    form_fields: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class PaymentVerificationResult:
    gateway: str
    is_valid: bool
    status: str
    transaction_id: str
    amount: float
    reference_id: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
