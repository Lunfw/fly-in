import heapq
from typing import Dict, FrozenSet, List, Optional, Tuple
from src.graph import Graph

State = Tuple[str, int]
Transition = Tuple[State, State, Optional[Tuple[str, str]]]
Event = Tuple[int, str, object]


class ReservationTable:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.node: Dict[Tuple[str, int], int] = {}
        self.edge: Dict[Tuple[FrozenSet[str], int], int] = {}

    def node_full(self, name: str, turn: int) -> bool:
        if (self.graph.is_unlimited(name)):
            return False
        cap = self.graph.nodes[name].max_drones
        return self.node.get((name, turn), 0) >= cap

    def edge_full(self, a: str, b: str, turn: int) -> bool:
        k = frozenset({a, b})
        cap = self.graph.edges[k].cap
        return self.edge.get((k, turn), 0) >= cap

    def add_node(self, name: str, turn: int) -> None:
        self.node[(name, turn)] = self.node.get((name, turn), 0) + 1

    def add_edge(self, a: str, b: str, turn: int) -> None:
        k = frozenset({a, b})
        self.edge[(k, turn)] = self.edge.get((k, turn), 0) + 1


class Planner:
    MAX_TURN = 500

    def __init__(self, graph: Graph, reservations: ReservationTable, logger) -> None:
        self.g = graph
        self.res = reservations
        self.logger = logger
        self._h = self._bfs_goal_distance()

    def _bfs_goal_distance(self) -> Dict[str, int]:
        dist: Dict[str, int] = {self.g.end: 0}
        frontier: List[str] = [self.g.end]
        while (frontier):
            nxt: List[str] = []
            for u in frontier:
                for v in self.g.neighbors(u):
                    if (self.g.is_blocked(v)):
                        continue
                    if (v not in dist):
                        dist[v] = dist[u] + 1
                        nxt.append(v)
            frontier = nxt
        return dist

    def _heuristic(self, node: str) -> int:
        return self._h.get(node, 10 ** 6)

    def find_path(self, start: str, start_turn: int = 0) -> Optional[List[Transition]]:
        goal = self.g.end
        open_heap: List[Tuple[int, int, State]] = []
        counter = 0
        init: State = (start, start_turn)
        heapq.heappush(open_heap, (self._heuristic(start), counter, init))
        g_score: Dict[State, int] = {init: 0}
        came_from: Dict[State, Tuple[State, Optional[Tuple[str, str]]]] = {}

        while (open_heap):
            _, _, cur = heapq.heappop(open_heap)
            node, turn = cur
            if (node == goal):
                return self._rebuild(cur, came_from)
            if (turn >= self.MAX_TURN):
                continue
            if (self.g.is_unlimited(node) or not self.res.node_full(node, turn + 1)):
                self._relax(cur, (node, turn + 1), None, 1, g_score, came_from, open_heap)
                counter += 1
            for nb in self.g.neighbors(node):
                if (self.g.is_blocked(nb)):
                    continue
                cost = self.g.move_cost(nb)
                arrive_turn = turn + cost
                if (self.res.edge_full(node, nb, turn)):
                    continue
                if (cost == 2 and self.res.edge_full(node, nb, turn + 1)):
                    continue
                if (self.res.node_full(nb, arrive_turn)):
                    continue
                self._relax(cur, (nb, arrive_turn), (node, nb), cost,
                            g_score, came_from, open_heap)
                counter += 1
        return None

    def _relax(self, cur: State, nxt: State,
               edge: Optional[Tuple[str, str]], cost: int,
               g_score: Dict[State, int],
               came_from: Dict[State, Tuple[State, Optional[Tuple[str, str]]]],
               open_heap: List[Tuple[int, int, State]]) -> None:
        ng = g_score[cur] + cost
        if (ng >= g_score.get(nxt, 10 ** 9)):
            return
        g_score[nxt] = ng
        came_from[nxt] = (cur, edge)
        bonus = -1 if edge and self.g.nodes[edge[1]].zone == 'priority' else 0
        f = ng + self._heuristic(nxt[0]) + bonus
        heapq.heappush(open_heap, (f, len(open_heap), nxt))

    def _rebuild(self, goal_state: State,
                 came_from: Dict[State, Tuple[State, Optional[Tuple[str, str]]]],
                 ) -> List[Transition]:
        transitions: List[Transition] = []
        cur = goal_state
        while (cur in came_from):
            prev, edge = came_from[cur]
            transitions.append((prev, cur, edge))
            cur = prev
        transitions.reverse()
        return transitions

    def commit(self, transitions: List[Transition]) -> None:
        for prev, cur, edge in transitions:
            u, t = prev
            v, t2 = cur
            if (edge is None):
                if (not self.g.is_unlimited(u)):
                    self.res.add_node(u, t2)
            else:
                self.res.add_edge(u, v, t)
                if (t2 - t == 2):
                    self.res.add_edge(u, v, t + 1)
                if (not self.g.is_unlimited(v)):
                    self.res.add_node(v, t2)

    def to_events(self, transitions: List[Transition],
                  start: str, start_turn: int) -> List[Event]:
        events: List[Event] = [(start_turn, 'at', start)]
        for prev, cur, edge in transitions:
            u, t = prev
            v, t2 = cur
            if (edge is None):
                events.append((t2, 'at', u))
            elif (t2 - t == 1):
                events.append((t2, 'at', v))
            else:
                events.append((t + 1, 'transit', (u, v)))
                events.append((t2, 'at', v))
        return events

    def log_events(self, events: List[Event], drone_id: int, raw_nodes: dict) -> None:
        from src.colors import Format
        for t, kind, data in sorted(events, key=lambda e: e[0]):
            if (kind == 'at'):
                name = Format().colored(data.upper(), raw_nodes[data].META.COLOR)
                self.logger.log(f'# DRONE {drone_id}: at {name} (turn {t})')
            elif (kind == 'transit'):
                a, b = data
                na = Format().colored(a.upper(), raw_nodes[a].META.COLOR)
                nb = Format().colored(b.upper(), raw_nodes[b].META.COLOR)
                self.logger.log(f'# DRONE {drone_id}: {na} -> {nb} (turn {t})')
