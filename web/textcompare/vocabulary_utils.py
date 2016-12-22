import math
import os
from textdoc import load_directory
from textdoc import TextDocFromWordSet
from metric import generate_metrics

# Given a list of books, a vocabulary, and a metric, return the book that is
# most similar to the vocabulary.
#
# Input:
# textdocs - a list of TextDoc objects representing the books
# vocabulary - a set of words that are known
# metric - the metric to be used to compare the vocabulary to each of the books
# 
# Output:
# the TextDoc that is most similar to the vocabulary
def find_closest_book(textdocs, vocabulary, metric):
  # A book representing the vocabulary.
  vocab_book = TextDocFromWordSet(vocabulary)

  # Initial values
  closest = textdocs[0]
  closest_score = float('inf')

  # Find the closest book
  for textdoc in textdocs:
    d = metric.distance(vocab_book, textdoc)
    if d < closest_score:
      closest_score = d
      closest = textdoc

  print "Lowest score: ",closest_score
  print vocab_book.get_frequencies()
  return closest

# Given a list of books, a vocabulary, and an asymmetric metric, return a list
# of books that are more difficult than the vocabulary.
#
# Input:
# textdocs - a list of TextDoc objects representing the books
# vocabulary - a set of words that are known
# metric - the metric to be used to compare the vocabulary to each of the
# books. NOTE: must be an asymmetric metric.
#
# Output:
# a list of books more difficult than the book represented by vocabulary. Here,
# A is considered more difficult than B iff M(A, B) < M(B, A), where M is the
# metric being used.
def get_harder_books(textdocs, vocabulary, metric):
  # A book representing the vocabulary.
  vocab_book = TextDocFromWordSet(vocabulary)

  harder_books = []

  for textdoc in textdocs:
    if metric.distance(textdoc, vocab_book) < metric.distance(vocab_book, textdoc):
      #print "Going from ", textdoc.get_title(), " to Vocab Book: ", metric.distance(textdoc, vocab_book)
      #print "Going from Vocab Book to ", textdoc.get_title(), ": ", metric.distance(vocab_book, textdoc)
      harder_books.append(textdoc)

  return harder_books

# Returns a mapping from word to difficulty score, where a higher difficulty
# score denotes a harder word.
#
# Input:
# None
#
# Output:
# map from word to difficulty score, where difficulty scores are in the range
# [1, num_difficulty_levels]
#
# NOTE: not every english word will be in this map. The function using the map
# must handle cases where a word is not in this map.
# Also, the current file does not work well for our purpose. It's based on the
# most common words used on TV, so it's not very good for estimating the
# difficulty of words found in children's books.
def get_difficulty_scores():
  # Determines how many difficulty levels there are.
  num_difficulty_levels = 10
  doc = open('../word_frequencies/english_50k.txt', 'r')
  freq = {}
  max_freq = float('-inf')
  min_freq = float('inf')
  
  for line in doc:
    word, count = line.lower().strip().split()
    count = int(count)
    # Use logarithmic scale, since the dropoff in frequencies is quite steep.
    count = math.log(count)
    freq[word] = count
    max_freq = max(count, max_freq)
    min_freq = min(count, min_freq)

  # discretize into num_difficulty_levels, ranging from 1 to num_difficulty_levels
  interval = float(max_freq - min_freq)/num_difficulty_levels
  for word in freq:
    # The subtraction is so that 1 means easier, and num_difficulty_levels
    # menas harder.
    freq[word] = num_difficulty_levels + 1 - math.ceil((freq[word] - min_freq)/interval)
  return freq

# For a given book, returns the difficulty of the book, where difficulty is
# defined as the difficulty level of the average word.
def get_difficulty_score(book, scores):
  frequencies = book.get_frequencies()
  #size = float(len(frequencies))

  # Number of total words (not unique words) in the book.
  size = 0.0
  difficulty = 0.0
  for word in frequencies:
    multiplier = scores[word] if word in scores else 1
    difficulty += frequencies[word] * multiplier
    size += frequencies[word]
  return difficulty / size

# Returns the closest book found by using the difficulty metric of comparing
# the difficulty level of the average word in the book to the difficulty of
# the average word in the vocabulary.
def find_closest_book_by_difficulty(textdocs, vocabulary):
  scores = get_difficulty_scores()
  v = TextDocFromWordSet(vocabulary)
  vocab_difficulty = get_difficulty_score(v, scores)
  print "Vocab difficulty: ", vocab_difficulty
  closest_score = float('inf')
  closest_book = None
  for book in textdocs:
    s = get_difficulty_score(book, scores)
    print "difficulty of {0}: {1}".format(book.get_title(), s)
    if abs(s - vocab_difficulty) < abs(closest_score - vocab_difficulty):
      closest_score = s
      closest_book = book
  return closest_book

# Test the functionality
# Can safely be deleted/commented out once satisfied with the performance.
if __name__ == "__main__":
  directory_path = "/Users/{0}/Dropbox (MIT)/children's books/books/".format(os.environ['USER'])
  textdocs = load_directory(directory_path)

  # The test vocabulary
  #vocabulary = {'a', 'the', 'he', 'she', 'we', 'i', 'they', 'brown', 'bear', 'goes', 'face', 'people'}
  vocabulary = {'ball', 'cheese', 'sun', 'frog', 'mine', 'no', 'apple'}
  metrics = generate_metrics(textdocs)
  metric = metrics['TF-IDF']
  book = find_closest_book(textdocs, vocabulary, metric)
  print "Closest book: ", book.get_title()

  asymmetric_metric = metrics['Original New Words']
  harder_books = get_harder_books(textdocs, vocabulary, asymmetric_metric)
  print "Harder books: "
  for book in harder_books:
    print book.get_title()
  print "Number of harder books: {0}".format(len(harder_books))
  print "----------------------------------------------------------------------"

  print "Easier books: "
  harder_set = set(harder_books)
  for book in textdocs:
    if book in harder_set:
      continue
    print book.get_title()
  f = get_difficulty_scores()
  print "difficulty of hello: ", f['hello']
  print "difficulty of metabolism: ", f['metabolism']
  print "difficulty of you: ", f['you']
  print "difficulty of bear: ", f['bear']
  print "difficulty of baby: ", f['baby']
  print "difficulty of dog: ", f['dog']
  print "difficulty of i: ", f['i']
  b = find_closest_book_by_difficulty(textdocs, vocabulary).get_title()
  print "The closest book is: ", b
