from src.colors import Colors
from pydantic import BaseModel, Field
from shutil import get_terminal_size
from typing import List
from os import listdir
from sys import stderr


class Maps(BaseModel):
    def get_maps(self) -> None:
        try:
            for entity in listdir('maps'):
                yield entity
        except DirectoryNotFoundError:
            print('No maps found', file=stderr)
            exit(1)


class Menu(BaseModel):
    colors: Colors = Field(default=Colors())
    maps: Maps = Field(default=Maps())

    def centered(self, text: tuple):
        width = get_terminal_size().columns
        for line in text:
            print(line.center(width))

    def display(self) -> None:
        print(self.colors.CYAN)
        head: tuple = (
                    'Welcome!',
                    'This is a drone simulation program.',
                    self.colors.WHITE,
                    '',
                    'omg get_next_line reference!!',
                    self.colors.RESET
                )
        self.centered(head)
        body: tuple = tuple(maps for maps in self.maps.get_maps())
        self.centered(body)
