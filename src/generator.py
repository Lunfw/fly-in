from src.colors import Colors, Format
from pydantic import BaseModel, Field
from typing import Dict, List, Self


class Node(BaseModel):
    NEXT: Self = Field(default=None)
    VALUE: tuple[str] = Field(default=('', ''))
    COLOR: str = Field(default='WHITE')


class Parsed(BaseModel):
    nb_drones: int = Field(default=0)
    start: tuple[tuple[str, str], str] = Field(default=(('', ''), ''))
    goal: tuple[tuple[str, str], str] = Field(default=(('', ''), ''))


class Generator(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())
    file: str = Field(default='')
    buffer: str = Field(default='')
    parsed: Parsed = Field(default=Parsed())
    waypoints: List[Node] = Field(default=[])

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
            parts: List[str] = value.split(' ')
            try:
                if (key == 'nb_drones'):
                    self.parsed.nb_drones = int(parts[0])
                elif (key in ('start_hub', 'end_hub', 'hub')):
                    coords: tuple = (parts[1], parts[2])
                    if (len(parts[3]) > 3):
                        colors = parts[3]
                    else:
                        colors = 'WHITE'
                    node = ((parts[0], coords), colors)
            except IndexError:
                print(self.colors.RED)
                print(f'# INVALID PARAM: got {line}')
                print(self.colors.RESET)
                exit(1)
