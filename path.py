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
    order = []
    for i in range(n):
        scores = [(id, sum([edges[key] for key in edges.keys() if (key[0] == id and key[1] in ids)])) for id in ids]
        scores.sort(key=lambda x: x[1])
        cur_id = scores[0][0]
        order.append(cur_id)
        ids = [id for id in ids if id != cur_id]
    return [nodes[id][0] for id in order]

def order_asymmetric3(graph):
    ids = graph['ids']
    nodes = graph['nodes']
    edges = graph['edges']
    ids.sort(key=lambda id: sum([edges[key] for key in edges.keys() if key[1] == id]))
    return [nodes[id][0] for id in ids]

if __name__ == '__main__':
    metric_name = 'New Words'
    filepath = "/Users/{0}/Dropbox (MIT)/children's books/books/".format(os.environ['USER'])
    textdocs, metric = compare.initialize(filepath)
    graph = compare.get_graph(textdocs, metric, metric_name)
    print order_asymmetric1(graph)
    print order_asymmetric2(graph)
    print order_asymmetric3(graph)
