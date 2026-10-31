from nepalpay import QRCodeGenerator
from nepalpay.utils.qr import gf_mul, rs_encode

def test_galois_field_multiplication():
    # In GF(256), a * 1 = a, a * 0 = 0
    assert gf_mul(15, 1) == 15
    assert gf_mul(255, 0) == 0
    assert gf_mul(0, 100) == 0
    # GF(256) commutative
    assert gf_mul(45, 87) == gf_mul(87, 45)

def test_reed_solomon_encoding():
    msg = [16, 32, 12, 86]
    ec = rs_encode(msg, 7)
    assert len(ec) == 7
    assert all(0 <= b < 256 for b in ec)

def test_qr_matrix_generation():
    qr = QRCodeGenerator("https://nepalpay.dev")
    matrix = qr.generate_matrix()
    size = qr.size
    assert len(matrix) == size
    assert all(len(row) == size for row in matrix)

    # Check top-left finder pattern corner is black
    assert matrix[0][0] is True
    assert matrix[6][0] is True
    assert matrix[0][6] is True

def test_terminal_renderer():
    qr = QRCodeGenerator("TEST_NEPALQR_100")
    rendered = qr.render_terminal(border=1)
    assert isinstance(rendered, str)
    assert len(rendered) > 0
    # Must contain Unicode block characters
    assert any(c in rendered for c in ("▀", "▄", "█"))
