class Metric:
    # Function signatures for arguments are as follows:
    # num_fn(freq1, freq2) # numerator
    # den_fn(freq1, freq2) # denominator
    # mod_fn(d, words1, words2) # modifier
    def __init__(self, num_fn, den_fn, mod_fn):
        self.num_fn = num_fn
        self.den_fn = den_fn
        self.mod_fn = mod_fn

    # Given two documents doc1 and doc2 returns the distance defined as follows:
    # distance = mult * [sum over common words](num / den)
    # Returns -1 if the two documents have no words in common.
    def distance(self, doc1, doc2):
        d = 0
        words1 = doc1.get_frequencies()
        words2 = doc2.get_frequencies()
        common_words = set(words1.keys()) & set(words2.keys())
        if len(common_words) == 0:
            return -1
        for word in common_words:
            num = float(self.num_fn(words1[word], words2[word]))
            den = float(self.den_fn(words1[word], words2[word]))
            d += num / den
        d = float(self.mod_fn(d, words1, words2))
        return d

# Numerator functions
def diff_fn(freq1, freq2):
    return abs(freq1 - freq2)

# Denominator functions
def sum_fn(freq1, freq2):
    return freq1 + freq2

def unit_fn(freq1, freq2):
    return 1

# Modifier functions
def identity_fn(d, words1, words2):
    return d

def divide_sum_fn(d, words1, words2):
    common_words = set(words1.keys()) & set(words2.keys())
    total = 0
    for word in common_words:
        total += words1[word] + words2[word]
    return d / total

# Map of names to metric instances
metrics = {
    'Canberra': Metric(diff_fn, sum_fn, identity_fn),
    'Sorenson': Metric(diff_fn, unit_fn, divide_sum_fn),
}
