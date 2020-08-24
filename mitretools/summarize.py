import networkx as nx


def condense_graph(graph):
    """
    Condenses a graph by node_type.

    Parameters
        graph: Graph to summarize
        
    Returns a graph.
    """
    working_graph = nx.DiGraph()
    for n1, n2, e in graph.edges(data = True):
        node1 = graph.nodes()[n1].get("node_type")
        node2 = graph.nodes()[n2].get("node_type")
        working_graph.add_edge(node1, node2, relationship = e.get('relationship'))
        working_graph.add_node(node1, node_type = 'Condensation', id = node1)
        working_graph.add_node(node2, node_type = 'Condensation', id = node2)
    return working_graph


def list_nodes(graph, attributes=['node_type'], separator=', '):
    """
    Summarize a graph's nodes into a list.

    Parameters
        graph: Graph to summarize
        attributes: a list of the attributes to group on (optional, default: ['node_type'])
        separator: the separator when multiple attributes are listed (optional, default: ',')
        
    Returns a dictionary with 'attributes' as the key and the number of instances as the value.
    """
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
    return dict(nodes)