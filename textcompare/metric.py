import math

tversky_alpha = 1.0
tversky_beta = 0.1

class Metric:
    # Function signatures for arguments are as follows:
    # num_fn(freq1, freq2) # numerator
    # den_fn(freq1, freq2) # denominator
    # mod_fn(d, words1, words2, weight_fn) # modifier
    # weight_fn(word) # function that maps from term to weight
    def __init__(self, num_fn, den_fn, mod_fn, weight_fn):
        self.num_fn = num_fn
        self.den_fn = den_fn
        self.mod_fn = mod_fn
        self.weight_fn = weight_fn

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
            d += ((self.weight_fn(word)**2) * (num / den))
        d = float(self.mod_fn(d, words1, words2, self.weight_fn))
        return d

# Numerator and denominator functions
def diff_fn(freq1, freq2):
    return abs(freq1 - freq2)

def diff_squared_fn(freq1, freq2):
    return (freq1 - freq2)**2

def sum_fn(freq1, freq2):
    return freq1 + freq2

def unit_fn(freq1, freq2):
    return 1

def mult_fn(freq1, freq2):
    return freq1 * freq2

def log_mult_fn(freq1, freq2):
  return (1 + math.log(freq1, 2)) * (1 + math.log(freq2, 2))

def freq2_fn(freq1, freq2):
  return freq2

# Modifier functions
def identity_fn(d, words1, words2, weight_fn):
    return d

def divide_sum_fn(d, words1, words2, weight_fn):
    common_words = set(words1.keys()) & set(words2.keys())
    total = 0
    for word in common_words:
        total += words1[word] + words2[word]
    return d / total

def sqrt_fn(d, words1, words2, weight_fn):
    return d**0.5

def jaccard_mod_fn(d, words1, words2, weight_fn):
    noncommon_words = (len(words1.keys()) - d) + (len(words2.keys()) - d)
    all_words = len(set(words1.keys()) | set(words2.keys()))
    return noncommon_words / all_words

def divide_by_magnitudes_fn(d, words1, words2, weight_fn):
  x = float(d) / ((reduce(lambda x,y: x + (weight_fn(y)*words1[y])**2, words1, 0)**.5) * (reduce(lambda x,y: x + (weight_fn(y)*words2[y])**2, words2, 0)**.5))
  return math.acos(max(-1.0, min(x, 1.0))) # Min and max are for rounding errors, like evaluating 1.0 as 1.0000000000001, etc.

def divide_by_log_magnitudes_fn(d, words1, words2, weight_fn):
  x = float(d) / ((reduce(lambda x,y: x + (weight_fn(y)*(1 + math.log(words1[y], 2)))**2, words1, 0)**.5) * (reduce(lambda x,y: x + (weight_fn(y)*(1 + math.log(words2[y], 2)))**2, words2, 0)**.5))
  return math.acos(max(-1.0, min(x, 1.0))) # Min and max are for rounding errors, like evaluating 1.0 as 1.0000000000001, etc.

def tversky_divide_fn(d, words1, words2, weight_fn):
  s1 = set(words1.keys())
  s2 = set(words2.keys())
  return 1 - d/(d + tversky_alpha*len(s1 - s2) + tversky_beta*(len(s2 - s1)))

def modified_tversky_divide_fn(d, words1, words2, weight_fn):
  s1 = set(words1.keys())
  s2 = set(words2.keys())
  size_diff = max(len(words2) - len(words1), 0)
  return 1 - (d + size_diff)/(d + size_diff + tversky_alpha*len(s1 - s2) + tversky_beta*((10 - len(s2 - s1))**2))

# Number of new words that would need to be learned to read book2 after reading book1.
def num_new_words_fn(d, words1, words2, weight_fn):
  s1 = set(words1.keys())
  s2 = set(words2.keys())
  return len(s2 - s1)

# Number of occurrences of new words when reading book2 after book1.
# To be used with freq2_fn as numerator function.
def num_new_occurrences_fn(d, words1, words2, weight_fn):
  # d represents the number of occurrences of all common words in book2.
  # So we just need to subtract this from the total number of words in book2.
  return (sum(words2[w] for w in words2) - d)

# Weight functions (these typically need to be defined in the class using the
# metrics, since they often require global knowledge of the documents).
def default_weight_fn(word):
  return 1

# Map of names to metric instances
metrics = {
    'Canberra': Metric(diff_fn, sum_fn, identity_fn, default_weight_fn),
    'Sorenson': Metric(diff_fn, unit_fn, divide_sum_fn, default_weight_fn),
    'Minkowski2': Metric(diff_squared_fn, unit_fn, sqrt_fn, default_weight_fn),
    'Jaccard': Metric(unit_fn, unit_fn, jaccard_mod_fn, default_weight_fn),
    'TF': Metric(mult_fn, unit_fn, divide_by_magnitudes_fn, default_weight_fn),
    'Sublinear TF': Metric(log_mult_fn, unit_fn, divide_by_log_magnitudes_fn, default_weight_fn),
}

asymmetric_metrics = {
  'Tversky index': Metric(unit_fn, unit_fn, modified_tversky_divide_fn, default_weight_fn),
  'New Words': Metric(unit_fn, unit_fn, num_new_words_fn, default_weight_fn),
  'New Occurrences': Metric(freq2_fn, unit_fn, num_new_occurrences_fn, default_weight_fn),
}
