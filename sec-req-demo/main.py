#!flask/bin/python
from flask import Flask, request, jsonify, make_response, render_template
import datetime
import json
import networkx as nx
import matplotlib
matplotlib.use('agg')
import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], ".."))
import mitretools as mt

# /consequences/group/impact

###############################################################################

app = Flask(__name__)
graph = nx.read_graphml(r'data/processed/mitre-data.graphml')

###############################################################################

@app.route('/', methods=["OPTIONS", "GET"])
def api_base():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "GET":
        return render_template('index.html')
    
###############################################################################
    
@app.route('/consequences/<group>/<impact>/<level>', methods=["GET", "OPTIONS"])
def api_consequences_group_impact(group, impact, level):
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "GET": 
        g = get_graph(graph, group, impact, level)
        return _corsify_actual_response(jsonify(g))

@app.route('/consequences', methods=["GET", "OPTIONS"])
def api_consequences():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "GET": 
        consequences = []
        result_nodes = filter(lambda x: x[1].get('node_type') == "Consequence", graph.nodes(data=True))
        for node in result_nodes:
            if node[1].get('group') in ['Confidentiality', 'Availability', 'Integrity']:
                consequences.append({ 'principle': node[1].get('group'), 'consequence': node[1].get('consequence') })
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

def starts_with(full, sub):
    return full[:len(sub)] == sub

def get_graph(graph, group, impact, level):

    g = mt.select_edges_by_relationship(graph, ['Inverse-ResultsIn',
                                    'Inverse-Enables', 
                                    'Inverse-Prevents',
                                    'Inverse-Mitigates',
                                    'ChildOf',
                                    'ParentOf',
                                     ''])
    orient = mt.select_nodes_by_type(g, ['Consequence'])
    print(group, impact, list(orient.nodes(data=True)).pop())
    orient = [nid for nid, attr in orient.nodes(data=True) if attr.get('group') == group and attr.get('consequence') == impact]
    print(orient)
    #print([(nid,attr) for nid, attr in orient.nodes(data=True) if attr.get('group') == group and attr.get('consequence') == impact])
    
    results = []
    for n in orient:
        w = nx.dfs_tree(g, n, 8)
        results += [nid for nid,attr in w.nodes(data=True) if starts_with(nid, 'ASVS')]
    return results

###############################################################################

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=2300)      