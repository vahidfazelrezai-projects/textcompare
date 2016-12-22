import os
from textcompare import *

# run in command line to allow easy opening of files in sequence
def read(directory_path, name_list):
    for name in name_list:
        print 'Press enter to open ' + name + '...'
        raw_input()
        file_path = os.path.join(directory_path, name + '.txt')
        os.system('open "' + file_path + '"')

# order1: sort by sum of all outgoing edges
def order1(graph):
    ids = graph.get_ids()
    nodes = graph.get_nodes()
    edges = graph.get_edges()
    ids.sort(key=lambda id: -sum([edges[key] for key in edges.keys() if key[0] == id]))
    return ids

# order2: sort by sum of all incoming edges
def order2(graph):
    ids = graph.get_ids()
    nodes = graph.get_nodes()
    edges = graph.get_edges()
    ids.sort(key=lambda id: -sum([edges[key] for key in edges.keys() if key[1] == id]))
    return ids

# order3: sort by sum of all outgoing edges recursively
def order3(graph):
    ids = graph.get_ids()
    n = len(ids)
    nodes = graph.get_nodes()
    edges = graph.get_edges()
    order = []
    for i in range(n):
        scores = [(id, -sum([edges[key] for key in edges.keys() if (key[0] == id and key[1] in ids)])) for id in ids]
        scores.sort(key=lambda x: x[1])
        cur_id = scores[0][0]
        order.append(cur_id)
        ids = [id for id in ids if id != cur_id]
    return order

# order4: sort by sum of all incoming edges recursively
def order4(graph):
    ids = graph.get_ids()
    n = len(ids)
    nodes = graph.get_nodes()
    edges = graph.get_edges()
    order = []
    for i in range(n):
        scores = [(id, -sum([edges[key] for key in edges.keys() if (key[1] == id and key[1] in ids)])) for id in ids]
        scores.sort(key=lambda x: x[1])
        cur_id = scores[0][0]
        order.append(cur_id)
        ids = [id for id in ids if id != cur_id]
    return order

# path1: greedily choose next node as smallest distance
def path1(graph, start_id, end_id):
    ids = set(graph.get_ids())
    nodes = graph.get_nodes()
    edges = graph.get_edges()
    path_ids = [start_id]
    cur = start_id
    while cur != end_id:
        ids.remove(cur)
        min_distance = float('inf')
        min_id = None
        for id in ids:
            if (cur, id) in edges and edges[(cur, id)] != -1 and edges[(cur, id)] < min_distance:
                min_id = id
                min_distance = edges[(cur, id)]
        if not min_id: return []
        path_ids.append(min_id)
        cur = min_id
    return path_ids

# path2: shortest overall distance path with Dijkstra
def path2(graph, start_id, end_id):
    ids = set(graph.get_ids())
    nodes = graph.get_nodes()
    edges = graph.get_edges()
    distance = {}
    previous = {}
    max_distance = max(graph.get_edges().values())
    for id in ids:
        distance[id] = max_distance
        previous[id] = None

    distance[start_id] = 0

    while ids:
        cur = sorted([(key, distance[key]) for key in distance.keys() if key in ids], key=lambda x: x[1])[0][0]
        ids.remove(cur)

        for id in ids:
            if (cur, id) in edges and edges[(cur, id)] >= 0:
                alt = distance[cur] + edges[(cur, id)]
                if alt < distance[id]:
                    distance[id] = alt
                    previous[id] = cur

    path_ids = [end_id]
    cur = end_id
    while True:
        cur = previous[cur]
        path_ids.append(cur)
        if cur == start_id:
            break

    path_ids = list(reversed(path_ids))
    return path_ids

# path3: shortest overall distance path with Dijkstra using max distance cutoff
def path3(graph, start_id, end_id):
    PERCENTILE = 0.8

    ids = set(graph.get_ids())
    nodes = graph.get_nodes()
    edges = graph.get_edges()

    distances = sorted([value for value in edges.values() if value >= 0])
    distance_cutoff = distances[int(len(distances) * PERCENTILE)]

    distance = {}
    previous = {}
    max_distance = max(graph.get_edges().values())
    for id in ids:
        distance[id] = max_distance
        previous[id] = None

    distance[start_id] = 0

    while ids:
        cur = sorted([(key, distance[key]) for key in distance.keys() if key in ids], key=lambda x: x[1])[0][0]
        ids.remove(cur)

        for id in ids:
            if (cur, id) in edges and edges[(cur, id)] >= 0 and edges[(cur, id)] <= distance_cutoff:
                alt = distance[cur] + edges[(cur, id)]
                if alt < distance[id]:
                    distance[id] = alt
                    previous[id] = cur

    path_ids = [end_id]
    cur = end_id
    while True:
        if cur not in previous: return []
        cur = previous[cur]
        if cur == None:
            return []
        path_ids.append(cur)
        if cur == start_id:
            break

    path_ids = list(reversed(path_ids))
    path_names = [nodes[id] for id in path_ids]
    return path_ids

if __name__ == '__main__':
    ### Set up graph
    directory_path = "/Users/{0}/Dropbox (MIT)/children's books/books/".format(os.environ['USER'])
    graph = make_graph(directory_path = directory_path, metric_name = 'Tversky index')
    graph.prune_edges()

    ids = set(graph.get_ids())
    nodes = graph.get_nodes()
    edges = graph.get_edges()

    ## Get list of names and ids
    ids = order1(graph)
    names1 = list(reversed([nodes[id] for id in ids]))
    print names1

    ids = order2(graph)
    names2 = list(reversed([nodes[id] for id in ids]))
    print names2

    ids = order3(graph)
    names3 = list(reversed([nodes[id] for id in ids]))
    print names3

    ids = order4(graph)
    names4 = list(reversed([nodes[id] for id in ids]))
    print names4

    print sum([1 if names2[i] == names4[i] else 0 for i in range(len(names1))])
    print sum([1 if names1[i] == names3[i] else 0 for i in range(len(names1))])
