from src.colors import Colors, Format
from pydantic import BaseModel, Field, model_validator
from typing import List, Self
from sys import stderr


class MetaData(BaseModel):
    ZONE: str = Field(default='NORMAL')
    COLOR: str = Field(default='NONE')
    MAX_DRONES: int = Field(default=1, ge=0)
    MAX_LINK_CAPACITY: int = Field(default=0, ge=0)

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

    @model_validator(mode='after')
    def validate_capacity(self) -> Self:
        if (self.MAX_LINK_CAPACITY < 0):
            Format().putstr(
                    Format().colored('\n# CAPACITY < 0', 'RED'),
                    stderr)
            self.MAX_LINK_CAPACITY = 1
        return (self)


class Node(BaseModel):
    ADJ: (List[Self]) = Field(default=[])
    VALUE: tuple[int, int] = Field(default=((0, 0)))
    META: MetaData = Field(default=MetaData())

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


class Generator(BaseModel):
    file: str = Field(default='')
    buffer: str = Field(default='')
    start: tuple[int, int] = Field(default=(0, 0))
    goal: tuple[int, int] = Field(default=(0, 0))
    nodes: dict[str, Node] = Field(default={})
    nb_drones: int = Field(default=0)

    def debug(self) -> None:
        print(f'\nFILENAME: {self.file}')
        print(f'START: {self.start}')
        print(f'GOAL: {self.goal}')
        print(f'NB_DRONES: {self.nb_drones}')
        print('NODES:')
        for i in list(self.nodes.values()):
            print(f'\n#   {i.VALUE} | [{i.META}]')
            for j in i.ADJ:
                print(f'    ->| {j.VALUE}')
        print('')

    def receive(self, filename: str) -> None:
        with open(filename, 'r') as f:
            self.buffer = f.read()
            self.file = filename
        f.close()
        self.parser()

    def parser(self) -> None:
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
                        metadata: List[str] = part[3].strip('[]').split('=')
                        tup: tuple[str, str, str, str] = ('color',
                                                         'zone',
                                                         'max_drones',
                                                         'max_link_capacity'
                                                         )
                        for i in range(len(metadata)):
                            if (metadata[i] in tup):
                                setattr(meta,
                                        metadata[i].upper(),
                                        metadata[i + 1].upper()
                                        )
                    if (key != 'connection'):
                        coords: tuple[int, int] = (int(part[1]), int(part[2]))
                        node: Node = Node(VALUE=coords, META=meta)
                        self.nodes[part[0]] = node
                    if (key == 'start_hub'):
                        self.start = node.VALUE
                    elif (key == 'end_hub'):
                        self.goal = node.VALUE
                    elif (key == 'connection'):
                        a, b = value.split('-')
                        self.nodes[a].connect(self.nodes[b])
                        self.nodes[b].connect(self.nodes[a])
            except IndexError:
                Format().putstr(
                        Format().colored('\n# INVALID PARAM', RED),
                        stderr)
        self.debug()
        self.nodes = {}
