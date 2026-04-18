from pydantic import BaseModel, Field
from typing import Dict, List, Any


class NodeInfo(BaseModel):
    max_drones: int = Field(default=999)
    zone: str = Field(default='NORMAL')


class EdgeInfo(BaseModel):
    cap: int = Field(default=999)


class Graph(BaseModel):
    nodes: Dict[str, NodeInfo] = Field(default_factory=dict)
    edges: Dict[frozenset[str], EdgeInfo] = Field(default_factory=dict)
    start: str = Field(default='')
    end: str = Field(default='')
    adj: Dict[str, List[str]] = Field(default_factory=dict)

    model_config = {'arbitrary_types_allowed': True}

    def build(self, raw_nodes: Dict[str, Any],
              raw_edges: Dict[frozenset[str], int],
              start: str, end: str) -> None:
        self.start = start
        self.end = end
        self.adj = {name: [] for name in raw_nodes}
        for name, node in raw_nodes.items():
            self.nodes[name] = NodeInfo(
                max_drones=node.META.MAX_DRONES,
                zone=node.META.ZONE
            )
        for key, cap in raw_edges.items():
            names = list(key)
            self.edges[key] = EdgeInfo(cap=cap)
            self.adj[names[0]].append(names[1])
            self.adj[names[1]].append(names[0])

    def neighbors(self, name: str) -> List[str]:
        return self.adj.get(name, [])

    def is_blocked(self, name: str) -> bool:
        return self.nodes[name].zone == 'BLOCKED'

    def is_unlimited(self, name: str) -> bool:
        return name in (self.start, self.end)

    def move_cost(self, name: str) -> int:
        costs = {'NORMAL': 1, 'RESTRICTED': 2, 'PRIORITY': 0, 'BLOCKED': 999}
        return costs.get(self.nodes[name].zone, 1)
