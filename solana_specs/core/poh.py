"""
Python pseudocode implementation of Solana proof-of-history.
"""

import hashlib


class Poh:
    def __init__(self, seed=bytes(32)):
        self.state = bytes(seed)

    def append(self):
        msg = hashlib.sha256()
        msg.update(self.state)
        self.state = msg.digest()

    def mixin(self, mixin):
        assert len(mixin) == 32
        msg = hashlib.sha256()
        msg.update(self.state)
        msg.update(mixin)
        self.state = msg.digest()


def test():
    poh = Poh()
    for _ in range(42):
        poh.append()
    poh.mixin(b"WAO.............................")
    assert (
        poh.state.hex()
        == "18a244914fc9d21673ed92fc9edfbc4b00a9d630af352e0d8a4cac5846a344ce"
    )


if __name__ == "__main__":
    test()
