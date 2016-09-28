import math
import os
import sys
from textdoc import TextDoc
import metric

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
  metric.metrics['Sublinear TF-IDF'] = metric.Metric(metric.log_mult_fn, metric.unit_fn, metric.divide_by_magnitudes_fn, idf_weight_fn)
  # Add the TF-ITTF (Term Frequency Inverse Total Term Frequency) metric
  metric.metrics['TF-ITTF'] = metric.Metric(metric.mult_fn, metric.unit_fn, metric.divide_by_magnitudes_fn, ittf_weight_fn)

  # Iterate over textdocs pairwise and compare them.
  for i in xrange(len(textdocs)):
    for j in xrange(i+1, len(textdocs)):
      doc1 = textdocs[i]
      doc2 = textdocs[j]
      print "Difference between {0} and {1}".format(doc1.title, doc2.title)
      for m in metric.metrics:
        # perform logic for comparing doc1 and doc2
        print "Using metric ", m, ":", metric.metrics[m].distance(doc1, doc2)
      print

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Incorrect usage: must be called with exactly one command-line argument (the directory name). Exiting."
  else:
    compare_files(sys.argv[1])
