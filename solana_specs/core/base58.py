BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(buf: bytes) -> str:
    b2 = int.from_bytes(buf, "big")
    b58 = ""
    while b2 > 0:
        b58 = str(BASE58_ALPHABET[b2 % 58]) + b58
        b2 //= 58
    pad = 0
    for b in buf:
        if b == 0:
            pad += 1
        else:
            break
    return "1" * pad + b58


def b58decode(str: str) -> bytes:
    b58 = 0
    j = 1
    for c in reversed(str):
        digit = BASE58_ALPHABET.find(c)
        assert digit != -1
        b58 += digit * j
        j *= 58
    b2 = b58.to_bytes((b58.bit_length() + 7) // 8, "big")
    pad = len(str) - len(str.lstrip("1"))
    return b"\x00" * pad + b2


def test():
    assert (
        b58decode("11111111111111111111111111111111").hex()
        == "0000000000000000000000000000000000000000000000000000000000000000"
    )
    assert (
        b58decode("Config1111111111111111111111111111111111111").hex()
        == "03064aa3002f74dcc86e43310f0c052af8c5da27f6104019a323efa000000000"
    )
    assert (
        b58decode("Certusm1sa411sMpV9FPqU5dXAYhmmhygvxJ23S6hJ24").hex()
        == "ad23766ddee6e99ca3340ee5beac0884c89ddbc74dfe248fea56135698bafdd1"
    )


if __name__ == "__main__":
    test()
