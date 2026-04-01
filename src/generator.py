from src.colors import Colors, Format
from pydantic import BaseModel, Field, model_validator, BeforeValidator
from typing import List, Self
from sys import stderr


class MetaData(BaseModel):
    ZONE: str = Field(default='normal')
    COLOR: str = Field(default='NONE')
    MAX_DRONES: int = Field(default=1, ge=0)
    form: Format = Field(default=Format())
    colors: Colors = Field(default=Colors())

    @model_validator(mode='after')
    def validate_zone(self) -> Self:
        valid_zones: tuple[str, str, str, str] = ('normal',
                                                  'blocked',
                                                  'restricted',
                                                  'priority'
                                                  )
        if (self.ZONE not in valid_zones):
            self.form.putstr(
                    self.form.colored('# INVALID ZONE', self.colors.RED),
                    stderr)
            self.ZONE = 'normal'
        return (self)

    @model_validator(mode='after')
    def validate_color(self) -> str:
        valid_colors: tuple[str] = self.colors.get_colors()
        if (self.COLOR not in valid_colors):
            self.form.putstr(
                    self.form.colored('# INVALID COLOR', self.colors.RED),
                    stderr)
            self.COLOR = 'NONE'
        return (self)

    @model_validator(mode='after')
    def validate_drones(self) -> int:
        if (self.MAX_DRONES <= 0):
            self.form.putstr(
                    self.form.colored('# NB_DRONES < 0', self.colors.RED),
                    stderr)
            self.MAX_DRONES = 1
        return (self)


class Node(BaseModel):
    ADJ: (List[Self] | List[None]) = Field(default=[])
    VALUE: tuple[int, int] = Field(default=((0, 0)))
    META: MetaData = Field(default=MetaData())

    def connect(self, other: Self) -> None:
        self.ADJ.append(other)

    @model_validator(mode='after')
    def validate_self(self) -> tuple[int, int]:
        if (self.VALUE[0][0] < 0 or self.VALUE[0][1] < 0):
            self.form.putstr(
                    self.form.colored('# INVALID NODE', self.colors.RED),
                    stderr)
            return (0, 0)
        return (self.ADJ)


class Generator(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())
    file: str = Field(default='')
    buffer: str = Field(default='')
    start: tuple[tuple[int, int], str] = Field(default=((0, 0), ''))
    goal: tuple[tuple[int, int], str] = Field(default=((0, 0), ''))
    nodes: dict[str, Node] = Field(default={})
    nb_drones: int = Field(default=0)

    def debug(self) -> None:
        print(f'\nFILENAME: {self.file}')
        print(f'START: {self.start}')
        print(f'GOAL: {self.goal}')
        print(f'NB_DRONES: {self.nb_drones}')
        print(f'NODES: {self.nodes}\n')

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
                elif (key in ('start_hub', 'end_hub', 'hub')):
                    coords: tuple[int, int] = (int(part[1]), int(part[2]))
                    if (len(part[3]) > 3):
                        color = part[3].split('=')[1].upper()
                    else:
                        color = 'NONE'
                    node: tuple[tuple[int, int], str] = (coords, color)
                    self.nodes[part[0]] = node
                    if (key == 'start_hub'):
                        self.start = node
                    elif (key == 'end_hub'):
                        self.goal = node
                    elif (key == 'connection'):
                        a, b = value.split('-')
                        self.nodes[a].connect(self.nodes[b])
                        self.nodes[b].connect(self.nodes[a])
            except IndexError:
                self.form.putstr(
                        self.form.colored('# INVALID PARAM', self.colors.RED),
                        stderr)
        self.debug()
