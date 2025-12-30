import csv
import sys
sys.path.append('../probCOmp/')
from functions import *

""" 
------------------------------------------------------------------------
SIMPLE WORKFLOW
------------------------------------------------------------------------

Overview of a workflow for a simple comparison which calculates the 
Wasserstein distance between two sets of paths and compares this distance 
against a control group. The examples use the datasets from Kroon (2024).

Steps:
1) Build a network representation of the total chaîne opératoire
2) Load two empirical datasets (a, b) with paths
3) Generate random paths as a control group (c)
4) Calculate and compare Wd(a,b) to Wd(a,c)
"""
#Step 1: Creating a basic graph
#Step 1.1: Extract the nodes for the total chaîne opératoire
with open('files/nodes_list.csv', 'r', encoding='utf-8') as fn:
    reader = csv.reader(fn, delimiter = ';')
    nodes = [n for n in reader][1:]

#Step 1.2: Exract the links for the total chaîne opératoire
with open('files/link_list_uniform.csv', 'r', encoding='utf-8') as fl:
    reader = csv.reader(fl, delimiter = ';')
    uniform_links = [n for n in reader][1:]

for link in uniform_links:
    link.append(int(link[2]))
    del link[2]

#Step 1.3: Build a network representation
G = load_network(nodes, uniform_links)

#Step 2: Loading empirical data
#Step 2.1: Extract paths from dataset
with open('files/FBW_4mil.csv', 'r', encoding='utf-8') as df1:
    reader = csv.reader(df1, delimiter=';')
    FBW4_paths = [l for l in reader]

#Step 2.2: Check paths for compatibility (recommended)
check_paths(G, FBW4_paths)

#Step 2.3: Repeat for the second dataset
with open('files/FBW_3mil.csv', 'r', encoding='utf-8') as df2:
    reader = csv.reader(df2, delimiter=';')
    FBW3_paths = [l for l in reader]
check_paths(G, FBW3_paths)

#Step 3: Generate a control group of 1,000 random paths with a termination
#chance of 0.5 for each new step after firing
random_paths = generate_random_paths(G, 1000, 0.5)

#Step 4: Calculate and compare Wasserstein distances
#Step 4.1: Convert the paths into weighted subgraphs of the ttotal chaîne 
#opératoire
FBW4 = load_paths_to_graph(G, FBW4_paths)
FBW3 = load_paths_to_graph(G, FBW3_paths)
random_control = load_paths_to_graph(G, random_paths)

#Step 4.2: Compare the two empirical datasets
outcome = compare_assemblages(FBW4, FBW3)
control = compare_assemblages(FBW4, random_control)

print(f'Outcomes: FBW4-FBW3 = {outcome}, FBW4-control = {control}.')
#Returns "Outcomes: FBW4-FBW3 = 0.39, FBW4-control = 3.529."

"""
------------------------------------------------------------------------
MORE COMPLEX WORKFLOW
------------------------------------------------------------------------

In this example, we are going to automate a number of the steps in the 
simple workflow, generate a control group based on (incomplete) 
empirical data and apply a permutation test with this control group.

Steps:
1) Program functions for extracting link lists
2) Extract empirical datasets
3) Generate a control group
4) Apply a permutation test
"""

#Step 1: Some functions to automate extracting link lists and paths
def extract_link_list(path_to_file, weight_type):
    """ Helper function to extract a link list from a csv file.

    Parameters
    ----------
    path_to_file : str
        String specifying the location of the paths to extract.
    weight_type : str
        Parameter specifying the type of weight. 'int' for integers, and 'float' 
        for decimal numbers.

    Returns
    -------
    link_list : list of lists
        List of links formatted as [source, target, weight].
    """

    #Open and read file with links
    with open(path_to_file, 'r', encoding='utf-8') as fl:
        reader = csv.reader(fl, delimiter=';')
        link_list = [l for l in reader][1:]

    #Convert weights
    for link in link_list:
        if weight_type == 'int':
            link.append(int(link[2]))
        elif weight_type == 'float':
            link.append(float(link[2]))
        del link[2]

    return link_list

def extract_paths(G, path_to_file):
    """Helper function to extract paths from .csv files.

    Parameters
    ----------
    G : networkx DiGraph object
        Network representing the total chaîne opératoire for ceramics
    path_to_file : str
        String specifying the location of the paths to extract.

    Returns
    -------
    paths : list of lists
        List of paths, each formatted as a list of nodes.
    """

    #Open file and extract paths
    with open(path_to_file, 'r', encoding='utf-8') as df:
        reader = csv.reader(df, delimiter=';')
        paths = [l for l in reader]

    #Check paths to be sure
    if check_paths(G, paths):
        return paths

#Step 2: Extract the empirical datasets
#Step 2.1: Create a network representation of the total chaîne opératoire
with open('files/nodes_list.csv', 'r', encoding='utf-8') as fn:
    reader = csv.reader(fn, delimiter = ';')
    nodes = [n for n in reader][1:]
G = load_network(
    nodes, 
    links=extract_link_list('files/link_list_uniform.csv', 'int')
    )

#Step 2.2: Extract paths
FBW4 = extract_paths(G, 'files/FBW_4mil.csv')
CW = extract_paths(G, 'files/CW.csv')

#Step 3: Set up a control group based on empirical data about FBN ceramic
#production
C = load_network(
    nodes, 
    links = extract_link_list('files/link_list_FBN.csv', 'int')
    )

#Step 4: Perform a permutation test
#score, percentile, control_scores = permutation_test(
score, percentile, control_scores = permutation_test(
    G=G, 
    a_paths = FBW4, 
    b_paths = CW, 
    C=C, 
    control_size = 100, 
    n_control = 1000,
    termination_chance = 1.0
    )

message = f'Wasserstein distance between FBW4 and CW: {score}. '
message += f'This score is in the {percentile}th percentile of '
message += 'Wasserstein distances to the control group.'
print(message)
#Returns "Outcomes: Wd (FBW4, CW) ca. 0.39, percentile < 5.0."
