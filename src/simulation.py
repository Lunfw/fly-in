from src.colors import Colors, Format
from sys import stdin, stdout
from tty import setraw
from termios import tcgetattr, tcsetattr, TCSADRAIN
from pydantic import BaseModel, Field
from typing import IO, List


class SimulationManager(BaseModel):
    colors: Colors = Field(default=Colors())
    first_draw: bool = Field(default=True)
    form: Format = Field(default=Format())
    nav_lines: int = Field(default=0)

    def prompt(self, filename: str) -> str:
        options: List = [
                    'Open',
                    'Generate',
                    'Close',
                ]
        print(self.colors.WHITE)
        print('#   What to do with ', end='')
        print(self.colors.CYAN, end='')
        print(f'{filename}?')
        selected: int = 0
        self.prompt_options(options, selected)
        while (True):
            key : str = self.get_key()

            if (key == '\x1b[A'):
                if (selected == 0):
                    selected = 0
                else:
                    selected = selected - 1
            elif (key == '\x1b[B'):
                if (selected == len(options) - 1):
                    selected = len(options) - 1
                else:
                    selected = selected + 1
            elif (options[selected] == 'Close' and key == '\r'):
                break
            elif (key == '\x03'):
                exit(0)
            self.prompt_options(options, selected)

    def get_key(self) -> str:
        fd = stdin.fileno()
        old = tcgetattr(fd)
        try:
            setraw(fd)
            char = stdin.read(1)
            if (char == '\x1b'):
                char += stdin.read(2)
            return (char)
        finally:
            tcsetattr(fd, TCSADRAIN, old)

    def prompt_options(self, items, selected):
        if (self.first_draw):
            self.first_draw = False
        else:
            stdout.write(f'\x1b[{self.nav_lines}A')
            stdout.write(f'\x1b[J')
            stdout.flush()

        max_len: int = max(len(item) for item in items)
        temp: List[str] = []
        for i, item in enumerate(items):
            if (i == selected):
                marker = '#'
            else:
                marker = ' '
            padded: str = item.ljust(max_len)
            temp.append(f'[{marker}]    ->| {padded}')
        self.form.putstr(temp)

        self.nav_lines = len(temp)

    def get_content(self, file: IO) -> str:
        temp: str = ''
        with open(file, 'r') as file:
            temp = file.read()
        return (temp)
