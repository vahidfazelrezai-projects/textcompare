# Given three asymmetric metrics (Tversky index, new words, and new
# occurrences), optimize the 5 available weights: 
# w_tversky in [-1, 1]
#   alpha in [0, 1] s.t. alpha != beta
#   beta in [0, 1] s.t. alpha != beta
# w_new_words in [-1, 1]
# w_new_occurrences in [-1, 1]

#import comparison_driver2
import metric
import os
from textdoc import TextDoc

def get_documents(directory_name):
  textdocs = []
  for filename in os.listdir(directory_name):
    if filename == ".DS_Store":
      continue
    textdocs.append(TextDoc(os.path.join(directory_name, filename)))
  return textdocs

def get_range(low, high):
  val = low
  s = []
  while val <= high:
    s.append(val)
    val += 0.1
  return s

if __name__ == '__main__':
  weights = {
    'Tversky index' : get_range(-1, 1),
    'New Words' : get_range(-1, 1),
    'New Occurrences' : get_range(-1, 1),
    'alpha' : get_range(0, 1),
    'beta' : get_range(0, 1),
  }
  documents = get_documents("/Users/{0}/Dropbox (MIT)/children's books/training_set/".format(os.environ['USER']))

  print "Checkpoint 1"
  alpha_beta_to_tversky_scores = {}
  for alpha in weights['alpha']:
    metric.tversky_alpha = alpha
    for beta in weights['beta']:
      metric.tversky_beta = beta
      alpha_beta_to_tversky_scores[(alpha, beta)] = {}
      # first compare all pairs of books.
      for i in xrange(len(documents)):
        for j in xrange(len(documents)):
          if i == j:
            continue
          doc1 = documents[i]
          doc2 = documents[j]
          alpha_beta_to_tversky_scores[(alpha, beta)][(doc1.get_title(), doc2.get_title())] = metric.asymmetric_metrics['Tversky index'].distance(doc1, doc2)
  
  print "Checkpoint 2"
  metric_to_scores = {}
  max_scores = {'New Words': float('-inf'), 'New Occurrences': float('-inf')}
  # compute scores for the rest of the metrics
  for m in metric.asymmetric_metrics:
    if m == 'Tversky index':
      continue
    if m not in metric_to_scores:
      metric_to_scores[m] = {}

    for i in xrange(len(documents)):
      for j in xrange(len(documents)):
        if i == j:
          continue
        doc1 = documents[i]
        doc2 = documents[j]
        score = metric.asymmetric_metrics[m].distance(doc1, doc2)
        metric_to_scores[m][(doc1.get_title(), doc2.get_title())] = score
        if score > max_scores[m]:
          max_scores[m] = score

  # Normalize new words and new occurrences by dividing by the largest value
  for m in metric_to_scores:
    for key in metric_to_scores[m]:
      metric_to_scores[m][key] = float(metric_to_scores[m][key]) / max_scores[m]

  print "Checkpoint 3"
  max_combination = ''
  max_score = float('-inf')
  scores = {}
  # finally, compute the total scores for every combination of weights
  # we'll try to maximize score(hug -> wolstencroft) - score(corduroy -> wolstencroft)
  for alpha in weights['alpha']:
    for beta in weights['beta']:
      for w_tversky in weights['Tversky index']:
        for w_new_words in weights['New Words']:
          for w_new_occurrences in weights['New Occurrences']:
            total_score = 0
            for i in xrange(len(documents)):
              for j in xrange(len(documents)):
                if i == j:
                  continue
                title1 = documents[i].get_title()
                title2 = documents[j].get_title()
                score = w_tversky * alpha_beta_to_tversky_scores[(alpha, beta)][(title1, title2)] + w_new_words*metric_to_scores['New Words'][(title1, title2)] + w_new_occurrences*metric_to_scores['New Occurrences'][(title1, title2)]
                #scores[(alpha, beta, w_tversky, w_new_words, w_new_occurrences, title1, title2)] = score
                if title1 == "Hug" and title2 == "Wolstencroft the Bear":
                  total_score += score
                elif title1 == "Corduroy" and title2 == "Wolstencroft the Bear":
                  total_score -= score
                elif title1 == "Faster! Faster!" and title2 == "Hug":
                  total_score -= score
                elif title1 == "Corduroy" and title2 == "Brown Bear Brown Bear, What Do You See?":
                  total_score -= score
                elif title1 == "Brown Bear Brown Bear, What Do You See?" and title2 == "Wolstencroft the Bear":
                  total_score += score
                  #max_hug_to_wolstencroft = "alpha: {0}, beta: {1}, tversky: {2}, new words: {3}, new occurrences: {4}".format(alpha, beta, w_tversky, w_new_words, w_new_occurrences)
            if total_score > max_score:
              max_combination = "alpha: {0}, beta: {1}, tversky: {2}, new words: {3}, new occurrences: {4}".format(alpha, beta, w_tversky, w_new_words, w_new_occurrences)
              max_score = total_score

  print "Largest score:"
  print max_score
  print max_combination
