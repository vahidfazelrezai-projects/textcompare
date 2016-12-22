import os
from textcompare import TextDoc, metric
import compare
from flask import Flask, jsonify, request
app = Flask(__name__)

tversky_alpha = 0.0
tversky_beta = 0.1

# filepath = "./data/books"
filepath = "/Users/{0}/Dropbox (MIT)/children's books/books/".format(os.environ['USER'])
all_textdocs, metric = compare.initialize(filepath)
freqs = [t.get_frequencies() for t in all_textdocs]
names = [t.get_title() for t in all_textdocs]

def tversky_divide_fn(d, words1, words2, weight_fn):
  if d == 0:
    return 1.0
  s1 = set(words1.keys())
  s2 = set(words2.keys())
  return 1 - d/(d + tversky_alpha*len(s1 - s2) + tversky_beta*(len(s2 - s1)))

def unit_fn(freq1, freq2):
    return 1

def default_weight_fn(word):
  return 1

def combine_freqs(freqs_list):
    keys = []
    for f in freqs_list:
        keys.extend(f.keys())
    keys = set(keys)

    new = {}
    for k in keys:
        new[k] = 0

    for f in freqs_list:
        for k in f.keys():
            new[k] += f[k]

    return new

def get_distance(words1, words2):
    d = 0
    common_words = set(words1.keys()) & set(words2.keys())
    for word in common_words:
        num = float(unit_fn(words1[word], words2[word]))
        den = float(unit_fn(words1[word], words2[word]))
        d += ((default_weight_fn(word)**2) * (num / den))
    d = float(tversky_divide_fn(d, words1, words2, default_weight_fn))
    return d

def get_min_dist_id(combined_freqs, ids):
    distances = []
    for id in ids:
        freq = freqs[id]
        distances.append((get_distance(combined_freqs, freq), id))
    distances.sort(key=lambda x: x[0])
    return distances[0][1]

@app.route('/')
def index():
    return app.send_static_file('index.html');

@app.route('/names')
def get_names():
    return jsonify(names)

@app.route('/suggest')
def get_suggest():
    id_list = [int(id) for id in request.args.get('read').split(',')];
    combined_freqs = combine_freqs([freqs[i] for i in id_list])
    remaining_ids = [index for index in range(len(freqs)) if index not in id_list]
    next = get_min_dist_id(combined_freqs, remaining_ids)
    return names[next]
