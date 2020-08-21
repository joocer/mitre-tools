

class base_mitre_node (object):
    """
    base_mitre_object

    base class for mitre objects to be extended from, ensures all
    mitre nodes have an explicit type and id attribute.
    """
    def __init__(self, node_type, id):
        self.type = node_type
        self.id = id


###########################


class null_node (base_mitre_node):
    """
    null_node

    is the most basic implementation, so you can copy to create your own.
    """
    def __init__(self, id, description):
        base_mitre_node.__init__(self, node_type = "null", id = id)


###########################


class capec_attack_node (base_mitre_node):
    """
    capec_attack_node
    """
    def __init__(self, id, description, likelihood_of_attack, typical_severity):
        base_mitre_node.__init__(self, node_type = "capec", id = id)
        self.description = description
        self.likelihood_of_attack = likelihood_of_attack
        self.typical_severity = typical_severity


###########################



## *********************************************************************

class cve_node (base_mitre_node):
    """
    cve_node

    """
    def __init__(self, id, description):
        base_mitre_node.__init__(self, node_type = "cve", id = id)
        self.a = 1
        self.b = 2
        self.c = 3


class cwe_node (base_mitre_node):

    def __init__(self, a, b, c):
        base_mitre_node.__init__(self, node_type = "cwe", id = id)
        self.a = 1
        self.b = 2
        self.c = 3


class asvs_node (base_mitre_node):

    def __init__(self, a, b, c):
        base_mitre_node.__init__(self, node_type = "asvs", id = id)
        self.a = 1
        self.b = 2
        self.c = 3



a = capec_attack_node("id", "descripion", "likelihood", "severity")

print(a.type, a.id, a.description, a.likelihood_of_attack, a.typical_severity)