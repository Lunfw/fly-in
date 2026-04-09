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
            self.ZONE = 'normal'
        return (self)

    @model_validator(mode='after')
    def validate_color(self) -> Self:
        self.COLOR = self.COLOR
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
    NAME: str = Field(default='')
    ADJ: (List[Self]) = Field(default=[])
    MAX_LINK: List[int] = Field(default=[])
    VALUE: tuple[int, int] = Field(default=((0, 0)))
    DRONE_COUNT: int = Field(default=0)
    META: MetaData = Field(default=MetaData())

    def __hash__(self) -> int:
        return (hash(self.VALUE))

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, Node)):
            return (False)
        return (self.VALUE == other.VALUE)

    def connect(self, other: Self) -> None:
        self.ADJ.append(other)

    @model_validator(mode='after')
    def validate_self(self) -> Self:
        if (self.VALUE[0] < 0 or self.VALUE[0] < 0):
            Format().putstr(
                    Format().colored('\n# INVALID NODE', 'RED'),
                    stderr)
            self.VALUE = (0, 0)
        return (self)


class Logger(BaseModel):
    logs: List[str] = Field(default_factory=list)
    form: Format = Field(default=Format())

    def log(self, message: str) -> None:
        timestamp: str = datetime.now().strftime('%H:%M:%S')
        entry = f'│ [{timestamp}] {message}'
        self.logs.append(entry)
        print(entry)


class Generator(BaseModel):
    visited: Set[Node] = Field(default_factory=set)
    logger: Logger = Field(default=Logger())

    def reset(self) -> None:
        self.visited.clear()
        self.logger.logs.clear()

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

    def dij(self, start: Node, goal: Node) -> List[Node]:
        from heapq import heappop, heappush

        PRIORITIES: dict[str, int | None] = {
                'NORMAL': 1,
                'BLOCKED': None,
                'RESTRICTED': 2,
                'PRIORITY': 0,
                }
        dist: dict[Node, int] = {start: 0}
        parent: dict[Node, Node | None] = {start: None}
        heap: List[tuple[int, int, Node]] = [(0, id(start), start)]

        while (heap):
            c, _, node = heappop(heap)
            self.logger.log(f'# VISITING: {node.NAME} at {node.VALUE} ({c})')

            if (node == goal):
                break
 
            for adj in node.ADJ:
                zone_cost = PRIORITIES.get(adj.META.ZONE)
                if (zone_cost is None):
                    continue
                new_cost = c + zone_cost
                if (adj not in dist or new_cost < dist[adj]):
                    dist[adj] = new_cost
                    parent[adj] = node
                    self.logger.log(f'# QUEUED: {adj.NAME}')
                    heappush(heap, (new_cost, id(adj), adj))

        path: List[Node] = []
        current: Node | None = goal
        while (current is not None):
            path.append(current)
            current = parent.get(current)
        path.reverse()

        if (not path or path[0] != start):
            Format().putstr(Format().colored('\n# NO PATH', 'RED'), stderr)
            return []

        self.logger.log(f'# PATH COST: {dist.get(goal, -1)}')
        return (path)

    def solve(self, path: List[Node]) -> None:
        start = datetime.now()
        max_count: int = path[0].DRONE_COUNT
        self.logger.log('# TRAVELING...')
        turn: int = 0
        while (path[-1].DRONE_COUNT != max_count):
            snapshot: List[int] = [node.DRONE_COUNT for node in path]
            for i in range(len(path) - 1, 0, -1):
                current: Node = path[i - 1]
                plus: Node = path[i]
                send: int = current.DRONE_COUNT
                receive: int = plus.META.MAX_DRONES - snapshot[i]

                if (current.MAX_LINK and i - 1 < len(current.MAX_LINK)):
                    send = min(send, current.MAX_LINK[i - 1])

                if (current.META.ZONE == 'RESTRICTED'):
                    turn += 1

                move: int = min(send, receive)
                if (move > 0):
                    current.DRONE_COUNT -= move
                    plus.DRONE_COUNT += move
                    self.logger.log(
                            f'# STEP: {move} of {current.NAME} '
                            f'({current.DRONE_COUNT})'
                            f' -> {plus.NAME} ({plus.DRONE_COUNT})'
                            )
            turn += 1
        end = datetime.now()
        elapsed = (end - start).total_seconds() * 1000
        self.logger.log(f'# DONE: {max_count} drones traveled to goal')
        self.logger.log(f'# TURN COUNT: {turn} turns in {elapsed:.3f}ms')


class Parser(BaseModel):
    file: str = Field(default='')
    buffer: str = Field(default='')
    start: str = Field(default='start')
    goal: str = Field(default='goal')
    nodes: dict[str, Node] = Field(default={})
    nb_drones: int = Field(default=0)
    generator: Generator = Field(default=Generator())

    def receive(self, filename: str, code: str = 'dfs') -> None:
        with open(filename, 'r') as f:
            self.buffer = f.read()
            self.file = filename
        f.close()
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
                    if (key != 'connection' and len(part[3]) > 3):
                        metadata: Any[str] = '='.join(part[3:]).strip('[]')
                        metadata = metadata.split('=')
                        tup: tuple[str, str, str] = ('color',
                                                     'zone',
                                                     'max_drones',
                                                     )
                        for i in range(len(metadata)):
                            if (metadata[i] in tup):
                                if (metadata[i + 1].isdigit()):
                                    metadata[i + 1] = int(metadata[i + 1])
                                else:
                                    metadata[i + 1] = metadata[i + 1].upper()
                                setattr(meta,
                                        metadata[i].upper(),
                                        metadata[i + 1]
                                        )
                        if (not meta.MAX_DRONES):
                            meta.MAX_DRONES = self.nb_drones
                    if (key != 'connection'):
                        coords: tuple[int, int] = (int(part[1]), int(part[2]))
                        if (not meta.MAX_DRONES):
                            meta.MAX_DRONES = self.nb_drones
                        node: Node = Node(VALUE=coords, META=meta)
                        self.nodes[part[0]] = node
                        node.NAME = Format().colored(part[0].upper(),
                                                     node.META.COLOR)
                    if (key == 'start_hub'):
                        self.start = part[0]
                    elif (key == 'end_hub'):
                        self.goal = part[0]
                    elif (key == 'connection'):
                        a, b = value.split('-')
                        if (' ' in b):
                            tmp: Any
                            b, tmp = b.split(' ', 1)
                            tmp = int(tmp.strip('[]').split('=')[1])
                            self.nodes[a].MAX_LINK.append(int(tmp))
                            self.nodes[b].MAX_LINK.append(int(tmp))
                        self.nodes[a].connect(self.nodes[b])
                        self.nodes[b].connect(self.nodes[a])
            except IndexError:
                Format().putstr(
                        Format().colored('\n# INVALID PARAM', 'RED'),
                        stderr)
        if (code == 'dfs'):
            Format().putstr('\n# MAPPED')
            self.generator.dfs(self.nodes[self.start])
        else:
            Format().putstr('\n# SOLVED')
            path = self.generator.dij(self.nodes[self.start],
                                      self.nodes[self.goal]
                                      )
            if (not len(path)):
                return
            path[0].DRONE_COUNT = self.nb_drones
            print('\n# PATH:', end='\n│ ')
            for j in path:
                print(j.NAME, end='')
                if (j != path[-1]):
                    print(' -> ', end='')
            Format().putstr('')
            if (path):
                self.generator.solve(path)
        self.generator.reset()
        self.nodes = {}
