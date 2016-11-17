import math
import os
import sys
from textcompare import TextDoc, metric
import matplotlib.pyplot as plt

normalize_by_avg = False
display_graph = False

def print_vocabulary_sizes(directory_name):
  textdocs = []
  for filename in os.listdir(directory_name):
    if filename == ".DS_Store":
      continue
    textdocs.append(TextDoc(os.path.join(directory_name, filename)))
  for textdoc in textdocs:
    print "Vocabulary size for {0}: {1}".format(textdoc.get_title(), len(textdoc.get_frequencies()))

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

  new_words_max = float('-inf')
  new_words_avg = 0.0
  new_occurrences_max = float('-inf')
  new_occurrences_avg = 0.0
  num_nonnegative_comparisons = 0
  for i in xrange(len(textdocs)):
    for j in xrange(len(textdocs)):
      if i == j:
        continue
      doc1 = textdocs[i]
      doc2 = textdocs[j]

      nw_dist = metric.asymmetric_metrics['New Words'].distance(doc1, doc2)
      new_words_max = max(new_words_max, nw_dist)

      no_dist = metric.asymmetric_metrics['New Occurrences'].distance(doc1, doc2)
      new_occurrences_max = max(new_occurrences_max, no_dist)

      if abs(nw_dist + 1.0) > 0.000000001:
        # Score wasn't -1
        new_words_avg += nw_dist
        new_occurrences_avg += no_dist
        num_nonnegative_comparisons += 1
  # NOTE: in the unlikely case where all comparisons return a score of -1, just
  # set the averages to 1, so they don't affect the scores.
  new_words_avg = (2.0 * new_words_avg)/num_nonnegative_comparisons if num_nonnegative_comparisons != 0 else 1
  new_occurrences_avg = (2.0 * new_occurrences_avg)/num_nonnegative_comparisons if num_nonnegative_comparisons != 0 else 1

  tversky_values = [0 for q in xrange(num_nonnegative_comparisons)]
  tversky_value_index = 0
  new_words_values = [0 for q in xrange(num_nonnegative_comparisons)]
  new_words_value_index = 0
  new_occurrences_values = [0 for q in xrange(num_nonnegative_comparisons)]
  new_occurrences_value_index = 0

  low_scores = {}
  low_pairs = {}
  high_scores = {}
  high_pairs = {}
  for m in metric.asymmetric_metrics:
    low_scores[m] = float("inf")
    low_pairs[m] = "INITIAL VALUE"
    high_scores[m] = float("-inf")
    high_pairs[m] = "INITIAL VALUE"

  low_scores['combined metric'] = float("inf")
  low_pairs['combined metric'] = "INITIAL VALUE"
  high_scores['combined metric'] = float("-inf")
  high_pairs['combined metric'] = "INITIAL VALUE"

  # Iterate over textdocs pairwise and compare them.
  for i in xrange(len(textdocs)):
    for j in xrange(len(textdocs)):
      if i == j:
        continue
      doc1 = textdocs[i]
      doc2 = textdocs[j]
      if not display_graph:
        print "Comparing {0} and {1}".format(doc1.title, doc2.title)
      common_words = set(doc1.get_frequencies().keys()) & set(doc2.get_frequencies().keys())
      f1 = doc1.get_frequencies()
      f2 = doc2.get_frequencies()
      if not display_graph:
        print "Listing common words and their frequencies (the order of frequencies is the same as the order the book titles were listed)"
        for word in common_words:
          print "Word: '{0}'\tFrequencies: {1}, {2}".format(word, f1[word], f2[word])
      for m in metric.asymmetric_metrics:
        # perform logic for comparing doc1 and doc2
        d = metric.asymmetric_metrics[m].distance(doc1, doc2)

        if d == -1:
          # Ignore books with no words in common.
          if not display_graph:
            print "Using metric ", m, ":", d
          continue

        if m == 'New Words':
          # Normalize
          if normalize_by_avg:
            d = d / new_words_avg
          else:
            d = d / new_words_max
          if display_graph:
            new_words_values[new_words_value_index] = d
            new_words_value_index += 1
        elif m == 'New Occurrences':
          # Normalize
          if normalize_by_avg:
            d = d / new_occurrences_avg
          else:
            d = d / new_occurrences_max
          if display_graph:
            new_occurrences_values[new_occurrences_value_index] = d
            new_occurrences_value_index += 1
        elif m == 'Tversky index':
          if display_graph:
            tversky_values[tversky_value_index] = d
            tversky_value_index += 1
        if not display_graph:
          print "Using metric ", m, ":", d
        if d < low_scores[m]:
          low_scores[m] = d
          low_pairs[m] = "{0} and {1}".format(doc1.title, doc2.title)
        if d > high_scores[m]:
          high_scores[m] = d
          high_pairs[m] = "{0} and {1}".format(doc1.title, doc2.title)
      d1 = metric.asymmetric_metrics['Tversky index'].distance(doc1, doc2)
      d2 = metric.asymmetric_metrics['New Words'].distance(doc1, doc2)/new_words_max
      d3 = metric.asymmetric_metrics['New Occurrences'].distance(doc1, doc2)/new_occurrences_max
      combined_score = -1
      if d1 >= 0 and d2 >= 0 and d3 >= 0:
        # No negative terms that occur when there's no overlap
        combined_score = (d1 + d2 + d3)/3.0
        if combined_score < low_scores['combined metric']:
          low_scores['combined metric'] = combined_score
          low_pairs['combined metric'] = "{0} and {1}".format(doc1.title, doc2.title)
        if combined_score > high_scores['combined metric']:
          high_scores['combined metric'] = combined_score
          high_pairs['combined metric'] = "{0} and {1}".format(doc1.title, doc2.title)

      if not display_graph:
        print "Using metric combined metric ", combined_score
        print "--------------------------------------------------------------------------------\n"
  print "Total Results Per Metric:"
  for m in metric.asymmetric_metrics:
    print m
    print "Low:  {0} ({1})".format(low_scores[m], low_pairs[m])
    print "High: {0} ({1})\n".format(high_scores[m], high_pairs[m])
  print "combined metric"
  print "Low:  {0} ({1})".format(low_scores['combined metric'], low_pairs['combined metric'])
  print "High: {0} ({1})\n".format(high_scores['combined metric'], high_pairs['combined metric'])

  if display_graph:
    print "Graphing results."
    plt.plot(tversky_values, 'r')
    plt.plot(new_words_values, 'g')
    plt.plot(new_occurrences_values, 'b')
    plt.legend(['Tversky', 'New Words', 'New Occurrences'])
    plt.show()

if __name__ == "__main__":
  default_filepath = "/Users/{0}/Dropbox (MIT)/children's books/books/".format(os.environ['USER'])

  if len(sys.argv) == 2:
    print "NOTE: Not specifying a path will only work for OS X. If using a differnt OS, please specify the filepath to the directory containing the books to be compared."
    print "No arguments were provided. Using default path of: {0}\n".format(default_filepath)
  elif len(sys.argv) == 1:
    print "Since no argument was specified, printing vocabulary size of all books in directory {0}.".format(default_filepath)
  elif len(sys.argv) != 3:
    print "Incorrect usage. Must specify 0, 1 or 2 arguments. If 0 arguments are specified, then the program will print the vocabulary size of all books in the default directory ({0}). If 2 arguments are specified, the last is used as the filepath for finding the text files. Otherwise, {0} is used. The first argument specifies what operation is to be performed: 'v' for vocabulary size, or 'a' for asymmetric comparisons.".format(default_filepath)
    print "Exiting."
    sys.exit(0)

  filepath = default_filepath if len(sys.argv) <= 2 else sys.argv[2]
  if len(sys.argv) > 1:
    if sys.argv[1] == 'a':
      # asymmetric comparisons
      compare_files(filepath)
    elif sys.argv[1] == 'v':
      # print vocabulary sizes
      print_vocabulary_sizes(filepath)
    else:
      print "Unknown operation specified: {0}\nThe valid operations are 'v', for printing vocabulary size, or 'a', for performing asymmetric sort operations on all pairs of books."
      print "Exiting."
      sys.exit(0)
  else:
    # Use all default values: i.e. print vocabulary size of all books in default directory.
    print_vocabulary_sizes(filepath)
