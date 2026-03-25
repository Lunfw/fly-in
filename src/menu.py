from src.colors import Colors, Format
from pydantic import BaseModel, Field
from os import listdir
from sys import stderr
from typing import Generator


class Maps(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())

    def get_maps(self) -> Generator:
        try:
            for entity in listdir('maps'):
                yield entity
        except FileNotFoundError:
            print(self.colors.RED)
            self.form.centered('No maps found.', stderr)
            print(self.colors.RESET)
            for files in listdir('.'):
                if ('maps' in files):
                    self.form.centered('Maybe if you unarchived this:')
                    self.form.centered(files)
                    break
            exit(1)


class Menu(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())
    maps: Maps = Field(default=Maps())

    def display(self) -> None:
        head: tuple = (
                    self.colors.CYAN,
                    'Welcome!',
                    'This is a drone simulation program.',
                    self.colors.WHITE,
                    'omg get_next_line reference!!',
                )
        self.form.centered(head)
        body: tuple = tuple(maps for maps in self.maps.get_maps())
