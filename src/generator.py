from src.colors import Colors, Format
from pydantic import BaseModel, Field, model_validator
from typing import List, Set, Self, Any
from datetime import datetime
from sys import stderr


class MetaData(BaseModel):
    ZONE: str = Field(default='NORMAL')
    COLOR: str = Field(default='NONE')
    MAX_DRONES: int = Field(default=0, ge=0)

    @model_validator(mode='after')
    def validate_zone(self) -> Self:
        valid_zones: tuple[str, str, str, str] = ('NORMAL',
                                                  'BLOCKED',
                                                  'RESTRICTED',
                                                  'PRIORITY'
                                                  )
        if (self.ZONE not in valid_zones):
            Format().putstr(
                    Format().colored('# INVALID ZONE', 'RED'),
                    stderr)
            self.ZONE = 'NORMAL'
        return (self)

    @model_validator(mode='after')
    def validate_color(self) -> Self:
        valid_colors: List[str] = Colors().get_colors()
        if (self.COLOR not in valid_colors):
            Format().putstr(
                    Format().colored('\n# INVALID COLOR', 'RED'),
                    stderr)
            self.COLOR = 'NONE'
        return (self)

    @model_validator(mode='after')
    def validate_drones(self) -> Self:
        if (self.MAX_DRONES < 0):
            Format().putstr(
                    Format().colored('\n# NB_DRONES < 0', 'RED'),
                    stderr)
            self.MAX_DRONES = 1
        return (self)


class Node(BaseModel):
    NAME: (str | List[str]) = Field(default='')
    ADJ: List[Self] = Field(default=[])
    MAX_LINK: dict[tuple[int, int], int] = Field(default={})
    VALUE: tuple[int, int] = Field(default=(0, 0))
    DRONE_COUNT: int = Field(default=0)
    META: MetaData = Field(default=MetaData())

    def __hash__(self) -> int:
        return (hash(self.VALUE))

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, Node)):
            return (False)
        return (self.VALUE == other.VALUE)

    def connect(self, other: Self, capacity: int = 0) -> None:
        self.ADJ.append(other)
        if (capacity):
            self.MAX_LINK[other.VALUE] = capacity


class Logger(BaseModel):
    logs: List[str] = Field(default_factory=list)

    def log(self, message: str) -> None:
        timestamp: str = datetime.now().strftime('%H:%M:%S')
        entry = f'│ [{timestamp}] {message}'
        self.logs.append(entry)
        print(entry)


class Generator(BaseModel):
    visited: Set[Node] = Field(default_factory=set)
    logger: Logger = Field(default_factory=Logger)
    frame_lines: int = Field(default=0)

    def reset(self) -> None:
        self.visited.clear()
        self.logger.logs.clear()
        self.frame_lines = 0

    def dfs(self, node: Node, prefix: str = '', is_last: bool = True) -> None:
        if (is_last):
            connector = '└── '
        else:
            connector = '├── '

        Format().putstr(f'{prefix}{connector}{node.NAME}')
        prefix += '│   '

        self.visited.add(node)
        unvisited: List[Node] = [i for i in node.ADJ if i not in self.visited]
        for j, child in enumerate(unvisited):
            is_last_child: bool = (j == len(unvisited) - 1)
            if (is_last):
                extension = '    '
            else:
                extension = '│   '
            self.dfs(child, prefix + extension, is_last_child)


class Parser(BaseModel):
    file: str = Field(default='')
    buffer: str = Field(default='')
    start: str = Field(default='start')
    goal: str = Field(default='goal')
    nodes: dict[str, Node] = Field(default_factory=dict)
    nb_drones: int = Field(default=0)
    generator: Generator = Field(default_factory=Generator)
    edges: dict[frozenset[str], int] = Field(default_factory=dict)

    model_config = {'arbitrary_types_allowed': True}

    def reset(self) -> None:
        self.nodes = {}
        self.edges = {}
        self.start = 'start'
        self.goal = 'goal'
        self.nb_drones = 0
        self.buffer = ''
        self.file = ''
        self.generator.reset()

    def receive(self, filename: str, code: str = 'dfs') -> None:
        with open(filename, 'r') as f:
            self.buffer = f.read()
            self.file = filename
        self.parser(code)

    def parser(self, code: str) -> None:
        for line in self.buffer.split('\n'):
            line = line.strip()
            if (not line or line.startswith('#') or ': ' not in line):
                continue
            key, value = line.split(': ', 1)
            part: List[str] = value.split(' ')
            try:
                if (key == 'nb_drones'):
                    self.nb_drones = int(part[0])
                elif (key in ('start_hub', 'end_hub', 'hub', 'connection')):
                    meta: MetaData = MetaData()
                    if (key != 'connection'
                        and len(part) > 3
                            and len(part[3]) > 3):
                        metadata: Any = '='.join(part[3:]).strip('[]')
                        metadata = metadata.split('=')
                        tup: tuple[str, str, str] = ('color',
                                                     'zone',
                                                     'max_drones')
                        for i in range(len(metadata)):
                            if (metadata[i] in tup):
                                if (metadata[i + 1].isdigit()):
                                    metadata[i + 1] = int(metadata[i + 1])
                                else:
                                    metadata[i + 1] = metadata[i + 1].upper()
                                setattr(meta,
                                        metadata[i].upper(),
                                        metadata[i + 1])
                        if (not meta.MAX_DRONES):
                            meta.MAX_DRONES = self.nb_drones
                    if (key != 'connection'):
                        coords: tuple[int, int] = (int(part[1]), int(part[2]))
                        if (not meta.MAX_DRONES):
                            meta.MAX_DRONES = self.nb_drones
                        node: Node = Node(VALUE=coords, META=meta)
                        self.nodes[part[0]] = node
                        if (meta.COLOR == 'RAINBOW'):
                            node.NAME = Colors().RAINBOW(part[0].upper())
                        else:
                            node.NAME = Format().colored(part[0].upper(),
                                                         meta.COLOR)
                    if (key == 'start_hub'):
                        self.start = part[0]
                    elif (key == 'end_hub'):
                        self.goal = part[0]
                    elif (key == 'connection'):
                        a, b = value.split('-')
                        capacity: int = 0
                        if (' ' in b):
                            b, tmp = b.split(' ', 1)
                            capacity = int(tmp.strip('[]').split('=')[1])
                        b = b.strip()
                        k = frozenset({a, b})
                        self.edges[k] = capacity if capacity else 999
                        self.nodes[a].connect(self.nodes[b], capacity)
                        self.nodes[b].connect(self.nodes[a], capacity)
            except IndexError:
                Format().putstr(
                        Format().colored('\n# INVALID PARAM', 'RED'),
                        stderr)
        if (code == 'dfs'):
            Format().putstr('\n# MAPPED')
            self.generator.dfs(self.nodes[self.start])
        else:
            from src.graph import Graph
            from src.planner import Planner, ReservationTable
            Format().putstr('\n# SOLVED')
            graph = Graph()
            graph.build(self.nodes, self.edges, self.start, self.goal)
            res = ReservationTable(graph)
            planner = Planner(graph, res, self.generator.logger)
            max_turn: int = 0
            for i in range(self.nb_drones):
                transitions = planner.find_path(self.start, start_turn=0)
                if (transitions is None):
                    self.generator.logger.log(
                            f'# DRONE {i + 1}: NO PATH FOUND')
                    continue
                planner.commit(transitions)
                events = planner.to_events(transitions, self.start, 0)
                planner.log_events(events, i + 1, self.nodes)
                arrival = max(t for t, _, _ in events)
                max_turn = max(max_turn, arrival)
                self.generator.logger.log(Format().colored(
                    f'# DRONE {i + 1} -> DONE!!', 'GOLD'))
            self.generator.logger.log(f'# MAX TURN: {max_turn}')
        self.reset()
