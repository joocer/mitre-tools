from datetime import datetime
import pandas as pd
import json
import uuid
import re

base_nvd_data_file = r'../../data/raw/nvdcve-1.1-{year}.json'
capec_stix_filepath = r'../../data/raw/stic-capec.json'
attack_filepath = r'../../data/raw/enterprise-attack.json'

nvd_filepath = r'../../data/intermediate/nvd-cve.csv'
attack_attack_pattern_filepath = r'../../data/intermediate/attack-attack_pattern.csv'
attack_relationship_filepath = r'../../data/intermediate/attack-relationship.csv'
attack_course_of_action_filepath = r'../../data/intermediate/attack-course_of_action.csv'
attack_intrusion_set_filepath = r'../../data/intermediate/attack-intrusion_set.csv'
attack_malware_filepath = r'../../data/intermediate/attack-malware.csv'
attack_tool_filepath = r'../../data/intermediate/attack-tool.csv'
attack_x_mitre_tactic_filepath = r'../../data/intermediate/attack-x_mitre_tactic.csv'
capec_attack_pattern_filepath = r'../../data/intermediate/capec-attack_pattern.csv'
capec_relationship_filepath = r'../../data/intermediate/capec-relationship.csv'
capec_course_of_action_filepath = r'../../data/intermediate/capec-course_of_action.csv'
capec_consequences_filepath = r'../../data/intermediate/capec-consequences.csv'
capec_prerequisite_filepath = r'../../data/intermediate/capec-prerequisite.csv'
exploitdb_filepath = r'../../data/intermediate/mitre-exploitdb.csv'

def find_cves(string):
    tokens = re.findall(r"(?i)CVE.\d{4}-\d{4,7}", string) 
    result = []
    for token in tokens:
        token = token.upper().strip()
        token = token[:3] + '-' + token[4:]  # snort rules list cves as CVE,2009-0001
        result.append(token)
    return result

def process_nvd():
    row_accumulator = []
    currentYear = datetime.now().year
    currentYear = 2020
    for year in range(2002, currentYear + 1):
        print(base_nvd_data_file.replace('{year}', str(year)))
        with open(base_nvd_data_file.replace('{year}', str(year)), 'r', encoding='utf-8') as f:
            nvd_data = json.load(f)
            for entry in nvd_data['CVE_Items']:
                cve = entry['cve']['CVE_data_meta']['ID']
                try:
                    published_date = entry['publishedDate']
                except KeyError:
                    published_date = ''
                try:
                    attack_vector = entry['impact']['baseMetricV3']['cvssV3']['attackVector']
                except KeyError:
                    attack_vector = ''
                try:
                    attack_complexity = entry['impact']['baseMetricV3']['cvssV3']['attackComplexity']
                except KeyError:
                    attack_complexity = ''
                try:
                    privileges_required = entry['impact']['baseMetricV3']['cvssV3']['privilegesRequired']
                except KeyError:
                    privileges_required = ''
                try:
                    user_interaction = entry['impact']['baseMetricV3']['cvssV3']['userInteraction']
                except KeyError:
                    user_interaction = ''
                try:
                    scope = entry['impact']['baseMetricV3']['cvssV3']['scope']
                except KeyError:
                    scope = ''
                try:
                    confidentiality_impact = entry['impact']['baseMetricV3']['cvssV3']['confidentialityImpact']
                except KeyError:
                    confidentiality_impact = ''
                try:
                    integrity_impact = entry['impact']['baseMetricV3']['cvssV3']['integrityImpact']
                except KeyError:
                    integrity_impact = ''
                try:
                    availability_impact = entry['impact']['baseMetricV3']['cvssV3']['availabilityImpact']
                except KeyError:
                    availability_impact = ''
                try:
                    base_score = entry['impact']['baseMetricV3']['cvssV3']['baseScore']
                except KeyError:
                    base_score = ''
                try:
                    base_severity = entry['impact']['baseMetricV3']['cvssV3']['baseSeverity']
                except KeyError:
                    base_severity = ''
                try:
                    exploitability_score = entry['impact']['baseMetricV3']['exploitabilityScore']
                except KeyError:
                    exploitability_score = ''
                try:
                    impact_score = entry['impact']['baseMetricV3']['impactScore']
                except KeyError:
                    impact_score = ''
                try:
                    cwe = entry['cve']['problemtype']['problemtype_data'][0]['description'][0]['value']
                except IndexError:
                    cwe = ''
                try:
                    description = entry['cve']['description']['description_data'][0]['value']
                except IndexError:
                    description = ''

                new_row = { 
                    'CVE': cve, 
                    'Published': published_date,
                    'AttackVector': attack_vector,
                    'AttackComplexity': attack_complexity,
                    'PrivilegesRequired': privileges_required,
                    'UserInteraction': user_interaction,
                    'Scope': scope,
                    'ConfidentialityImpact': confidentiality_impact,
                    'IntegrityImpact': integrity_impact,
                    'AvailabilityImpact': availability_impact,
                    'BaseScore': base_score,
                    'BaseSeverity': base_severity,
                    'ExploitabilityScore': exploitability_score,
                    'ImpactScore': impact_score,
                    'CWE': cwe,
                    'Description': description
                }
                if not description.startswith('**'): # disputed, rejected and other non issues start with '**'
                    row_accumulator.append(new_row)
            
    nvd = pd.DataFrame(row_accumulator)
    nvd.to_csv(nvd_filepath,index=False)

    print ('CVEs from NVD:', nvd['CVE'].count())

def process_attack():
    attack_pattern_accumulator = []
    relationship_accumulator = []
    course_of_action_accumulator = []
    intrusion_set_accumulator = []
    malware_accumulator = []
    tool_accumulator = []
    x_mitre_tactic_accumulator = []

    with open(attack_filepath, 'r') as f:
        attack_data = json.load(f)
        for entry in attack_data['objects']:
            id = entry['id']
            a_type = entry['type']
            if a_type == 'attack-pattern':
                capec_id = ''
                attack_id = ''
                for reference in entry['external_references']:
                    source = reference['source_name']
                    if (source == 'mitre-attack'):
                        attack_id = reference['external_id']
                    if (source == 'capec'):
                        capec_id = reference['external_id']
                new_row = { 
                    'type': a_type,
                    'id': id, 
                    'attack_id': attack_id, 
                    'capec_id': capec_id,
                    'name': entry['name']
                }
                attack_pattern_accumulator.append(new_row)
            elif a_type == 'relationship':
                new_row = {
                    'type': a_type,
                    'id': id,
                    'target': entry['target_ref'],
                    'source': entry['source_ref'],
                    'relationship': entry['relationship_type']
                }
                relationship_accumulator.append(new_row)
            elif a_type == 'course-of-action':
                attack_id = ''
                for reference in entry['external_references']:
                    source = reference['source_name']
                    if (source == 'mitre-attack'):
                        attack_id = reference['external_id']
                new_row = {
                    'type': a_type,
                    'id': id,
                    'attack': attack_id,
                    'name': entry['name']
                }
                course_of_action_accumulator.append(new_row)
            elif a_type == 'intrusion-set':
                new_row = {
                    'type': a_type,
                    'id': id,
                    'name': entry['name']
                }
                intrusion_set_accumulator.append(new_row)
            elif a_type == 'malware':
                new_row = {
                    'type': a_type,
                    'id': id,
                    'name': entry['name']
                }
                malware_accumulator.append(new_row)
            elif a_type == 'tool':
                new_row = {
                    'type': a_type,
                    'id': id,
                    'name': entry['name']
                }
                tool_accumulator.append(new_row)
            elif a_type == 'x-mitre-tactic':
                attack_id = ''
                for reference in entry['external_references']:
                    source = reference['source_name']
                    if (source == 'mitre-attack'):
                        attack_id = reference['external_id']
                new_row = {
                    'type': a_type,
                    'id': id,
                    'attack': attack_id,
                    'name': entry['name']
                }
                x_mitre_tactic_accumulator.append(new_row)
            else:
                print('Other Type', a_type)

    pd.DataFrame(attack_pattern_accumulator).to_csv(attack_attack_pattern_filepath,index=False)
    pd.DataFrame(relationship_accumulator).to_csv(attack_relationship_filepath,index=False)
    pd.DataFrame(course_of_action_accumulator).to_csv(attack_course_of_action_filepath,index=False)
    pd.DataFrame(intrusion_set_accumulator).to_csv(attack_intrusion_set_filepath,index=False)
    pd.DataFrame(malware_accumulator).to_csv(attack_malware_filepath,index=False)
    pd.DataFrame(tool_accumulator).to_csv(attack_tool_filepath,index=False)
    pd.DataFrame(x_mitre_tactic_accumulator).to_csv(attack_x_mitre_tactic_filepath,index=False)    

def process_capec():
    attack_pattern_accumulator = []
    relationship_accumulator = []
    course_of_action_accumulator = []
    attack_prerequisite_accumulator = []

    consequences = {}
    pre_reqs = {}

    with open(capec_stix_filepath, 'r') as f:
        capec_data = json.load(f)
        for entry in capec_data['objects']:
            id = entry['id']
            a_type = entry['type']
            if a_type == 'attack-pattern':
                externals = {}
                for reference in entry['external_references']:
                    source = reference['source_name']
                    if externals.get(source) == None:
                        externals[source] = [reference['external_id']]
                    else:
                        externals[source].append(reference['external_id'])
                for capec in externals['capec']:
                    new_row = {
                            'type': a_type,
                            'id': id,
                            'name': entry['name'],
                            'capec': capec,
                            'likelihood_of_attack': entry.get('x_capec_likelihood_of_attack'),
                            'typical_severity': entry.get('x_capec_typical_severity')
                        }
                    if entry['x_capec_status'] != 'Deprecated':
                        attack_pattern_accumulator.append(new_row)
                    if externals.get('cwe') != None:
                        for cwe in externals['cwe']:
                            new_row = {
                                    'type': 'relationship',
                                    'id': 'relationship++' + str(uuid.uuid4()),
                                    'target': capec,
                                    'source': cwe,
                                    'relationship': 'Enables'
                                }
                            relationship_accumulator.append(new_row)

                    if entry.get('x_capec_prerequisites') != None:
                        for pre in entry.get('x_capec_prerequisites'):
                            if pre_reqs.get(pre) == None:
                                pre_reqs[pre] = 'prereq++' + str(uuid.uuid4())
                            new_row = {
                                'type': 'prerequisites',
                                'id': pre_reqs[pre],
                                }
                            attack_prerequisite_accumulator.append(new_row)
                            new_row = {
                                    'type': 'relationship',
                                    'id': 'relationship++' + str(uuid.uuid4()),
                                    'target': capec,
                                    'source': pre_reqs[pre],
                                    'relationship': 'Requires'
                                }
                            relationship_accumulator.append(new_row)
                            
                if 'x_capec_consequences' in entry:
                    ## consequences aren't a relationship, they're an attribute, 
                    ## making them a relationship needs addtional work
                    for consequence_group in entry['x_capec_consequences']:
                        for consequence in entry['x_capec_consequences'][consequence_group]:
                            consequence_key = consequence_group + consequence
                            if consequence_key in consequences:
                                consequence_id = consequences[consequence_key]['id']
                            else:
                                consequence_id = 'consequence++' + str(uuid.uuid4())
                                consequence = re.sub(r'\([^()]*\)', '', consequence)
                                consequence = re.sub(r'\([^()]*\)', '', consequence)
                                consequence = consequence.strip()
                                consequence_value = { 
                                    'type': 'consequence', 
                                    'id': consequence_id,  
                                    'group': consequence_group, 
                                    'consequence': consequence
                                }
                                consequences[consequence_key] = consequence_value
                            new_row = {
                                'type': 'relationship',
                                'id': 'relationship++' + str(uuid.uuid4()),
                                'target': consequence_id,
                                'source': id,
                                'relationship': 'ResultsIn'
                            }
                            relationship_accumulator.append(new_row)
            elif a_type == 'relationship':
                new_row = {
                    'type': a_type,
                    'id': id,
                    'target': entry['target_ref'],
                    'source': entry['source_ref'],
                    'relationship': entry['relationship_type']
                }
                relationship_accumulator.append(new_row)
            elif a_type == 'course-of-action':
                new_row = {
                    'type': a_type,
                    'id': id,
                    'name': entry['name'],
                    'description': entry['description']
                }
                course_of_action_accumulator.append(new_row)
            else:
                print('Other Type', a_type)

    pd.DataFrame(attack_pattern_accumulator).to_csv(capec_attack_pattern_filepath,index=False)
    pd.DataFrame(relationship_accumulator).to_csv(capec_relationship_filepath,index=False)
    pd.DataFrame(course_of_action_accumulator).to_csv(capec_course_of_action_filepath,index=False)
    pd.DataFrame(consequences.values()).to_csv(capec_consequences_filepath,index=False)
    pd.DataFrame(attack_prerequisite_accumulator).to_csv(capec_prerequisite_filepath, index=False)

process_attack()
process_capec()
process_nvd()