"""
Methods to apply filters to graphs.


"""

def select_edges(graph, edge_filter = [], remove = False):
    """
    Filters the edges of a graph.

    Parameters
        graph: Graph to filter
        edge_filter: List of edge relationships to filter on
        remove: whether to remove the selected Edges (optional, default: False) 
    Returns a filtered graph.
    """
    working_graph = graph.copy()
    for edge_id in graph.edges:
        value = working_graph.edges()[edge_id].get('relationship')
        if remove:
            if value in edge_filter:
                working_graph.remove_edge(edge_id[0], edge_id[1])
        else:
            if not value in edge_filter:
                working_graph.remove_edge(edge_id[0], edge_id[1])
    return working_graph


def select_nodes(graph, node_filter = [], remove = False):
    """
    Filters the edges of a graph.

    Parameters
        graph: Graph to filter
        node_filter: List of node data types to filter on
        remove: whether to remove the selected Nodes (optional, default: False)
    Returns a filtered graph.
    """
    remove_nodes = []
    working_graph = graph.copy()
    for node_id in working_graph.nodes:
        node = working_graph.nodes()[node_id]
        if remove:
            if node.get('label') in node_filter:
                remove_nodes.append(node_id)
        else:
            if not node.get('label') in node_filter:
                remove_nodes.append(node_id)            
    for node_id in remove_nodes:
        working_graph.remove_node(node_id)
    return working_graph


def remove_orphans(graph):
    """
    Identifies nodes with no edges and removes them.

    Returns a graph.
    """
    working_graph = graph.copy()
    orphan_nodes = []
    for node_id in working_graph.nodes():
        node = working_graph.nodes()[node_id]
        if node.get('data') in [None]:
            orphan_nodes.append(node_id)
    for node_id in orphan_nodes:
        working_graph.remove_node(node_id)
    return working_graph


def walk_from(graph, starting_node, depth = 25):
    working_graph = nx.dfs_tree(graph, source=starting_node, depth_limit=depth)
    return working_graph