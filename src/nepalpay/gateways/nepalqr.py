from typing import Optional, Dict

def calculate_crc16_ccitt(data: str) -> str:
    """
    EMVCo CRC-16/CCITT calculation.
    Polynomial: 0x1021, Initial: 0xFFFF.
    Returns 4-character uppercase hex string.
    """
    crc = 0xFFFF
    for char in data:
        code = ord(char)
        crc ^= (code << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"

def format_tlv(tag: str, value: str) -> str:
    length = f"{len(value):02d}"
    return f"{tag}{length}{value}"

class NepalQRGenerator:
    """
    NepalQR & Fonepay EMVCo Compliant Dynamic QR String Generator.
    Zero external dependencies.
    """

    @staticmethod
    def generate_emvco_payload(
        merchant_id: str,
        amount: float,
        merchant_name: str,
        merchant_city: str = "Kathmandu",
        merchant_category_code: str = "0000",
        bill_number: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> str:
        # 00: Payload Format Indicator
        # 01: Point of Initiation Method (12 = Dynamic)
        payload = ""
        payload += format_tlv("00", "01")
        payload += format_tlv("01", "12")

        # 26: Merchant Account Information (Nepal Clearing House / Fonepay standard)
        sub_tlv = format_tlv("00", "NP.NPI.MERCHANT") + format_tlv("01", merchant_id)
        payload += format_tlv("26", sub_tlv)

        # 52: Merchant Category Code
        payload += format_tlv("52", merchant_category_code)

        # 53: Transaction Currency (116 = NPR ISO 4217)
        payload += format_tlv("53", "116")

        # 54: Transaction Amount
        payload += format_tlv("54", f"{amount:.2f}")

        # 58: Country Code
        payload += format_tlv("58", "NP")

        # 59: Merchant Name
        payload += format_tlv("59", merchant_name[:25])

        # 60: Merchant City
        payload += format_tlv("60", merchant_city[:15])

        # 62: Additional Data Field Template
        add_data = ""
        if bill_number:
            add_data += format_tlv("01", bill_number[:25])
        if reference_id:
            add_data += format_tlv("05", reference_id[:25])
        if add_data:
            payload += format_tlv("62", add_data)

        # 63: CRC placeholder
        payload_for_crc = payload + "6304"
        crc = calculate_crc16_ccitt(payload_for_crc)
        return payload_for_crc + crc
