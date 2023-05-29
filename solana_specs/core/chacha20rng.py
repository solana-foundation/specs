import struct
from .chacha20 import chacha20_block


class ChaCha20Rng:
    def __init__(self, key):
        self.key = key
        self.buf = bytearray()
        self.idx = 0

    def refill(self):
        self.buf += chacha20_block(self.key, self.idx, b"\x00" * 12)
        self.idx += 1

    def next_u64(self):
        if len(self.buf) < 8:
            self.refill()
        ret = struct.unpack("<Q", self.buf[:8])[0]
        self.buf = self.buf[8:]
        return ret

    def roll_u64(self, max):
        r = (2**64 - max) % max
        zone = 2**64 - 1 - r
        while True:
            v = self.next_u64()
            res = v * max
            hi = res >> 64
            lo = res & (2**64 - 1)
            if lo <= zone:
                return hi


def test():
    key = bytes.fromhex(
        "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
    )
    rng = ChaCha20Rng(key)
    assert rng.next_u64() == 0x6A19C5D97D2BFD39
    for _ in range(100000):
        rng.next_u64()
    assert rng.next_u64() == 0xF4682B7E28EAE4A7


if __name__ == "__main__":
    test()
