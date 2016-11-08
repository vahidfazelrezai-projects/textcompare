import compare
import os

# note: doesn't deal with d = -1 properly

# asymmetric1: sort by sum of all distances
def order_asymmetric1(graph):
    ids = graph['ids']
    nodes = graph['nodes']
    edges = graph['edges']
    ids.sort(key=lambda id: sum([edges[key] for key in edges.keys() if key[0] == id]))
    return [nodes[id][0] for id in ids]

# asymmetric2: greedily add nodes one by one
def order_asymmetric2(graph):
    ids = graph['ids']
    n = len(ids)
    nodes = graph['nodes']
    edges = graph['edges']
    table = [[0] * n] * n
    table[0] = [sum([edges[key] for key in edges.keys() if key[9] == ids[i]]) for i in range(n)]
    scores = [(id, sum([edges[key] for key in edges.keys() if key[0] == id])) for id in ids]
    # incomplete!

if __name__ == '__main__':
    metric_name = 'Tversky index'
    filepath = "/Users/{0}/Dropbox (MIT)/children's books/books/".format(os.environ['USER'])
    textdocs, metric = compare.initialize(filepath)
    graph = compare.get_graph(textdocs, metric, metric_name)
    print order_asymmetric1(graph)
    # print order_asymmetric2(graph)
