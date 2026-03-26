from src.colors import Colors, Format
from pydantic import BaseModel, Field
from typing import IO


class SimulationManager(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())

    def prompt(self, filename: str) -> str:
        print(self.colors.WHITE)
        print('#   What to do with ', end='')
        print(self.colors.CYAN, end='')
        print(f'{filename}?')

    def get_content(self, file: IO) -> str:
        temp: str = ''
        with open(file, 'r') as file:
            temp = file.read()
        return (temp)

