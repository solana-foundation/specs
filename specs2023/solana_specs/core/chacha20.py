import struct


def chacha20_quarter_round(state, a, b, c, d):
    state[a] = (state[a] + state[b]) & 0xFFFF_FFFF
    state[d] = state[d] ^ state[a]
    state[d] = ((state[d] << 16) & 0xFFFF_FFFF) | (state[d] >> 16)
    state[c] = (state[c] + state[d]) & 0xFFFF_FFFF
    state[b] = state[b] ^ state[c]
    state[b] = ((state[b] << 12) & 0xFFFF_FFFF) | (state[b] >> 20)
    state[a] = (state[a] + state[b]) & 0xFFFF_FFFF
    state[d] = state[d] ^ state[a]
    state[d] = ((state[d] << 8) & 0xFFFF_FFFF) | (state[d] >> 24)
    state[c] = (state[c] + state[d]) & 0xFFFF_FFFF
    state[b] = state[b] ^ state[c]
    state[b] = ((state[b] << 7) & 0xFFFF_FFFF) | (state[b] >> 25)


def chacha20_block(key, idx, nonce):
    key_parts = list(struct.unpack("<8I", key))
    nonce_parts = list(struct.unpack("<3I", nonce))

    state_pre = [0x61707865, 0x3320646E, 0x79622D32, 0x6B206574]
    state_pre += key_parts
    state_pre += [idx]
    state_pre += nonce_parts

    state = state_pre.copy()

    for _ in range(10):
        chacha20_quarter_round(state, 0, 4, 8, 12)
        chacha20_quarter_round(state, 1, 5, 9, 13)
        chacha20_quarter_round(state, 2, 6, 10, 14)
        chacha20_quarter_round(state, 3, 7, 11, 15)
        chacha20_quarter_round(state, 0, 5, 10, 15)
        chacha20_quarter_round(state, 1, 6, 11, 12)
        chacha20_quarter_round(state, 2, 7, 8, 13)
        chacha20_quarter_round(state, 3, 4, 9, 14)

    for i in range(16):
        state[i] = (state[i] + state_pre[i]) & 0xFFFF_FFFF
    return struct.pack("<16I", *state)


def test():
    key = bytes.fromhex(
        "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
    )
    nonce = bytes.fromhex("000000090000004a00000000")
    idx = 1
    expected = bytes.fromhex(
        "10f1e7e4d13b5915500fdd1fa32071c4c7d1f4c733c068030422aa9ac3d46c4ed2826446079faa0914c2d705d98b02a2b5129cd1de164eb9cbd083e8a2503c4e"
    )
    actual = chacha20_block(key, idx, nonce)
    assert actual == expected


if __name__ == "__main__":
    test()
