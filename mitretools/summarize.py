import networkx as nx


def condense_graph(graph):
    g = nx.DiGraph()
    for n1, n2, e in graph.edges(data = True):
        node1 = graph.nodes()[n1]
        node2 = graph.nodes()[n2]
        g.add_edge(node1.get('kind'), node2.get('kind'), relationship=e.get('relationship'))
        g.add_node(node1.get('kind'), label=node1.get('kind'))
        g.add_node(node2.get('kind'), label=node2.get('kind'))
    return g


def list_nodes(graph, type_filter = [], attributes=['label'], separator=', ', occurances=False):
    nodes = {}
    for node_id in graph.nodes():
        match = False
        node = graph.nodes()[node_id]
        if len(type_filter) == 0:
            match = True
        else:
            match = node.get('kind') in type_filter
        if match:
            result = ''
            if len(attributes) == 1:
                result = node.get(attributes[0])
            else:
                results = []
                for attribute in attributes:
                    value = node.get(attribute)
                    if value != None:
                        results.append(value)
                result = separator.join(results)
            nodes[result] = node.get('occurances')
    return nodes