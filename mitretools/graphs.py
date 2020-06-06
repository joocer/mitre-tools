import networkx as nx
import matplotlib.pyplot as plt
import random


def remove_orphans(graph):
    orphan_nodes = []
    g = graph.copy()
    for node_id in g.nodes():
        node = g.nodes()[node_id]
        if node.get('kind') in [None]:
            orphan_nodes.append(node_id)

    for node_id in orphan_nodes:
        g.remove_node(node_id)
    return g

def intersect_lists(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 

def intersect_list_of_lists(list_of_lists):
    lister = list_of_lists[0]
    for i in range(len(list_of_lists)):
        lister = intersect_lists(lister, list_of_lists[i])
    return lister

def show_graph(graph):
    LARGE_FONT = 14
    plt.rc('font', size=LARGE_FONT)
    node_labels=nx.get_node_attributes(graph, 'label')
    pos = nx.spring_layout(graph, iterations=20)
    plt.figure(figsize = (15,12))
    nx.draw(graph, pos=pos, edge_color="#CCCCCC", linewidths=0.3, node_size=1, with_labels=True, labels=node_labels, connectionstyle='arc3, rad=0.2')
    edge_labels = nx.get_edge_attributes(graph, 'relationship')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red', connectionstyle='arc3, rad=0.2')
    plt.axis('off')
    plt.show()

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

def filter_graph(graph, target_node_filter, edge_filter, node_filter = {}):
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
    for key in node_filter:
        for node_id in working_graph.nodes:
            node = working_graph.nodes()[node_id]
            if node.get('kind') == key:
                for sub_key in node_filter[key]:
                    sub_value = node.get(sub_key)
                    if sub_value != None:
                        if node_filter[key][sub_key] == sub_value:
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

def simplify_graph(graph):
    g = nx.DiGraph()
    for n1, n2, e in graph.edges(data = True):
        node1 = graph.nodes()[n1]
        node2 = graph.nodes()[n2]
        g.add_edge(node1.get('kind'), node2.get('kind'), relationship=e.get('relationship'))
        g.add_node(node1.get('kind'), label=node1.get('kind'))
        g.add_node(node2.get('kind'), label=node2.get('kind'))
    return g

import networkx as nx
import random


def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

    '''
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
    Licensed under Creative Commons Attribution-Share Alike 

    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch 
    - if the tree is directed and this is not given, 
      the root will be found and used
    - if the tree is directed and this is given, then 
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given, 
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    '''

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''

        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            dx = width/len(children) 
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos


    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

def show_tree(graph):
    pos = hierarchy_pos(graph)
    for node in pos:
        pos[node] = (1 - pos[node][1]),pos[node][0]
    
    LARGE_FONT = 14
    plt.rc('font', size=LARGE_FONT)
    
    node_labels=nx.get_node_attributes(graph, 'label')
    plt.figure(figsize = (15,12))
    nx.draw(graph, pos=pos, edge_color="#CCCCCC", linewidths=0.3, node_size=1, with_labels=True, labels=node_labels)
    edge_labels = nx.get_edge_attributes(graph, 'relationship')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red')