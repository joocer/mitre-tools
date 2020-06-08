#!flask/bin/python
from flask import Flask, request, jsonify, make_response, render_template
import datetime
import json
import networkx as nx
import matplotlib
matplotlib.use('agg')
import sys
sys.path.insert(0,'..')
import mitretools as mt

# /consequences/group/impact

###############################################################################

app = Flask(__name__)
graph = nx.read_graphml(r'../data/processed/mitre-data.graphml')

###############################################################################

@app.route('/', methods=["OPTIONS", "GET"])
def api_base():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "GET":
        return render_template('index.html')
    
###############################################################################
    
@app.route('/consequences/<group>/<impact>', methods=["GET", "OPTIONS"])
def api_consequences_group_impact(group, impact):
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "GET": 
        g = get_graph(graph, group, impact)
        reqs = get_list(mt.list_nodes(g, ['asvs'], ['label']))
        return _corsify_actual_response(jsonify(reqs))

@app.route('/consequences', methods=["GET", "OPTIONS"])
def api_consequences():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "GET": 
        consequences = []
        c_graph = mt.filter_graph(graph, { 'kind': ['consequence'] }, {}, {})
        for node_id in c_graph:
            node = c_graph.nodes()[node_id]
            if node.get('group') in ['Confidentiality', 'Availability', 'Integrity']:
                consequences.append({ 'principle': node.get('group'), 'consequence': node.get('label') })
        consequences = [dict(t) for t in {tuple(d.items()) for d in consequences}]
        return _corsify_actual_response(jsonify(consequences))

###############################################################################

def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

###############################################################################

def get_list(items):
    r = []
    for key in items:
        r.append(key)
    r.sort()
    return r

def get_graph(graph, group, impact):
    return mt.filter_graph(graph, 
                 { 
                     'label': [impact], 
                     'group': [group] 
                 }, 
                 { 'relationship': ['Inverse-ResultsIn',
                                    #'ResultsIn', 
                                    'Inverse-Enables', 
                                    #'Enables', 
                                    #'Inverse-Requires',
                                    #'Requires',
                                    'Inverse-Prevents',
                                    #'Prevents',
                                    'Inverse-Mitigates',
                                    #'Mitigates',
                                    'ChildOf',
                                    'ParentOf',
                                     ''
                                   ] },
                { 'capec' : { 'likelihood_of_attack': 'High' } })

###############################################################################

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=2300)