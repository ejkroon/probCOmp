import networkx as nx
import csv
from random import choices
from scipy.stats import wasserstein_distance
from scipy.stats import percentileofscore

def check_target_node(G:nx.DiGraph, path:list[str], target:str):
    """Function to check whether target node could be appended to a 
        path.

    The function checks 1) whether the technique be performed in the 
    present path state; 2) whether performing the technique would cause 
    a loop; and 3) whether there is a chance of selecting the technique. 

    Paramaters
    ----------
    G : nx.DiGraph
        Directed graph representing the total chaîne opératoire.
    path : list
        List of nodes in which the 0th item is the path state and the 
        remaining nodes are previously visited techniques
    target : string
        Node ID of a potential new node to add to the path

    Returns
    -------
    check : boolean
        Returns True if node could appear next, and False if not.
    """

    check = True

    if not path[0] in G.nodes[target]['tolerance']:
        check = False

    if target in path:
        check = False

    if G.edges[path[-1], target]['weight'] == 0.0:
        check = False

    return check

def generate_random_paths(
                            G:nx.DiGraph, 
                            number:int, 
                            termination_chance:float,
                            initial_state:str = 'W',
                            starting_node:str = 'Wet clay'
                        ):
    """Function to generate paths through the total chaîne opératoire 
    for ceramics.

    This function can perform both random path generation and guided 
    random path generation (cf. Kroon 2024) by modifying the edge 
    weights in G.


    Parameters
    ----------
    G : networkx DiGraph object
        Directed graph representing the total 
    number : int
        Number of paths to generate (positive integer).
    termination_chance : float
        Chance a path terminates after the firing process or each step 
        following the firing process. Interval [0,1].
    initial_state : str
        Initial state of the path in the network. Default = 'W'.
    starting_node : str
        Initial node on the path. Default = 'Wet clay'.

    Returns
    -------
    generated_paths : list of lists
        List containing all generated paths as lists of nodes.
    """
    
    #List of results
    generated_paths = []
    
    #Loop to generate paths
    while len(generated_paths) < number:
        path = [initial_state, starting_node]

        #Loop to select potential new nodes
        active = True
        while active:
            potential_targets = list(G.neighbors(path[-1]))
            targets = []
            for pt in potential_targets:
                if check_target_node(G, path, pt) == True:
                    targets.append(pt)
            
            #Select new node or terminate
            if targets:
                target_weights = [
                    G.edges[path[-1], target]['weight'] for target in targets
                    ]
                new_node = choices(targets, weights=target_weights ,k=1)[0]
            else:
                if path[0] == 'F':
                    generated_paths.append(path[1:])
                    active = False
                else:
                    active = False

            #Post-firing check
            if path[0] == 'F':
                if choices(
                            [0,1], 
                            weights = [
                                termination_chance, 
                                1-termination_chance
                                ], 
                            k=1
                        )[0] == 0:
                    generated_paths.append(path[1:])
                    active = False
                else:
                    path.append(new_node)
            else:
                path.append(new_node)
            
            #Update path state if necessary
            if new_node == 'Drying to leather-hard':
                path[0] = 'L'
            elif new_node == 'Drying to dry':
                path[0] = 'D'
            elif new_node in [
                                'Open firing',
                                'Enclosed firing',
                                'Direct flame kilns',
                                'Indirect flame kilns',
                                'Radiant heat kilns',
                            ]:
                path[0] = 'F'

    return generated_paths

def load_network(
        nodes:list[list[str]], 
        links:list[list[str, float|int]]
        ):
    """ Function to create networkx DiGraph object for total châîne opératoire.

    Paramaters
    ----------
    nodes : list of lists
        List of nodes and their tolerance, formatted as [node_ID, tolerances]
    links : list of lists
        List of links formatted as [source, target, weight]

    Returns
    -------
    G : networkx DiGraph object
    """

    #Create dictionairy for node attributes
    node_tolerance_dict={}
    for node in nodes:
        node_tolerance_dict[node[0]] = [
            value for value in node[1:] if value != ''
            ]

    #Create graph object from data
    G = nx.DiGraph()
    G.add_nodes_from([node[1] for node in nodes])
    G.add_weighted_edges_from(links)
    nx.set_node_attributes(G, node_tolerance_dict, 'tolerance')
    weight = nx.get_edge_attributes(G, 'weight')

    return G

def check_paths(G:nx.DiGraph, paths:list[list[str]]):
    """Function to check whether the paths in a dataset are formatted 
    correctly.

    Paramaters
    ----------
    G : networkx DiGraph object
        Network representing the total chaîne opératoire.
    paths : list of lists
        List of paths through the total chaîne opératoire.

    Returns
    -------
    check_state : boolean
        Returns False if errors were detected and True if not.
    """
    
    #Results list
    error_list = []

    #Loop through paths and perform checks
    for idx, path in enumerate(paths):
        
        #check if paths start with correct node
        if path[0] != 'Wet clay':
            error_list.append(f'path{idx} path does not start on "Wet clay".')

        #Check for loops
        if len(set(path)) != len(path):
            for node in path:
                if path.count(node) > 1:
                    error_list.append(f'path {idx} loops at {node}')
                else:
                    continue
        
        #Check if all pairs exist and conform syntax
        for first, second in zip(path, path[1:]):
            if G.has_edge(first, second) == False:
                error_list.append(f'path {idx}, pair {first, second} absent in graph.')
        
        #Check if path respects syntax
        virtual_state = 'W'
        for node in path:
            if node not in list(G.nodes):
                error_list.append(f'path {idx} {node} absent in graph')

            if virtual_state not in G.nodes[node]['tolerance']:
                error_list.append(f'path {idx} {node} appears out of syntax')

            if node == 'Drying to leather-hard':
                virtual_state = 'L'
            if node == 'Drying to dry':
                virtual_state = 'D'
            if node in [
                        'Open firing',
                        'Enclosed firing',
                        'Direct flame kilns',
                        'Indirect flame kilns',
                        'Radiant heat kilns',
                    ]:
                virtual_state = 'F'

    #Flag problems if any
    if error_list: 
        check_state = False
        for error in error_list:
            print(error)
    else:
        check_state = True

    return check_state

def load_paths_to_graph(G:nx.DiGraph, paths:list[list[str]]):
    """Function to obtain a weighted link list from a set of paths.

    Parameters
    ----------
    G : networkx DiGraph object
        Network object representing the total chaîne opératoire.
    paths : list of lists
        List of specific chaînes opératoires for ceramics.

    Returns
    -------
    link_list : list of lists
        Weighted link list, formatted as [source, target, weight] where edge 
        weights derive from the set of paths.
    """

    #List to store results
    link_list = [list(edge) for edge in G.edges()]
    for link in link_list:
        link.append(0)
    
    #Loop through paths and count links
    for path in paths:
        for first, second in zip(path, path[1:]):
            for link in link_list:
                if [link[0], link[1]] == [first, second]:
                    link[2] += 1
                else:
                    continue

    #Convert counts to relative frequencies
    for link in link_list:
        link[2] = (link[2]/len(paths))*100

    return link_list

def compare_assemblages(
        a:list[list[str,float]], 
        b:list[list[str,float]]
        ):
    """"Function to calculate the Wasserstein distance between two subgraphs.
    
    The subgraphs are represented as weighted link lists of the networkx 
    DiGraph representing the total ceramic chaîne opératoire.

    Parameters
    ----------
    a : list of lists
        Source of the comparison. Weighted link list with the relative 
        frequencies of links in a set of paths, formatted as [source, target, 
        weight].
    b: list of lists
        Target of the comparison. Weighted link list with the relative 
        frequencies of links in a set of paths, formatted as [source, target, 
        weight].

    Returns
    -------
    outcome : float
        Wasserstein distance between two subgraphs. Returns None if the two 
        link lists are not identical.
    """
    
    #Extract link list and check if identical
    a_links = [[link[0], link[1]] for link in a]
    b_links = [[link[0], link[1]] for link in b]
    if a_links == b_links:
        
        #Calcultate Wasserstein distance
        outcome = wasserstein_distance(
                                        [link[2] for link in a], 
                                        [link[2] for link in b],
                                    )
    else:
        outcome = None 

    return outcome

def generate_control_from_link_list(
                                    G:nx.DiGraph, 
                                    links:list[list[str, float|int]], 
                                    nodes:list[list[str]], 
                                    n_paths:int, 
                                    termination_chance:float,
                                ):
    """Helper function to randomly generate paths from a link list.

    Chains together extract_link_list(), load_network(), 
    generate_random_paths(), and load_paths_to_graph(). This enables fast 
    generation of a link list for calculating Wasserstein distances.

    Paramaters
    ----------
    G : networkx DiGraph object
        Network representing the total chaîne opératoire for ceramics
    links : list of lists
        List of weighted links for path generation, formatted as [source, 
        target, weight].
    nodes : list of lists
        List of nodes and their tolerance, formatted as [node_ID, tolerances].
    n_paths : int
        Number of paths to generate (positive integer).
    termination_chance : float
        Chance a path terminates after the firing process or each step 
        following the firing process. Interval [0,1].

    Returns
    -------
    link_list : list of lists
        List of links formatted as [source, target, weight]. Corresponding to 
        the edge weight distribution of a subgraph of G with the generated 
        paths.
    """
    
    #Generate paths from link list
    H = load_network(nodes, links)
    paths = generate_random_paths(H, n_paths, termination_chance)
    if check_paths(G, paths) == True:
        link_list = load_paths_to_graph(G, paths)

    return link_list

def permutation_test(
                        G:nx.DiGraph, 
                        a_paths:list[list[str]], 
                        b_paths:list[list[str]], 
                        C:nx.DiGraph, 
                        control_size:int, 
                        n_control:int, 
                        termination_chance:float,
                    ):
    """ Helper function to perform a permutation test with a control group.
    
    Chains together load_paths_to_graph() and compare_assemblages() for the 
    empirical datasets a and b. This returns the Wasserstein distance between 
    the empirical assemblages (Wd a,b).

    Then chains together generate_random_paths(), compare_assemblages(), and 
    load_paths_to_graph() to generate an ensemble of control groups, both with 
    a specified size. Each control group is compared against a, and the 
    percentile of Wd a,b relative to these controls is calculated.

    Parameters
    ----------
    G : networkx DiGraph object
        Network representing the total chaîne opératoire for ceramics
    a_paths : str
        Path to file with a dataset of empirical paths.
    b_paths : str
        Path to file with a dataset of empirical paths.
    C : networkx DiGraph object
        Weighted subgraph of G representing the variation in techniques in a 
        control group with (no) shared knowledge with assemblage A.
    control_size : int
        Number of control groups to generate from C. Positive integer.
    n_control
        Size of each control group to generate from C. Positive integer.
    termination_chance : float
        Chance a path terminates in C after the firing process or each step 
        following the firing process. Interval [0,1].

    Returns
    -------
    score : float
        The Wasserstein distance between the empirical sets of paths (Wd a,b).
    percentile : float
        The percentile of Wd a,b relative to the ensemble of control groups.
    control_scores : list
        List of the Wd a,c for all control groups
    """

    #Obtain weighted link lists and calculate Wasserstein distance
    a = load_paths_to_graph(G, a_paths)
    b = load_paths_to_graph(G, b_paths)
    score = compare_assemblages(a, b)

    #Generate control groups
    control_scores = []
    for n in range(0, n_control):
        control_group = generate_random_paths(
            C, control_size, 
            termination_chance
            )
        control_scores.append(
            compare_assemblages(a, load_paths_to_graph(G, control_group))
            )

    #Calculate percentile of Wd a,b relative to Wd a,c
    percentile = percentileofscore(control_scores, score, 'weak')
    return score, percentile, control_scores
