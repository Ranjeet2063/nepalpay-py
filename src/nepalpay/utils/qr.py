"""
Pure Python Zero-Dependency QR Code Matrix & Terminal ASCII/Unicode Renderer.
Ramanujan Mathematical Rigor: GF(256) Galois Field Arithmetic & Reed-Solomon Code.
"""

from typing import List, Tuple, Optional

# Galois Field GF(256) tables with primitive polynomial 0x11D (285)
EXP_TABLE = [0] * 512
LOG_TABLE = [0] * 256

x = 1
for i in range(255):
    EXP_TABLE[i] = x
    LOG_TABLE[x] = i
    x <<= 1
    if x >= 256:
        x ^= 0x11D

for i in range(255, 512):
    EXP_TABLE[i] = EXP_TABLE[i - 255]

def gf_mul(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return EXP_TABLE[LOG_TABLE[a] + LOG_TABLE[b]]

def rs_generator_poly(num_ec: int) -> List[int]:
    poly = [1]
    for i in range(num_ec):
        factor = [1, EXP_TABLE[i]]
        new_poly = [0] * (len(poly) + 1)
        for j in range(len(poly)):
            for k in range(len(factor)):
                new_poly[j + k] ^= gf_mul(poly[j], factor[k])
        poly = new_poly
    return poly

def rs_encode(msg: List[int], num_ec: int) -> List[int]:
    gen = rs_generator_poly(num_ec)
    rem = [0] * num_ec
    for b in msg:
        feedback = b ^ rem[0]
        rem = rem[1:] + [0]
        if feedback != 0:
            for j in range(num_ec):
                rem[j] ^= gf_mul(gen[j + 1], feedback)
    return rem

# Version capacity table for Byte Mode, Error Correction Level L
# (Version, total_codewords, ec_codewords, data_codewords, num_blocks)
VERSION_SPECS_L = [
    (1, 26, 7, 19, 1),
    (2, 44, 10, 34, 1),
    (3, 70, 15, 55, 1),
    (4, 100, 20, 80, 1),
    (5, 134, 26, 108, 1),
    (6, 172, 36, 136, 2),
    (7, 196, 40, 156, 2),
    (8, 242, 48, 194, 2),
    (9, 292, 60, 232, 2),
    (10, 346, 72, 274, 2),
    (11, 404, 80, 324, 4),
    (12, 466, 96, 370, 4),
    (13, 532, 104, 428, 4),
    (14, 581, 120, 461, 4),
]

ALIGNMENT_PATTERN_POS = {
    2: [6, 18],
    3: [6, 22],
    4: [6, 26],
    5: [6, 30],
    6: [6, 34],
    7: [6, 22, 38],
    8: [6, 24, 42],
    9: [6, 26, 46],
    10: [6, 28, 50],
    11: [6, 30, 54],
    12: [6, 32, 58],
    13: [6, 34, 62],
    14: [6, 26, 46, 66],
}

class BitBuffer:
    def __init__(self):
        self.buffer: List[int] = []
        self.length = 0

    def put(self, num: int, length: int):
        for i in range(length - 1, -1, -1):
            bit = (num >> i) & 1
            self.buffer.append(bit)
            self.length += 1

    def to_bytes(self) -> List[int]:
        res = []
        for i in range(0, self.length, 8):
            byte = 0
            for j in range(8):
                if i + j < self.length:
                    byte = (byte << 1) | self.buffer[i + j]
                else:
                    byte = byte << 1
            res.append(byte)
        return res

class QRCodeGenerator:
    """
    Zero-dependency pure Python QR Code Generator.
    Supports Versions 1 to 14, Byte Mode, EC Level L, Mask 0.
    """

    def __init__(self, data: str):
        self.raw_data = data.encode("utf-8")
        self.version = self._select_version(len(self.raw_data))
        self.size = self.version * 4 + 17
        self.modules: List[List[Optional[bool]]] = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.is_function: List[List[bool]] = [[False for _ in range(self.size)] for _ in range(self.size)]

    def _select_version(self, data_len: int) -> int:
        for ver, _, _, data_cap, _ in VERSION_SPECS_L:
            # overhead: mode indicator (4) + character count (8 or 16)
            overhead = 2 if ver < 10 else 3
            if data_len + overhead <= data_cap:
                return ver
        raise ValueError(f"Data exceeds capacity of QR Version 14 ({data_len} bytes)")

    def _get_spec(self):
        for spec in VERSION_SPECS_L:
            if spec[0] == self.version:
                return spec
        return VERSION_SPECS_L[0]

    def _encode_data(self) -> List[int]:
        spec = self._get_spec()
        data_cap = spec[3]
        total_ec = spec[2]
        num_blocks = spec[4]

        bb = BitBuffer()
        # Mode indicator: 0100 (Byte mode)
        bb.put(0b0100, 4)
        # Character count indicator
        count_bits = 16 if self.version >= 10 else 8
        bb.put(len(self.raw_data), count_bits)
        # Data bytes
        for b in self.raw_data:
            bb.put(b, 8)

        # Terminator
        needed_bits = data_cap * 8
        term_len = min(4, needed_bits - bb.length)
        if term_len > 0:
            bb.put(0, term_len)

        # Padding to byte boundary
        rem = bb.length % 8
        if rem != 0:
            bb.put(0, 8 - rem)

        data_bytes = bb.to_bytes()
        # Pad bytes 0xEC, 0x11
        pad_bytes = [0xEC, 0x11]
        pad_idx = 0
        while len(data_bytes) < data_cap:
            data_bytes.append(pad_bytes[pad_idx % 2])
            pad_idx += 1

        # Interleave blocks if num_blocks > 1
        block_data_len = data_cap // num_blocks
        block_ec_len = total_ec // num_blocks

        data_blocks = []
        ec_blocks = []
        for i in range(num_blocks):
            sub_data = data_bytes[i * block_data_len: (i + 1) * block_data_len]
            sub_ec = rs_encode(sub_data, block_ec_len)
            data_blocks.append(sub_data)
            ec_blocks.append(sub_ec)

        final_stream = []
        for col in range(block_data_len):
            for b in range(num_blocks):
                final_stream.append(data_blocks[b][col])

        for col in range(block_ec_len):
            for b in range(num_blocks):
                final_stream.append(ec_blocks[b][col])

        return final_stream

    def _setup_finder_pattern(self, row: int, col: int):
        for r in range(-1, 8):
            for c in range(-1, 8):
                if 0 <= row + r < self.size and 0 <= col + c < self.size:
                    val = (0 <= r <= 6 and (c in (0, 6) or r in (0, 6))) or (2 <= r <= 4 and 2 <= c <= 4)
                    self.modules[row + r][col + c] = val
                    self.is_function[row + r][col + c] = True

    def _setup_alignment_patterns(self):
        if self.version < 2:
            return
        positions = ALIGNMENT_PATTERN_POS.get(self.version, [])
        for r in positions:
            for c in positions:
                # Do not overlap with finder patterns
                if (r < 9 and c < 9) or (r < 9 and c >= self.size - 9) or (r >= self.size - 9 and c < 9):
                    continue
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        val = (abs(dr) == 2 or abs(dc) == 2 or (dr == 0 and dc == 0))
                        self.modules[r + dr][c + dc] = val
                        self.is_function[r + dr][c + dc] = True

    def _setup_timing_patterns(self):
        for i in range(8, self.size - 8):
            val = (i % 2 == 0)
            if not self.is_function[6][i]:
                self.modules[6][i] = val
                self.is_function[6][i] = True
            if not self.is_function[i][6]:
                self.modules[i][6] = val
                self.is_function[i][6] = True

    def _setup_format_info(self):
        # EC Level L: 01, Mask 000 -> 01000 = 8
        # Format info BCH(15, 5) with XOR mask 0x5412: for EC L, Mask 0 = 0x77C4 (0b111011111000100)
        format_bits = 0x77C4
        for i in range(15):
            bit = bool((format_bits >> i) & 1)
            # Top-left horizontal & vertical
            if i < 6:
                r, c = i, 8
            elif i < 8:
                r, c = i + 1, 8
            else:
                r, c = 8, 14 - i

            self.modules[r][c] = bit
            self.is_function[r][c] = True

            if i < 8:
                r2, c2 = 8, self.size - 1 - i
            else:
                r2, c2 = self.size - 15 + i, 8

            self.modules[r2][c2] = bit
            self.is_function[r2][c2] = True

        # Dark module
        self.modules[self.size - 8][8] = True
        self.is_function[self.size - 8][8] = True

    def generate_matrix(self) -> List[List[bool]]:
        # 1. Place finders
        self._setup_finder_pattern(0, 0)
        self._setup_finder_pattern(0, self.size - 7)
        self._setup_finder_pattern(self.size - 7, 0)

        # 2. Alignment & Timing
        self._setup_alignment_patterns()
        self._setup_timing_patterns()
        self._setup_format_info()

        # 3. Data placement in zigzag columns
        data = self._encode_data()
        bit_idx = 0
        total_bits = len(data) * 8

        row = self.size - 1
        col = self.size - 1
        direction = -1

        while col > 0:
            if col == 6:
                col -= 1

            for c in range(2):
                curr_col = col - c
                if not self.is_function[row][curr_col]:
                    bit = False
                    if bit_idx < total_bits:
                        byte_val = data[bit_idx // 8]
                        bit = bool((byte_val >> (7 - (bit_idx % 8))) & 1)
                        bit_idx += 1

                    # Apply Mask 0: (row + col) % 2 == 0
                    mask = ((row + curr_col) % 2 == 0)
                    self.modules[row][curr_col] = bit ^ mask

            row += direction
            if row < 0 or row >= self.size:
                direction = -direction
                row += direction
                col -= 2

        return [[bool(cell) for cell in r] for r in self.modules]

    def render_terminal(self, border: int = 2) -> str:
        """
        Renders QR code matrix into Unicode half-block characters (▀, ▄, █, ' ')
        for crisp scannable high-contrast terminal display.
        """
        matrix = self.generate_matrix()
        w = len(matrix)
        total_w = w + border * 2
        
        # Build expanded grid with white quiet-zone (False)
        grid = [[False] * total_w for _ in range(total_w)]
        for r in range(w):
            for c in range(w):
                grid[r + border][c + border] = matrix[r][c]

        lines = []
        for r in range(0, total_w, 2):
            line = []
            for c in range(total_w):
                top = grid[r][c]
                bot = grid[r + 1][c] if r + 1 < total_w else False
                if top and bot:
                    line.append("█")
                elif top and not bot:
                    line.append("▀")
                elif not top and bot:
                    line.append("▄")
                else:
                    line.append(" ")
            lines.append("".join(line))
        return "\n".join(lines)
