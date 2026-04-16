from src.colors import Colors, Format
from pydantic import BaseModel, Field, model_validator
from typing import List, Set, Self, Any
from datetime import datetime
from time import sleep
from sys import stderr, stdout
from re import sub


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
    MAX_LINK: dict[tuple[int, int], int] = Field(default={})
    VALUE: tuple[int, int] = Field(default=((0, 0)))
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

    def render(self, all_nodes: dict[str, Node]) -> None:
        import re

        def strip_ansi(text: str) -> str:
            return re.sub(r'\033\[[0-9;]*m', '', text)

        max_x = max(n.VALUE[0] for n in all_nodes.values())
        max_y = max(n.VALUE[1] for n in all_nodes.values())

        cell_w: int = 16
        canvas_h: int = (max_y + 1) * 3
        canvas_w: int = (max_x + 1) * cell_w
        canvas: List[List[str]] = [[' '] * canvas_w for _ in range(canvas_h)]

        def place(text: str, row: int, col: int) -> None:
            clean = strip_ansi(text)
            chunks = re.split(r'(\033\[[0-9;]*m)', text)
            ci: int = col
            current_code: str = ''
            for chunk in chunks:
                if (re.match(r'\033\[[0-9;]*m', chunk)):
                    current_code += chunk
                else:
                    for ch in chunk:
                        if 0 <= row < len(canvas) and 0 <= ci < canvas_w:
                            canvas[row][ci] = current_code + ch
                            current_code = ''
                        ci += 1

        for node in all_nodes.values():
            x, y = node.VALUE
            cx: int = x * cell_w
            cy: int = y * 3
            label: str = f'{node.NAME}({node.DRONE_COUNT})'
            label_len: int = len(strip_ansi(label))
            place(label, cy, cx)

            for adj in node.ADJ:
                if (adj.VALUE <= node.VALUE):
                    continue
                ax, ay = adj.VALUE
                dy = ay - y
                dx = ax - x

                if (dx < 0) or (dx == 0 and dy < 0):
                    continue

                if (dx == 0 and dy == 0):
                    continue

                if (dy == 0):
                    adj_label_len: int = len(strip_ansi(f'{adj.NAME}({adj.DRONE_COUNT})'))
                    arrow_len: int = cell_w * dx - label_len
                    arrow = '|' + '—' * (arrow_len)
                    place(arrow, cy, cx + label_len)

                elif (dy > 0 and dx == 0):
                    for step in range(1, dy * 3):
                        place('│', cy + step, cx + label_len // 2)
                    place('v', cy + dy * 3, cx + label_len // 2)

                elif (dy > 0 and dx > 0):
                    for step in range(1, dy * 3):
                        place('╲', cy + step, cx + label_len + step)

                elif (dy < 0 and dx > 0):
                    for step in range(1, abs(dy) * 3):
                        place('╱', cy - step, cx + label_len + step)

        lines: List[str] = []
        for row in canvas:
            line = ''.join(row).rstrip()
            lines.append(line)

        while (lines and not lines[-1].strip()):
            lines.pop()

        if (self.frame_lines > 0):
            stdout.write(f'\x1b[{self.frame_lines}A')
            stdout.write('\x1b[J')
            stdout.flush()

        for line in lines:
            print(line + Colors().RESET)
        self.frame_lines = len(lines)

    def solve(self, path: List[Node], all_nodes: dict[str, Node]) -> None:
        start = datetime.now()
        max_count: int = path[0].DRONE_COUNT
        self.logger.log('# TRAVELING...')
        turn: int = 0
        frames: List[tuple[List[str]]] = []
        states: List[dict[Node, int]] = []
        while (path[-1].DRONE_COUNT != max_count):
            snapshot: List[int] = [node.DRONE_COUNT for node in path]
            for i in range(len(path) - 1, 0, -1):
                current: Node = path[i - 1]
                plus: Node = path[i]
                send: int = snapshot[i - 1]
                receive: int = plus.META.MAX_DRONES - snapshot[i]

                link_cap = current.MAX_LINK.get(plus.VALUE)
                if (link_cap):
                    send = min(send, link_cap)

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
            states.append({n: n.DRONE_COUNT for n in all_nodes.values()})
        end = datetime.now()
        elapsed = (end - start).total_seconds() * 1000
        self.logger.log(f'# DONE: {max_count} drones traveled to goal')
        self.logger.log(f'# TURN COUNT: {turn} turns in {elapsed:.3f}ms')
        print('')
        for state in states:
            for node, count in state.items():
                node.DRONE_COUNT = count
            self.render(all_nodes)
            sleep(1)


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
                        capacity: int = 0
                        if (' ' in b):
                            tmp: Any
                            b, tmp = b.split(' ', 1)
                            capacity = int(tmp.strip('[]').split('=')[1])
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
                self.generator.solve(path, self.nodes)
        self.generator.reset()
        self.nodes = {}
