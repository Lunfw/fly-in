from src.colors import Colors, Format
from sys import stdin, stdout
from tty import setraw
from termios import tcgetattr, tcsetattr, TCSADRAIN
from pydantic import BaseModel, Field
from typing import IO, List


class SimulationDisplay(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())
    first_draw: bool = Field(default=True)
    nav_lines: int = Field(default=0)

    def prompt(self, filename: str) -> str:
        options: List = [
                    'Open',
                    'Generate',
                    'Close',
                ]
        selected: int = 0
        self.prompt_options(options, selected, filename)
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
            elif (options[selected] == 'Open' and key == '\r'):
                self.get_content(f'maps/{filename}')
            elif (options[selected] == 'Close' and key == '\r'):
                break
            elif (key == '\x03'):
                exit(0)
            self.prompt_options(options, selected, filename)

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

    def prompt_options(self, items, selected, filename: str) -> None:

        if (self.first_draw):
            self.first_draw = False
        else:
            stdout.write(f'\x1b[{self.nav_lines}A')
            stdout.write(f'\x1b[J')
            stdout.flush()

        print(self.colors.WHITE)
        print('#   What to do with ', end='')
        print(self.colors.CYAN, end='')
        print(f'{filename}?')
        print(self.colors.RESET)

        max_len: int = max(len(item) for item in items)
        temp: List[str] = []
        for i, item in enumerate(items):
            if (i == selected):
                marker = self.colors.GREEN + 'X' + self.colors.RESET
            else:
                marker = ' '
            padded: str = item.ljust(max_len)
            temp.append(f'[{marker}]    ->| {padded}')
        self.form.putstr(temp)

        self.nav_lines = len(temp) * 2

    def get_content(self, filename: str) -> None:
        with open(filename, 'r') as file:
            buffer: str = file.read()
        print('\n' + buffer)
        
