from bisect import bisect
from .chacha20rng import ChaCha20Rng


class WeightedIndex:
    def __init__(self, weights):
        self.cumulative_weight = 0
        self.indexed_weights = []
        for weight in weights:
            self.indexed_weights.append((self.cumulative_weight, weight))
            self.cumulative_weight += weight

    def lookup(self, x):
        if x >= self.cumulative_weight:
            return None
        return bisect(self.indexed_weights, x, key=lambda x: x[0]) - 1

    def sample(self, rng):
        return self.lookup(rng.roll_u64(self.cumulative_weight))


def test():
    assert WeightedIndex([1]).lookup(0) == 0
    assert WeightedIndex([1]).lookup(1) == None
    assert WeightedIndex([2, 3, 2]).lookup(0) == 0
    assert WeightedIndex([2, 3, 2]).lookup(1) == 0
    assert WeightedIndex([2, 3, 2]).lookup(2) == 1
    assert WeightedIndex([2, 3, 2]).lookup(5) == 2
    assert WeightedIndex([2, 3, 2]).lookup(6) == 2
    assert WeightedIndex([2, 3, 2]).lookup(7) == None


if __name__ == "__main__":
    test()
