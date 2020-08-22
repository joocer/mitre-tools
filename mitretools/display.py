import networkx as nx
import matplotlib.pyplot as plt
import random


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


def hierarchy_pos(G, root=None, width=1.5, vert_gap = 1., vert_loc = 0, xcenter = 0.5):

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
    
    LARGE_FONT = 12
    plt.rc('font', size=LARGE_FONT)
    
    node_labels=nx.get_node_attributes(graph, 'label')
    plt.figure(figsize = (25,16))
    nx.draw(graph, pos=pos, edge_color="#CCCCCC", linewidths=0.3, node_size=1, with_labels=True, labels=node_labels)
    edge_labels = nx.get_edge_attributes(graph, 'relationship')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red')