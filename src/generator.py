from src.colors import Colors, Format
from pydantic import BaseModel, Field
from typing import List, Self


class Node(BaseModel):
    NEXT: (Self | None) = Field(default=None)
    VALUE: tuple[tuple[int, int], str] = Field(default=((0, 0), ''))
    COLOR: str = Field(default='WHITE')


class Parsed(BaseModel):
    nb_drones: int = Field(default=0)
    start: tuple[tuple[int, int], str] = Field(default=((0, 0), ''))
    goal: tuple[tuple[int, int], str] = Field(default=((0, 0), ''))


class Generator(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())
    file: str = Field(default='')
    buffer: str = Field(default='')
    parsed: Parsed = Field(default=Parsed())
    waypoints: List[Node] = Field(default=[])

    def debug(self) -> None:
        print(f'\nFILENAME: {self.file}')
        print(f'PARSED: {self.parsed}')
        print(f'NB_DRONES: {self.parsed.nb_drones}\n')

    def receive(self, filename: str) -> None:
        with open(filename, 'r') as f:
            self.buffer = f.read()
            self.file = filename
        f.close()

    def parser(self) -> None:
        for line in self.buffer.split('\n'):
            line = line.strip()
            if (not line or line.startswith('#') or ': ' not in line):
                continue
            key, value = line.split(': ', 1)
            part: List[str] = value.split(' ')
            try:
                if (key == 'nb_drones'):
                    self.parsed.nb_drones = int(part[0])
                elif (key in ('start_hub', 'end_hub', 'hub')):
                    coords: tuple[int, int] = (int(part[1]), int(part[2]))
                    if (len(part[3]) > 3):
                        color = part[3].split('=')[1].upper()
                    else:
                        color = 'WHITE'
                    node: tuple[tuple[int, int], str] = (coords, color)
                    if (key == 'start_hub'):
                        self.parsed.start = node
                    if (key == 'end_hub'):
                        self.parsed.goal = node
            except IndexError:
                print(self.colors.RED)
                print(f'# INVALID PARAM: got {line}')
                print(self.colors.RESET)
                exit(1)
        self.debug()
