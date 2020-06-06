import networkx as nx
import pandas as pd
import re
import time

capec_attack_pattern_filepath = r'../../data/intermediate/capec-attack_pattern.csv'
capec_relationship_filepath = r'../../data/intermediate/capec-relationship.csv'
capec_course_of_action_filepath = r'../../data/intermediate/capec-course_of_action.csv'
capec_consequences_filepath = r'../../data/intermediate/capec-consequences.csv'
capec_prerequisite_filepath = r'../../data/intermediate/capec-prerequisite.csv'

asvs_filepath = r'../../data/raw/OWASP Application Security Verification Standard 4.0-en.csv'
cwe_filepath = r'../../data/raw/2000-cwe.csv'

## currently aren't loading these into the graph
nvd_filepath = r'../../data/intermediate/nvd-cve.csv'
exploitdb_filepath = r'../../data/raw/mitre-exploitdb.csv'
attack_malware_filepath = r'../../data/intermediate/attack-malware.csv'
attack_intrusion_set_filepath = r'../../data/intermediate/attack-intrusion_set.csv'
attack_tool_filepath = r'../../data/intermediate/attack-tool.csv'
attack_relationship_filepath = r'../../data/intermediate/attack-relationship.csv'
attack_x_mitre_tactic_filepath = r'../../data/intermediate/attack-x_mitre_tactic.csv'
attack_course_of_action_filepath = r'../../data/intermediate/attack-course_of_action.csv'
attack_attack_pattern_filepath = r'../../data/intermediate/attack-attack_pattern.csv'

def find_relationships(string):
    tokens = re.findall(r"(?i)ChildOf\:CWE ID\:\d{1,5}", string) 
    result = []
    for token in tokens:
        result.append('CWE-' + token[15:])
    return result

def find_cves(string):
    tokens = re.findall(r"(?i)CVE.\d{4}-\d{4,7}", string) 
    result = []
    for token in tokens:
        token = token.upper().strip()
        token = token[:3] + '-' + token[4:]  # snort rules list cves as CVE,2009-0001
        result.append(token)
    return result

# new graph
graph = nx.DiGraph()

###########################

capecs = {}
coa = {}

###########################

print('capec_attack_pattern_filepath')
data = pd.read_csv(capec_attack_pattern_filepath)

# add nodes
for i, row in data.iterrows():
    graph.add_node(row['capec'], 
                   label=row['capec'], 
                   kind='capec', 
                   description=row['name'],
                   likelihood_of_attack=row['likelihood_of_attack'],
                   typical_severity=row['typical_severity']
                  )    
    capecs[row['id']] = row['capec']

print (len(graph.nodes), len(graph.edges))

###########################

print('capec_course_of_action_filepath')
data = pd.read_csv(capec_course_of_action_filepath)

# add nodes
for i, row in data.iterrows():
    graph.add_node(row['name'], 
                   label=row['name'], 
                   description=row['description'],
                   kind='course of action')
    coa[row['id']] = row['name']

print (len(graph.nodes), len(graph.edges))

###########################

print('capec_consequences_filepath')
data = pd.read_csv(capec_consequences_filepath)

# add nodes
for i, row in data.iterrows():
    graph.add_node(row['id'], label=row['consequence'], kind='consequence', group=row['group'])

print (len(graph.nodes), len(graph.edges))

###########################

print('capec_prerequisite_filepath')
data = pd.read_csv(capec_prerequisite_filepath)

# add nodes
for i, row in data.iterrows():
    graph.add_node(row['id'], label=row['id'], kind='prerequisite')

print (len(graph.nodes), len(graph.edges))

###########################

print('cwe_filepath')
data = pd.read_csv(cwe_filepath, index_col=False)
data.fillna('', inplace=True)

# add nodes
for i, row in data.iterrows():
    graph.add_node('CWE-' + str(row['CWE-ID']), 
                   label='CWE-' + str(row['CWE-ID']), 
                   kind='cwe', 
                   name=row['Name'])
    
# add edges
for i, row in data.iterrows():
    for rel in find_relationships(row['Related Weaknesses']):
        graph.add_edge(rel, 'CWE-' + str(row['CWE-ID']), relationship='ChildOf')
        graph.add_edge('CWE-' + str(row['CWE-ID']), rel, relationship='ParentOf')

print (len(graph.nodes), len(graph.edges))

###########################

print('asvs_filepath')
data = pd.read_csv(asvs_filepath, index_col=False)
data.fillna('', inplace=True)

# add nodes
for i, row in data.iterrows():
    graph.add_node('ASVS-' + str(row['Item']), 
                   label='ASVS-' + str(row['Item']),
                   kind='asvs', 
                   description=row['Description'],
                   section_id=row['Section'],
                   section_name=row['Name'])
    
# add edges
for i, row in data.iterrows():
    CWE = row['CWE']
    if CWE != '':
        CWE = 'CWE-' + str(int(CWE))
        graph.add_edge('ASVS-' + str(row['Item']), CWE, relationship='Prevents')
        graph.add_edge(CWE, 'ASVS-' + str(row['Item']), relationship='Inverse-Prevents')

print (len(graph.nodes), len(graph.edges))

###########################

print('capec_relationship_filepath')
data = pd.read_csv(capec_relationship_filepath)

# add edges
for i, row in data.iterrows():
    relationship = row['relationship']
    if relationship == 'mitigates':
        graph.add_edge(coa.get(row['source']), capecs.get(row['target']), relationship='Mitigates')
        graph.add_edge(capecs.get(row['target']), coa.get(row['source']), relationship='Inverse-Mitigates')
    elif relationship == 'ResultsIn':
        graph.add_edge(capecs.get(row['source']), row['target'], relationship=relationship)
        graph.add_edge(row['target'], capecs.get(row['source']), relationship='Inverse-' + relationship)
    else:
        graph.add_edge(row['source'], row['target'], relationship=relationship)
        graph.add_edge(row['target'], row['source'], relationship='Inverse-' + relationship)

print (len(graph.nodes), len(graph.edges))

###########################

print('saving to graphml')
nx.write_graphml(graph, r'../../data/processed/mitre-data.graphml')
print ('done')