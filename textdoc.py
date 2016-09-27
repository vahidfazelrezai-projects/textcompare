# A class representing a book file that has been read.
# The stored state are the title, author, isbn, and a map from word to
# frequency.
class TextDoc:
  def __init__(self, filepath):
    doc = open(filepath, 'r')
    self.title = doc.readline()[:-1]
    self.author = doc.readline()[:-1]
    self.isbn = doc.readline()[:-1]
    if doc.readline() != ">>>>>\n":
      print "File not formatted correctly."

    self.frequencies = {}
    # Read the actual content of the story.
    for line in doc:
      # Convert all words to lowercase
      words = map(lambda s: s.lower(), line.split())
      for word in words:
        w = word
        # Get rid of starting punctuation
        while len(w) > 0 and not w[0].isalpha():
          w = w[1:]
        # Get rid of trailing punctuation
        while len(w) > 0 and not w[-1].isalpha():
          w = w[:-1]
        if len(w) == 0:
          continue
        if w in self.frequencies:
          self.frequencies[w] += 1
        else:
          self.frequencies[w] = 1

  def get_frequencies(self):
    return self.frequencies

  def get_author(self):
    return self.author

  def get_title(self):
    return self.title

  def get_isbn(self):
    return self.isbn

# Test
#t = TextDoc("./data/books/Corduroy.txt")
#print t.frequencies
#print t.get_author()
#print t.get_title()
