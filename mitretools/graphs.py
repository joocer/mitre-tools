import networkx as nx
import matplotlib.pyplot as plt
import random



def intersect_lists(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 

def intersect_list_of_lists(list_of_lists):
    lister = list_of_lists[0]
    for i in range(len(list_of_lists)):
        lister = intersect_lists(lister, list_of_lists[i])
    return lister


def filter_graph(graph, target_node_filter, edge_filter, node_filter = []):
    '''
    Filters a graph for nodes connected to a given set of nodes.

    graph: the graph (must be a directed)

    target_node_filter: a dictionary of filters, where multiple filters are given, they are ANDed.
        format for the filters are:
        { 
            attribute: [values], 
            attribute: [values] 
        }
        
    edge_filter:
    '''
    working_graph = graph.copy()
    
    # filter the graph to only the edges wanted
    for edge_id in graph.edges:
        for key in edge_filter:
            value = working_graph.edges()[edge_id].get(key)
            if not value in edge_filter[key]:
                working_graph.remove_edge(edge_id[0], edge_id[1])
                
    remove_nodes = []
    # filter the graph to only the nodes wanted
    for i in range(len(node_filter)):
        for key in node_filter[i]:
            for node_id in working_graph.nodes:
                node = working_graph.nodes()[node_id]
                if node.get('kind') == key:
                    for sub_key in node_filter[i][key]:
                        sub_value = node.get(sub_key)
                        if sub_value != None:
                            if node_filter[i][key][sub_key] != sub_value:
                                remove_nodes.append(node_id)
    for node_id in remove_nodes:
        working_graph.remove_node(node_id)
            
    # filter nodes to find starting points
    target_nodes = []
    for key in target_node_filter:
        _target_nodes = [x for x,y in working_graph.nodes(data=True) if y.get(key) in target_node_filter[key]]
        target_nodes.append(_target_nodes)
    target_nodes = intersect_list_of_lists(target_nodes)

    # build a list of nodes attached to the search nodes
    nodes = []
    for target_node in target_nodes:
        tree = nx.dfs_tree(working_graph, source=target_node, depth_limit=10)
        for node_id in tree.nodes():
            node = working_graph.nodes()[node_id]
            if node.get('occurances') == None:
                node['occurances'] = len(tree.in_edges(node_id))
            else:
                node['occurances'] = node['occurances'] + len(tree.in_edges(node_id))
            nodes.append(node_id)
            
    return working_graph.subgraph(nodes).copy()






