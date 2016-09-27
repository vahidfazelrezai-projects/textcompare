import os
import sys
from textdoc import TextDoc
import metric

def compare_files(directory_name):
  textdocs = []
  for filename in os.listdir(directory_name):
    textdocs.append(TextDoc(os.path.join(directory_name, filename)))
  # Iterate over textdocs pairwise and compare them.
  for doc1 in textdocs:
    print doc1.get_author() # For testing; remove later
    for doc2 in textdocs:
      if doc1.get_title() == doc2.get_title():
        continue
      for m in metric.metrics:
        # perform logic for comparing doc1 and doc2
        print "Difference between ", doc1.title, " and ", doc2.title, " using metric ", m, ":", metric.metrics[m].distance(doc1, doc2)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Incorrect usage: must be called with exactly one command-line argument (the directory name). Exiting."
  else:
    compare_files(sys.argv[1])
