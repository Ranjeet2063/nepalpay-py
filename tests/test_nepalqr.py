from nepalpay import NepalQRGenerator
from nepalpay.gateways.nepalqr import calculate_crc16_ccitt

def test_crc16_calculation():
    # Standard EMVCo test string
    test_str = "0002010102126304"
    crc = calculate_crc16_ccitt(test_str)
    assert len(crc) == 4
    assert crc.isalnum()

def test_generate_emvco_payload():
    payload = NepalQRGenerator.generate_emvco_payload(
        merchant_id="NP01MERCHANT",
        amount=1250.50,
        merchant_name="Annapurna Cafe",
        merchant_city="Pokhara",
        bill_number="BILL-7788",
        reference_id="REF-9900"
    )

    assert payload.startswith("000201010212")
    assert "Annapurna Cafe" in payload
    assert "Pokhara" in payload
    assert "1250.50" in payload
    assert "BILL-7788" in payload
    assert "6304" in payload
    # Verify CRC is at the end (last 4 chars)
    crc_part = payload[-4:]
    data_part = payload[:-4]
    assert calculate_crc16_ccitt(data_part) == crc_part
