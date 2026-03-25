from src.colors import Colors
from pydantic import BaseModel, Field
from shutil import get_terminal_size
from typing import List


class Menu(BaseModel):
    colors: Colors = Field(default=Colors())

    def centered(self, text: tuple):
        width = get_terminal_size().columns
        for line in text:
            print(line.center(width))

    def display(self) -> None:
        print(self.colors.CYAN)
        head: tuple = (
                    "Welcome!",
                    "This is a drone simulation program.",
                    self.colors.WHITE,
                    '',
                    'omg get_next_line reference!!',
                )
        body: tuple = (
        self.centered(head)
