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

# Test the functionality
# Can safely be deleted/commented out once satisfied with the performance.
if __name__ == "__main__":
  directory_path = "/Users/{0}/Dropbox (MIT)/children's books/books/".format(os.environ['USER'])
  textdocs = load_directory(directory_path)

  # The test vocabulary
  vocabulary = {'a', 'the', 'he', 'she', 'we', 'i', 'they', 'brown', 'bear', 'goes', 'face', 'people'}
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
