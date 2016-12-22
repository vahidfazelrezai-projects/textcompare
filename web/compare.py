import math
import os
import sys
from textcompare import TextDoc, metric

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

def initialize(directory_name):
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

  return textdocs, metric

def get_graph(textdocs, metric, metric_name):
    ids = []
    nodes = {}
    id_map = {}
    id_counter = 1
    for doc in textdocs:
        num_words = len(doc.get_frequencies().keys())
        ids.append(id_counter)
        nodes[id_counter] = (doc.get_title(), num_words)
        id_map[doc] = id_counter
        id_counter += 1

    edges = {}
    if metric_name in metric.metrics:
        m = metric.metrics[metric_name]
    elif metric_name in metric.asymmetric_metrics:
        m = metric.asymmetric_metrics[metric_name]
    else:
        return
    for i in xrange(len(textdocs)):
        for j in xrange(i+1, len(textdocs)):
            doc1 = textdocs[i]
            doc2 = textdocs[j]
            edges[(id_map[doc1], id_map[doc2])] = m.distance(doc1, doc2)
            edges[(id_map[doc2], id_map[doc1])] = m.distance(doc2, doc1)

    return {
        'ids': ids,
        'nodes': nodes,
        'edges': edges
    }
