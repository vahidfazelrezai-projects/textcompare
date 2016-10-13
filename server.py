import os
from textdoc import TextDoc
import compare
from flask import Flask, jsonify, request
app = Flask(__name__)

filepath = "./data/books"
all_textdocs, metric = compare.initialize(filepath)

@app.route('/')
def index():
    return app.send_static_file('index.html');

@app.route('/metrics')
def metrics():
    return jsonify(metric.metrics.keys())

@app.route('/data')
def data():
    if 'count' in request.args:
        count = int(request.args['count'])
    else:
        count = 7
    textdocs = all_textdocs[:count]

    nodes = []
    id_map = {}
    id_counter = 1
    for doc in textdocs:
        num_words = len(doc.get_frequencies().keys())
        nodes.append({
            'id': id_counter,
            'value': num_words,
            'label': doc.get_title() + ' (' + str(num_words) + ')'
        })
        id_map[doc] = id_counter
        id_counter += 1

    edges = []
    if 'metric' in request.args and request.args['metric'] != 'None':
        m = metric.metrics[request.args['metric']]
        for i in xrange(len(textdocs)):
            for j in xrange(i+1, len(textdocs)):
                doc1 = textdocs[i]
                doc2 = textdocs[j]
                d = m.distance(doc1, doc2)
                if d == -1:
                    continue # Ignore books with no words in common.
                edges.append({
                    'from': id_map[doc1],
                    'to': id_map[doc2],
                    'value': d,
                    'title': 'd: ' + str(d)
                })

    return jsonify({
        'nodes': nodes,
        'edges': edges
    })
