import sys
import argparse
import json
from .client import NepalPay
from .types import Environment, EsewaConfig
from .gateways.esewa import EsewaGateway
from .gateways.nepalqr import NepalQRGenerator
from .utils.qr import QRCodeGenerator

def main():
    parser = argparse.ArgumentParser(
        prog="nepalpay",
        description="Unified, Zero-Dependency Nepal Payments CLI (eSewa, Khalti, ConnectIPS, IME Pay, NepalQR)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: qr
    qr_parser = subparsers.add_parser("qr", help="Generate scannable Terminal NepalQR code")
    qr_parser.add_argument("--amount", type=float, default=100.0, help="Amount in NPR")
    qr_parser.add_argument("--name", type=str, default="Merchant Store", help="Merchant Name")
    qr_parser.add_argument("--city", type=str, default="Kathmandu", help="Merchant City")
    qr_parser.add_argument("--order", type=str, default="ORD-001", help="Order reference ID")
    qr_parser.add_argument("--mid", type=str, default="NP01TESTMERCHANT", help="Merchant ID")

    # Command: esewa
    esewa_parser = subparsers.add_parser("esewa", help="Generate eSewa ePaisa V2 signed test form fields")
    esewa_parser.add_argument("--amount", type=float, default=100.0, help="Amount in NPR")
    esewa_parser.add_argument("--order", type=str, default="ORD-001", help="Transaction UUID")
    esewa_parser.add_argument("--code", type=str, default="EPAYTEST", help="Product code")
    esewa_parser.add_argument("--secret", type=str, default="8gBm/:&EnhH.1/q", help="Secret key")

    # Command: verify
    verify_parser = subparsers.add_parser("verify-esewa", help="Verify eSewa V2 callback payload")
    verify_parser.add_argument("data", type=str, help="Base64 encoded response string from eSewa")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "qr":
        client = NepalPay(environment=Environment.TEST)
        res = client.generate_dynamic_qr(
            merchant_id=args.mid,
            amount=args.amount,
            merchant_name=args.name,
            merchant_city=args.city,
            bill_number=args.order,
            reference_id=args.order
        )
        print("\n=== NEPALQR TERMINAL PREVIEW ===")
        print(f"Merchant : {args.name} ({args.city})")
        print(f"Amount   : NPR {args.amount:.2f}")
        print(f"Order ID : {args.order}")
        print("Scannable via eSewa, Khalti, Fonepay, ConnectIPS & Mobile Banking:")
        print(res["terminal_qr"])
        print(f"\nRaw EMVCo Payload:\n{res['qr_string']}\n")

    elif args.command == "esewa":
        gateway = EsewaGateway(EsewaConfig(product_code=args.code, secret_key=args.secret))
        res = gateway.initiate_payment(
            amount=args.amount,
            transaction_uuid=args.order,
            success_url="https://example.com/payment/success",
            failure_url="https://example.com/payment/failure"
        )
        print("\n=== ESEWA EPAISA V2 TEST PAYLOAD ===")
        print(f"Redirect URL: {res.redirect_url}")
        print("Form Fields:")
        print(json.dumps(res.form_fields, indent=2))

    elif args.command == "verify-esewa":
        gateway = EsewaGateway()
        res = gateway.verify_payment(args.data)
        print("\n=== ESEWA VERIFICATION RESULT ===")
        print(f"Valid       : {res.is_valid}")
        print(f"Status      : {res.status}")
        print(f"Txn UUID    : {res.transaction_id}")
        print(f"Amount      : NPR {res.amount}")
        print(f"Ref Code    : {res.reference_id}")
        if res.error_message:
            print(f"Error       : {res.error_message}")

if __name__ == "__main__":
    main()
