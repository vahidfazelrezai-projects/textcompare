import os
from textdoc import load_directory
from metric import generate_metrics

class Graph:
    def __init__(self, textdocs, metric):
        self.ids = []
        self.nodes = {}
        id_map = {}
        id_counter = 1
        for doc in textdocs:
            num_words = len(doc.get_frequencies().keys())
            self.ids.append(id_counter)
            self.nodes[id_counter] = doc.get_title()
            id_map[doc] = id_counter
            id_counter += 1

        self.edges = {}
        for i in xrange(len(textdocs)):
            for j in xrange(i+1, len(textdocs)):
                doc1 = textdocs[i]
                doc2 = textdocs[j]
                self.edges[(id_map[doc1], id_map[doc2])] = metric.distance(doc1, doc2)
                self.edges[(id_map[doc2], id_map[doc1])] = metric.distance(doc2, doc1)

    def get_ids(self):
        return self.ids

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges


def make_graph(directory_path = "/Users/{0}/Dropbox (MIT)/children's books/books/".format(os.environ['USER']), metric_name = 'New Words'):
    textdocs = load_directory(directory_path)
    metrics = generate_metrics(textdocs)
    graph = Graph(textdocs, metrics[metric_name])
    return graph


class Subgraph:
    def __init__(self, ids = [], nodes = {}, edges = {}):
        self.ids = ids
        self.nodes = nodes
        self.edges = edges

    def set_ids(self, ids):
        self.ids = ids

    def set_nodes(self, nodes):
        self.nodes = nodes

    def set_edges(self, edges):
        self.edges = edges

    def get_ids(self):
        return self.ids

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges
