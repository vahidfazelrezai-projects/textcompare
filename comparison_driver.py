import math
import os
import sys
from textcompare import TextDoc, metric

# Given a list of TextDoc objects, returns a map from
# word -> log(number of docs / number of docs containing word)
# used by IDF
def get_idf_map(textdocs):
  m = {}
  N = float(len(textdocs))
  for doc in textdocs:
    for word in doc.get_frequencies():
      if word in m:
        m[word] += 1
      else:
        m[word] = 1
  idf_map = {}
  # Using log base 2 for now
  for word in m:
    idf_map[word] = 1 + math.log(N / m[word], 2)
  return idf_map

def get_ittf_map(textdocs):
  m = {}
  for doc in textdocs:
    frequencies = doc.get_frequencies()
    for word in frequencies:
      if word in m:
        m[word] += frequencies[word]
      else:
        m[word] = frequencies[word]
  total_words = 0.0
  for word in m:
    total_words += m[word]
  ittf_map = {}
  for word in m:
    ittf_map[word] = 1 + math.log(total_words / m[word], 2)
  return ittf_map

# Given a directory, compare all pairs of books in that directory using all the
# metrics in metric.metrics, plus TF-IDF, Sublinear TF-IDF, and TF-ITTF.
def compare_files(directory_name):
  textdocs = []
  for filename in os.listdir(directory_name):
    if filename == ".DS_Store":
      continue
    textdocs.append(TextDoc(os.path.join(directory_name, filename)))
  idf_map = get_idf_map(textdocs)
  ittf_map = get_ittf_map(textdocs)
  def idf_weight_fn(word):
    return idf_map[word]
  def ittf_weight_fn(word):
    return ittf_map[word]
  # Add metrics that require global knowledge of documents

  # Add the TF-IDF (Term Frequency Inverse Document Frequency) metric
  metric.metrics['TF-IDF'] = metric.Metric(metric.mult_fn, metric.unit_fn, metric.divide_by_magnitudes_fn, idf_weight_fn)
  # Add the sublinear TF-IDF metric
  metric.metrics['Sublinear TF-IDF'] = metric.Metric(metric.log_mult_fn, metric.unit_fn, metric.divide_by_log_magnitudes_fn, idf_weight_fn)
  # Add the TF-ITTF (Term Frequency Inverse Total Term Frequency) metric
  metric.metrics['TF-ITTF'] = metric.Metric(metric.mult_fn, metric.unit_fn, metric.divide_by_magnitudes_fn, ittf_weight_fn)

  low_scores = {}
  low_pairs = {}
  high_scores = {}
  high_pairs = {}
  for m in metric.metrics:
    low_scores[m] = float("inf")
    low_pairs[m] = "INITIAL VALUE"
    high_scores[m] = float("-inf")
    high_pairs[m] = "INITIAL VALUE"

  # Iterate over textdocs pairwise and compare them.
  for i in xrange(len(textdocs)):
    for j in xrange(i+1, len(textdocs)):
      doc1 = textdocs[i]
      doc2 = textdocs[j]
      print "Comparing {0} and {1}".format(doc1.title, doc2.title)
      common_words = set(doc1.get_frequencies().keys()) & set(doc2.get_frequencies().keys())
      f1 = doc1.get_frequencies()
      f2 = doc2.get_frequencies()
      print "Listing common words and their frequencies (the order of frequencies is the same as the order the book titles were listed)"
      for word in common_words:
        print "Word: '{0}'\tFrequencies: {1}, {2}".format(word, f1[word], f2[word])
      for m in metric.metrics:
        # perform logic for comparing doc1 and doc2
        d = metric.metrics[m].distance(doc1, doc2)
        print "Using metric ", m, ":", d
        if d == -1:
          # Ignore books with no words in common.
          continue
        if d < low_scores[m]:
          low_scores[m] = d
          low_pairs[m] = "{0} and {1}".format(doc1.title, doc2.title)
        if d > high_scores[m]:
          high_scores[m] = d
          high_pairs[m] = "{0} and {1}".format(doc1.title, doc2.title)
      print "--------------------------------------------------------------------------------\n"
  print "Total Results Per Metric:"
  for m in metric.metrics:
    print m
    print "Low:  {0} ({1})".format(low_scores[m], low_pairs[m])
    print "High: {0} ({1})\n".format(high_scores[m], high_pairs[m])

if __name__ == "__main__":
  default_filepath = "/Users/{0}/Dropbox (MIT)/children's books/books/".format(os.environ['USER'])

  if len(sys.argv) == 1:
    print "NOTE: Not specifying an argument will only work for OS X. If using a differnt OS, please specify the filepath to the directory containing the books to be compared."
    print "No arguments were provided. Using default path of: {0}\n".format(default_filepath)
  elif len(sys.argv) > 2:
    print "Incorrect usage. Must specify 1 or 0 arguments. If 1 argument is specified, that is used as the filepath for finding the text files. Otherwise, {0} is used".format(default_filepath)

  if len(sys.argv) == 2:
    compare_files(sys.argv[1])
  else:
    compare_files(default_filepath)
