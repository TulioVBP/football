class Accumulator:  # @save
    """For accumulating sums over `n` variables."""

    def __init__(self, n):
        """
        Args:
            n: number of variables"""
        self.data = [0.0] * n

    def add(self, *args):
        """Adds the arguments passed."""
        self.data = [a + float(b) for a, b in zip(self.data, args)]

    def reset(self):
        """ Resets the cummulative data."""
        self.data = [0.0] * len(self.data)

    def __getitem__(self, idx):
        """Returnd the requested item.
        Arg:
            idx: the index of requested item."""
        return self.data[idx]
