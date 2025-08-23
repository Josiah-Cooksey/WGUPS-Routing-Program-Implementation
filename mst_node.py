from __future__ import annotations
from hash_table import HashTable

# just a start point, other nodes that it connects to, and the distances between each
class MSTNode():
    def __init__(self, label):
        self.label = label
        self.nodes = HashTable()
    
    def add_node(self, node: MSTNode, distance):
        self.nodes.insert(node, distance)
    
    def remove_node(self, node: MSTNode):
        return self.nodes.remove_by_key(node)
    
    def __str__(self):
        return f"MSTNode({self.label})"
    
    def __repr__(self):
        return f"MSTNode({self.label})"
    
    def __getitem__(self, index):
        return [x for x in self.nodes][index]
    
    def __eq__(self, other):
        if isinstance(other, MSTNode) and other.label == self.label:
            return True
        return False