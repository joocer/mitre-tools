import networkx as nx


def condense_graph(graph):
    g = nx.DiGraph()
    for n1, n2, e in graph.edges(data = True):
        node1 = graph.nodes()[n1].get("node_type")
        node2 = graph.nodes()[n2].get("node_type")
        g.add_edge(node1, node2, relationship=e.get('relationship'))
        g.add_node(node1, node_type='Condensation', id=node1)
        g.add_node(node2, node_type='Condensation', id=node2)
    return g


def list_nodes(graph, attributes=['node_type'], separator=','):
    from collections import Counter
    nodes = Counter()
    for node_id in graph.nodes():
        node = graph.nodes()[node_id]        
        results = []
        for attribute in attributes:
            value = node.get(attribute)
            if value != None:
                results.append(value)
        result = separator.join(results)
        nodes.update([result])
    return nodes