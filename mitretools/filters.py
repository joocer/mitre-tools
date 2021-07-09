"""
Methods to apply filters to graphs.
"""

import networkx as nx


def select_edges_by_relationship(graph, edge_filter = [], remove = False):
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


def select_nodes_by_type(graph, node_filter = [], remove = False):
    """
    Filters the edges of a graph based on node_type.

    Parameters
        graph: Graph to filter
        node_filter: List of 'node_types' to filter on
        remove: whether to remove the selected Nodes (optional, default: False)

    Returns a filtered graph.
    """
    if remove:
        result_nodes = filter(lambda x: x[1].get('node_type', '') in node_filter, graph.nodes(data=True))
    else:
        result_nodes = filter(lambda x: x[1].get('node_type', '') not in node_filter, graph.nodes(data=True))
    result_nodeids = map(lambda x: x[0], result_nodes)    
    working_graph = graph.copy()
    working_graph.remove_nodes_from(result_nodeids)
    return working_graph
    

def intersect_lists(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 


def intersect_list_of_lists(list_of_lists):
    lister = list_of_lists[0]
    for i in range(len(list_of_lists)):
        lister = intersect_lists(lister, list_of_lists[i])
    return lister


def search_nodes(graph, conditions = {}):
    """
    Filters the edges of a graph based on node_type.

    Parameters
        graph: Graph to filter
        predicate: function to used to search

    Returns a graph.
    """
    target_nodes = []
    for key in conditions:
        _target_nodes = [x for x,y in graph.nodes(data=True) if y.get(key) == conditions[key]]
        target_nodes.append(_target_nodes)
    target_nodes = intersect_list_of_lists(target_nodes)
    return graph.subgraph(target_nodes).copy()


def remove_orphans(graph):
    """
    Identifies nodes with no edges and removes them.

    Returns a graph.
    """
    working_graph = graph.copy()
    orphan_nodes = []
    for node_id in working_graph.nodes():
        node = working_graph.nodes()[node_id]
        if node.get('node_type') in [None]:
            orphan_nodes.append(node_id)
    for node_id in orphan_nodes:
        working_graph.remove_node(node_id)
    return working_graph


def walk_from(graph, starting_nodes, depth = 25):
    """
    Walks a graph from a set of starting nodes, joins the resultant graphs together.

    Parameters
        graph: Graph to filter
        predicate: function to used to search

    Returns a graph.
    """
    try:
        iterator = iter(starting_nodes)
    except TypeError:
        starting_nodes = [starting_nodes]

    nodes = []
    for node in starting_nodes:
        tree = nx.dfs_tree(graph, source = node[0], depth_limit = depth)
        nodes = nodes + list(tree.nodes())
    return graph.subgraph(nodes).copy()
